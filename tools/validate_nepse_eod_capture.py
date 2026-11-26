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
from urllib.parse import urlparse

OFFICIAL_HOSTS = {"www.nepalstock.com", "nepalstock.com", "www.nepalstock.com.np", "nepalstock.com.np"}
REQUIRED = (
    "businessDate", "securityId", "symbol", "openPrice", "highPrice",
    "lowPrice", "closePrice", "totalTradedQuantity",
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


def _check_official_url(value):
    parsed = urlparse(value)
    if parsed.scheme != "https" or parsed.hostname not in OFFICIAL_HOSTS:
        raise EvidenceError("source_url must use HTTPS on an official NEPSE host")


def validate_capture(payload_bytes, expected_symbol, expected_date, source_url, retrieved_at, raw_payload_file):
    _check_official_url(source_url)
    captured_at = _retrieved_at(retrieved_at)
    try:
        payload = json.loads(payload_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceError(f"payload is not valid UTF-8 JSON: {exc}") from exc

    if not isinstance(payload, dict) or not isinstance(payload.get("content"), list):
        raise EvidenceError("expected NEPSE EOD response object with a content array")

    symbol = expected_symbol.strip().upper()
    expected_day = date.fromisoformat(expected_date)
    matches = [
        row for row in payload["content"]
        if isinstance(row, dict)
        and str(row.get("symbol", "")).strip().upper() == symbol
        and _date(row.get("businessDate")) == expected_day
    ]
    if len(matches) != 1:
        raise EvidenceError(f"expected exactly one {symbol} row for {expected_day}; found {len(matches)}")

    row = matches[0]
    missing = [field for field in REQUIRED if field not in row or row[field] is None]
    if missing:
        raise EvidenceError(f"official row missing required fields: {', '.join(missing)}")

    prices = {name: _decimal(row, field) for name, field in (
        ("open", "openPrice"), ("high", "highPrice"),
        ("low", "lowPrice"), ("close", "closePrice"),
    )}
    volume = _decimal(row, "totalTradedQuantity")
    turnover = _decimal(row, "totalTradedValue") if row.get("totalTradedValue") is not None else None
    trades = _decimal(row, "totalTrades") if row.get("totalTrades") is not None else None

    if any(value <= 0 for value in prices.values()):
        raise EvidenceError("OHLC prices must be positive")
    if volume < 0 or (turnover is not None and turnover < 0) or (trades is not None and trades < 0):
        raise EvidenceError("volume, turnover and trades cannot be negative")
    if volume != volume.to_integral_value() or (trades is not None and trades != trades.to_integral_value()):
        raise EvidenceError("volume and trade count must be whole numbers")
    if prices["high"] < prices["low"]:
        raise EvidenceError("highPrice is below lowPrice")

    flags = []
    if not (prices["low"] <= prices["open"] <= prices["high"]):
        flags.append("open_outside_range")
    if not (prices["low"] <= prices["close"] <= prices["high"]):
        flags.append("close_outside_range")
    if trades is not None and volume == 0 and trades > 0:
        flags.append("zero_volume_with_positive_trade_count")
    if trades is not None and volume > 0 and trades == 0:
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
        "raw_payload_file": str(raw_payload_file),
        "raw_payload_sha256": hashlib.sha256(payload_bytes).hexdigest(),
        "row": normalized,
        "parsed_ohlcv": {
            "open": str(prices["open"]), "high": str(prices["high"]),
            "low": str(prices["low"]), "close": str(prices["close"]),
            "volume": str(volume), "turnover": str(turnover) if turnover is not None else None,
            "trades": str(trades) if trades is not None else None,
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
