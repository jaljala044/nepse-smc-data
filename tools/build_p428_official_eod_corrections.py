#!/usr/bin/env python3
"""Create a primary-source correction ledger from the P4.28 official EOD matrix."""
import argparse
import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

FIELDS = [
    "symbol", "business_date", "candidate_status", "changed_fields",
    "candidate_open", "candidate_high", "candidate_low", "candidate_close",
    "candidate_volume", "candidate_turnover", "official_security_id",
    "official_open", "official_high", "official_low", "official_close",
    "official_volume", "official_turnover", "official_trades",
    "official_capture_status", "official_payload_sha256",
    "official_source_url", "official_retrieved_at",
    "disposition",
]


def dec(value):
    try:
        return Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, TypeError):
        return None


def build(matrix_path, output_path, expected_count=112):
    with matrix_path.open(newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    corrections = []
    for row in rows:
        if row.get("official_ohlcv_match") != "FALSE":
            continue
        if row.get("official_capture_status") != "OFFICIAL_CAPTURE_ACCEPTED":
            raise ValueError(f"non-accepted official row cannot enter correction ledger: {row.get('symbol')}")
        if row.get("official_quality_flags", "").strip():
            raise ValueError(f"official quality flags block correction: {row.get('symbol')}")
        if not row.get("official_security_id") or row["official_security_id"] != row.get("mapping_security_id"):
            raise ValueError(f"security-ID mismatch blocks correction: {row.get('symbol')}")

        changed = []
        for field in ("open", "high", "low", "close", "volume", "turnover"):
            if dec(row.get(f"candidate_{field}")) != dec(row.get(f"official_{field}")):
                changed.append(field)
        if not changed:
            raise ValueError(f"row marked mismatch but no numeric fields differ: {row.get('symbol')}")
        if not set(changed).issubset({"open", "close"}):
            raise ValueError(f"unexpected changed fields for {row.get('symbol')}: {changed}")

        o, h, l, c = (dec(row.get(f"official_{field}")) for field in ("open", "high", "low", "close"))
        volume = dec(row.get("official_volume"))
        if None in (o, h, l, c, volume) or min(o, h, l, c) <= 0 or h < max(o, l, c) or l > min(o, h, c) or volume < 0:
            raise ValueError(f"official row failed OHLCV invariant: {row.get('symbol')}")

        corrections.append({
            "symbol": row["symbol"], "business_date": row["business_date"],
            "candidate_status": row["candidate_status"],
            "changed_fields": ";".join(changed),
            "candidate_open": row["candidate_open"], "candidate_high": row["candidate_high"],
            "candidate_low": row["candidate_low"], "candidate_close": row["candidate_close"],
            "candidate_volume": row["candidate_volume"], "candidate_turnover": row["candidate_turnover"],
            "official_security_id": row["official_security_id"],
            "official_open": row["official_open"], "official_high": row["official_high"],
            "official_low": row["official_low"], "official_close": row["official_close"],
            "official_volume": row["official_volume"], "official_turnover": row["official_turnover"],
            "official_trades": row["official_trades"],
            "official_capture_status": row["official_capture_status"],
            "official_payload_sha256": row["official_payload_sha256"],
            "official_source_url": row["official_source_url"],
            "official_retrieved_at": row["official_retrieved_at"],
            "disposition": "PRIMARY_OFFICIAL_NEPSE_EOD_CORRECTION",
        })

    if expected_count is not None and len(corrections) != expected_count:
        raise ValueError(f"expected {expected_count} official corrections, found {len(corrections)}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(corrections)
    return corrections


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = build(args.matrix, args.output)
    by_status = {}
    by_fields = {}
    for row in rows:
        by_status[row["candidate_status"]] = by_status.get(row["candidate_status"], 0) + 1
        by_fields[row["changed_fields"]] = by_fields.get(row["changed_fields"], 0) + 1
    print({"corrections": len(rows), "by_candidate_status": by_status, "changed_fields": by_fields})
    if len(rows) != 112:
        raise SystemExit("expected 112 primary-source corrections")


if __name__ == "__main__":
    main()
