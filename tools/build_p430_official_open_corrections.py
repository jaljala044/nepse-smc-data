#!/usr/bin/env python3
"""Build a strict Open-only correction ledger from P4.30 official EOD evidence."""
import argparse
import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

FIELDS = [
    "symbol", "business_date", "field", "candidate_value", "official_value",
    "official_security_id", "official_quality_flags", "official_payload_sha256",
    "official_source_url", "official_retrieved_at", "disposition",
]


def dec(value):
    try:
        return Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, TypeError):
        return None


def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def build(matrix_path, output_path, expected_count=11):
    rows = read_csv(matrix_path)
    if expected_count is not None and len(rows) != expected_count:
        raise ValueError(f"expected {expected_count} rows, found {len(rows)}")
    keys = [(r.get("symbol"), r.get("business_date")) for r in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate symbol/business_date in official matrix")

    ledger = []
    for row in rows:
        symbol, day = row["symbol"], row["business_date"]
        if row.get("official_capture_status") != "OFFICIAL_CAPTURE_ACCEPTED":
            raise ValueError(f"official capture not accepted: {symbol} {day}")
        if row.get("official_row_count") != "1":
            raise ValueError(f"official row not unique: {symbol} {day}")
        if row.get("official_quality_flags", "").strip():
            raise ValueError(f"official quality flags block correction: {symbol} {day}")
        if not row.get("official_security_id") or row["official_security_id"] != row.get("mapping_security_id"):
            raise ValueError(f"security ID mismatch: {symbol} {day}")

        candidate = {k: dec(row.get(f"candidate_{k}")) for k in ("open", "high", "low", "close", "volume")}
        official = {k: dec(row.get(f"official_{k}")) for k in ("open", "high", "low", "close", "volume")}
        if any(v is None for v in (*candidate.values(), *official.values())):
            raise ValueError(f"missing/non-numeric OHLCV: {symbol} {day}")
        if not (candidate["open"] > candidate["high"] or candidate["open"] < candidate["low"]):
            raise ValueError(f"candidate Open is not outside its range: {symbol} {day}")
        if official["open"] < official["low"] or official["open"] > official["high"]:
            raise ValueError(f"official Open remains outside range: {symbol} {day}")
        if candidate["open"] == official["open"]:
            raise ValueError(f"no Open correction required: {symbol} {day}")
        for field in ("high", "low", "close", "volume"):
            if candidate[field] != official[field]:
                raise ValueError(f"unexpected non-Open change ({field}): {symbol} {day}")

        ledger.append({
            "symbol": symbol, "business_date": day, "field": "Open",
            "candidate_value": row["candidate_open"], "official_value": row["official_open"],
            "official_security_id": row["official_security_id"],
            "official_quality_flags": row.get("official_quality_flags", ""),
            "official_payload_sha256": row["official_payload_sha256"],
            "official_source_url": row["official_source_url"],
            "official_retrieved_at": row["official_retrieved_at"],
            "disposition": "PRIMARY_OFFICIAL_NEPSE_EOD_OPEN_CORRECTION",
        })

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(ledger)
    return ledger


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-count", type=int, default=11)
    args = parser.parse_args()
    rows = build(args.matrix, args.output, expected_count=args.expected_count)
    print({"official_open_corrections": len(rows), "symbols": len({r["symbol"] for r in rows})})


if __name__ == "__main__":
    main()
