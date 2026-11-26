#!/usr/bin/env python3
"""Validate P4.28 candidates against complete official NEPSE EOD board captures."""
import argparse
import csv
import hashlib
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from validate_nepse_eod_capture import EvidenceError, validate_capture

FIELDS = [
    "symbol", "business_date", "candidate_status",
    "candidate_open", "candidate_high", "candidate_low", "candidate_close",
    "candidate_volume", "candidate_turnover",
    "mapping_security_id", "mapping_active_status", "mapping_snapshot_date",
    "official_row_count", "official_security_id", "official_open",
    "official_high", "official_low", "official_close", "official_volume",
    "official_turnover", "official_trades", "official_capture_status",
    "official_quality_flags", "official_ohlcv_match", "official_volume_match",
    "official_turnover_match", "official_payload_sha256", "official_source_url",
    "official_retrieved_at", "disposition",
]


def dec(value):
    if value is None or str(value).strip() == "":
        return None
    try:
        return Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, TypeError):
        return None


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def load_mapping(path):
    rows = read_csv(path)
    mapping = {}
    ids = {}
    for row in rows:
        symbol = row.get("symbol", "").strip().upper()
        security_id = row.get("security_id", "").strip()
        if not symbol or not security_id:
            continue
        if symbol in mapping:
            raise ValueError(f"duplicate symbol in security-ID snapshot: {symbol}")
        if security_id in ids:
            raise ValueError(f"duplicate security ID {security_id}: {ids[security_id]} and {symbol}")
        mapping[symbol] = row
        ids[security_id] = symbol
    return mapping


def load_board(capture_dir, business_date):
    manifest_path = capture_dir / business_date / "capture_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "COMPLETE_BOARD_CAPTURE":
        raise ValueError(f"incomplete official board capture for {business_date}")
    pages = manifest.get("captured_pages", [])
    if len(pages) != int(manifest.get("total_pages", -1)):
        raise ValueError(f"page count mismatch for {business_date}")
    if sum(int(p.get("rows", 0)) for p in pages) != int(manifest.get("total_elements", -1)):
        raise ValueError(f"totalElements mismatch for {business_date}")

    by_symbol = {}
    for page in pages:
        payload_path = Path(page["file"])
        raw = payload_path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != page.get("sha256"):
            raise ValueError(f"payload SHA-256 mismatch: {payload_path}")
        payload = json.loads(raw.decode("utf-8"))
        if len(payload.get("content", [])) != int(page["rows"]):
            raise ValueError(f"page row count mismatch: {payload_path}")
        for row in payload["content"]:
            if not isinstance(row, dict):
                continue
            symbol = str(row.get("symbol", "")).strip().upper()
            day = str(row.get("businessDate", ""))[:10]
            if day != business_date or not symbol:
                continue
            by_symbol.setdefault(symbol, []).append({
                "page": page, "payload_path": payload_path, "raw": raw,
                "row": row,
            })
    return manifest, by_symbol


def build(queue_path, mapping_path, capture_dir, output_path, expected_count=599):
    candidates = read_csv(queue_path)
    if expected_count is not None and len(candidates) != expected_count:
        raise ValueError(f"expected {expected_count} P4.22 candidates, found {len(candidates)}")
    mapping = load_mapping(mapping_path)
    symbols = {r["symbol"].strip().upper() for r in candidates}
    missing_mapping = sorted(symbols - set(mapping))
    if missing_mapping:
        raise ValueError(f"missing current security-ID mapping for: {missing_mapping}")

    board_cache = {}
    results = []
    for item in candidates:
        symbol = item["symbol"].strip().upper()
        day = item["date"].strip()
        if day not in board_cache:
            board_cache[day] = load_board(capture_dir, day)
        manifest, by_symbol = board_cache[day]
        matches = by_symbol.get(symbol, [])
        map_row = mapping[symbol]
        official = None
        capture_status = "NO_OFFICIAL_ROW"
        quality_flags = []
        official_id = ""
        official_values = {}
        payload_sha = source_url = retrieved_at = ""

        if len(matches) > 1:
            capture_status = "DUPLICATE_OFFICIAL_ROWS"
        elif len(matches) == 1:
            hit = matches[0]
            page = hit["page"]
            payload_sha = page["sha256"]
            source_url = page["url"]
            retrieved_at = page["retrieved_at"]
            try:
                evidence = validate_capture(
                    hit["raw"], symbol, day, source_url, retrieved_at,
                    hit["payload_path"],
                )
                official = evidence["row"]
                capture_status = evidence["status"]
                quality_flags = evidence["quality_flags"]
                official_values = evidence["parsed_ohlcv"]
                official_id = str(official.get("securityId", ""))
            except EvidenceError as exc:
                capture_status = "OFFICIAL_ROW_VALIDATION_FAILED"
                quality_flags = [str(exc)]
                official = hit["row"]
                official_id = str(official.get("securityId", ""))

        candidate_values = {
            "open": dec(item.get("open")), "high": dec(item.get("high")),
            "low": dec(item.get("low")), "close": dec(item.get("close")),
            "volume": dec(item.get("volume")), "turnover": dec(item.get("turnover")),
        }
        official_tuple = tuple(dec(official_values.get(k)) for k in ("open", "high", "low", "close", "volume"))
        candidate_tuple = tuple(candidate_values[k] for k in ("open", "high", "low", "close", "volume"))
        tuple_match = official is not None and capture_status == "OFFICIAL_CAPTURE_ACCEPTED" and official_tuple == candidate_tuple
        volume_match = official is not None and capture_status == "OFFICIAL_CAPTURE_ACCEPTED" and official_tuple[4] == candidate_values["volume"]
        turnover_match = (
            official is not None and capture_status == "OFFICIAL_CAPTURE_ACCEPTED"
            and dec(official_values.get("turnover")) == candidate_values["turnover"]
        )
        id_match = bool(official_id) and official_id == map_row["security_id"]

        if capture_status == "OFFICIAL_CAPTURE_ACCEPTED" and id_match:
            disposition = "OFFICIAL_ROW_MATCHES_CANDIDATE" if tuple_match else "OFFICIAL_ROW_DIFFERS_CANDIDATE"
        elif capture_status == "OFFICIAL_CAPTURE_ACCEPTED" and not id_match:
            disposition = "UNKNOWN_SECURITY_ID_MISMATCH"
        elif capture_status == "NO_OFFICIAL_ROW":
            disposition = "UNKNOWN_NO_OFFICIAL_ROW"
        elif capture_status == "DUPLICATE_OFFICIAL_ROWS":
            disposition = "UNKNOWN_DUPLICATE_OFFICIAL_ROWS"
        else:
            disposition = "OFFICIAL_CAPTURE_REVIEW_REQUIRED"

        results.append({
            "symbol": symbol, "business_date": day, "candidate_status": item["status"],
            "candidate_open": item["open"], "candidate_high": item["high"],
            "candidate_low": item["low"], "candidate_close": item["close"],
            "candidate_volume": item["volume"], "candidate_turnover": item["turnover"],
            "mapping_security_id": map_row["security_id"],
            "mapping_active_status": map_row.get("active_status", ""),
            "mapping_snapshot_date": map_row.get("snapshot_date", ""),
            "official_row_count": len(matches), "official_security_id": official_id,
            "official_open": official_values.get("open", ""),
            "official_high": official_values.get("high", ""),
            "official_low": official_values.get("low", ""),
            "official_close": official_values.get("close", ""),
            "official_volume": official_values.get("volume", ""),
            "official_turnover": official_values.get("turnover", ""),
            "official_trades": official.get("totalTrades", "") if official else "",
            "official_capture_status": capture_status,
            "official_quality_flags": ";".join(quality_flags),
            "official_ohlcv_match": str(tuple_match).upper(),
            "official_volume_match": str(volume_match).upper(),
            "official_turnover_match": str(turnover_match).upper(),
            "official_payload_sha256": payload_sha, "official_source_url": source_url,
            "official_retrieved_at": retrieved_at, "disposition": disposition,
        })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(results)
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--capture-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = build(args.queue, args.mapping, args.capture_dir, args.output)
    counts = {}
    for row in rows:
        counts[row["disposition"]] = counts.get(row["disposition"], 0) + 1
    print(json.dumps({"rows": len(rows), "dispositions": counts, "output": str(args.output)}, indent=2))
    if len(rows) != 599:
        raise SystemExit("not all 599 candidate rows were audited")


if __name__ == "__main__":
    main()
