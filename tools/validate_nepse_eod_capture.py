#!/usr/bin/env python3
"""Validate a captured NEPSE official EOD response without mutating raw archives.

This is an evidence gate, not a network scraper. The caller must preserve the
original response bytes and provide the official endpoint URL and retrieval
timestamp. Only an exact symbol/date row can pass.
"""
import argparse
import hashlib
import json
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import parse_qs, urlparse

OFFICIAL_HOSTS = {"www.nepalstock.com", "nepalstock.com", "www.nepalstock.com.np", "nepalstock.com.np"}
REQUIRED = (
    "businessDate", "securityId", "symbol", "openPrice", "highPrice",
    "lowPrice", "closePrice", "totalTradedQuantity", "totalTradedValue",
    "totalTrades",
)


class EvidenceError(ValueError):
    """The capture cannot support an official-source claim."""


def _decimal(row, field):
    value = row.get(field)
    if value is None or str(value).strip() == "":
        raise EvidenceError(f"missing required numeric field: {field}")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise EvidenceError(f"invalid numeric field {field}: {value!r}") from exc
    if not result.is_finite():
        raise EvidenceError(f"non-finite numeric field: {field}")
    return result


def _date(value):
    try:
        return date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError) as exc:
        raise EvidenceError(f"invalid businessDate: {value!r}") from exc


def _retrieved_at(value):
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise EvidenceError("retrieved_at must be an ISO-8601 timestamp") from exc
    if result.tzinfo is None or result.utcoffset() is None:
        raise EvidenceError("retrieved_at must include a timezone offset")
    return result


def _check_official_url(value, expected_date):
    parsed = urlparse(value)
    if parsed.scheme != "https" or parsed.hostname not in OFFICIAL_HOSTS:
        raise EvidenceError("source_url must use HTTPS on an official NEPSE host")
    if parsed.path.rstrip("/") != "/api/nots/nepse-data/today-price":
        raise EvidenceError("source_url path must be the official NEPSE today-price EOD endpoint")
    query = parse_qs(parsed.query)
    if query.get("businessDate") != [expected_date.isoformat()]:
        raise EvidenceError("source_url businessDate must exactly match the expected exchange date")


def validate_capture(payload_bytes, expected_symbol, expected_date, source_url, retrieved_at, raw_payload_file):
    expected_day = date.fromisoformat(expected_date)
    _check_official_url(source_url, expected_day)
    captured_at = _retrieved_at(retrieved_at)
    try:
        payload = json.loads(payload_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceError(f"payload is not valid UTF-8 JSON: {exc}") from exc

    if not isinstance(payload, dict) or not isinstance(payload.get("content"), list):
        raise EvidenceError("expected NEPSE EOD response object with a content array")

    try:
        total_elements = int(payload["totalElements"])
        total_pages = int(payload["totalPages"])
    except (KeyError, TypeError, ValueError) as exc:
        raise EvidenceError("official EOD response must include integer totalElements and totalPages metadata") from exc
    if total_elements < len(payload["content"]) or total_pages < 1:
        raise EvidenceError("invalid EOD pagination metadata")
    if total_elements < 1:
        raise EvidenceError("official EOD response contains no records")

    symbol = expected_symbol.strip().upper()
    matches = [
        row for row in payload["content"]
        if isinstance(row, dict)
        and str(row.get("symbol", "")).strip().upper() == symbol
        and _date(row.get("businessDate")) == expected_day
    ]
    if len(matches) != 1:
        raise EvidenceError(f"expected exactly one {symbol} row for {expected_day}; found {len(matches)}")

    row = matches[0]
    try:
        security_id = int(row["securityId"])
    except (KeyError, TypeError, ValueError) as exc:
        raise EvidenceError("securityId must be a positive integer") from exc
    if security_id <= 0:
        raise EvidenceError("securityId must be a positive integer")

    missing = [field for field in REQUIRED if field not in row or row[field] is None]
    if missing:
        raise EvidenceError(f"official row missing required fields: {', '.join(missing)}")

    prices = {name: _decimal(row, field) for name, field in (
        ("open", "openPrice"), ("high", "highPrice"),
        ("low", "lowPrice"), ("close", "closePrice"),
    )}
    volume = _decimal(row, "totalTradedQuantity")
    turnover = _decimal(row, "totalTradedValue")
    trades = _decimal(row, "totalTrades")

    if any(value <= 0 for value in prices.values()):
        raise EvidenceError("OHLC prices must be positive")
    if volume < 0 or turnover < 0 or trades < 0:
        raise EvidenceError("volume, turnover and trades cannot be negative")
    if volume != volume.to_integral_value() or trades != trades.to_integral_value():
        raise EvidenceError("volume and trade count must be whole numbers")
    if prices["high"] < prices["low"]:
        raise EvidenceError("highPrice is below lowPrice")

    flags = []
    if not (prices["low"] <= prices["open"] <= prices["high"]):
        flags.append("open_outside_range")
    if not (prices["low"] <= prices["close"] <= prices["high"]):
        flags.append("close_outside_range")
    if volume == 0 and trades > 0:
        flags.append("zero_volume_with_positive_trade_count")
    if volume > 0 and trades == 0:
        flags.append("positive_volume_with_zero_trade_count")

    # Keep the wire row intact. Decimal strings make the output lossless and JSON-safe.
    normalized = dict(row)
    evidence = {
        "status": "OFFICIAL_CAPTURE_ACCEPTED" if not flags else "OFFICIAL_CAPTURE_REVIEW_REQUIRED",
        "evidence_tier": "OFFICIAL_NEPSE_EOD_CAPTURE",
        "symbol": symbol,
        "business_date": expected_day.isoformat(),
        "source_url": source_url,
        "retrieved_at": captured_at.isoformat(),
        "response_metadata": {
            "total_elements": total_elements,
            "total_pages": total_pages,
            "page": payload.get("number"),
            "page_size": payload.get("size"),
        },
        "raw_payload_file": str(raw_payload_file),
        "raw_payload_sha256": hashlib.sha256(payload_bytes).hexdigest(),
        "row": normalized,
        "parsed_ohlcv": {
            "open": str(prices["open"]), "high": str(prices["high"]),
            "low": str(prices["low"]), "close": str(prices["close"]),
            "volume": str(volume), "turnover": str(turnover), "trades": str(trades),
        },
        "quality_flags": flags,
        "raw_archive_mutated": False,
    }
    return evidence


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--payload", type=Path, required=True, help="Unmodified captured NEPSE EOD JSON response")
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--date", required=True, help="Expected exchange-local YYYY-MM-DD")
    parser.add_argument("--source-url", required=True, help="Exact official NEPSE endpoint URL")
    parser.add_argument("--retrieved-at", required=True, help="Timezone-aware ISO-8601 retrieval timestamp")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    payload_bytes = args.payload.read_bytes()
    evidence = validate_capture(
        payload_bytes, args.symbol, args.date, args.source_url,
        args.retrieved_at, args.payload,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": evidence["status"],
        "symbol": evidence["symbol"],
        "business_date": evidence["business_date"],
        "raw_payload_sha256": evidence["raw_payload_sha256"],
        "quality_flags": evidence["quality_flags"],
        "raw_archive_mutated": False,
    }, indent=2))
    if evidence["quality_flags"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
