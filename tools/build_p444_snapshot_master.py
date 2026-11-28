#!/usr/bin/env python3
"""Normalize the pinned NEPSE current security snapshot without inventing history."""
from __future__ import annotations
import argparse, csv
from pathlib import Path

FIELDS = [
    "security_id", "symbol", "security_name", "active_status", "snapshot_date",
    "instrument_type", "effective_from", "effective_to", "source_url",
    "retrieved_at_utc", "source_git_blob_sha", "authorization_status",
    "evidence_tier", "identity_scope", "canonical_promotion_allowed",
]
REQUIRED = {"security_id", "symbol", "security_name", "active_status", "snapshot_date", "source_blob_sha"}

def normalize(source: Path, destination: Path) -> int:
    with source.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"missing columns: {sorted(missing)}")
        rows = list(reader)
    seen_ids, seen_symbols = set(), set()
    output = []
    for row in rows:
        security_id, symbol = row["security_id"].strip(), row["symbol"].strip().upper()
        if not security_id or not symbol:
            raise ValueError("blank stable ID or symbol in source snapshot")
        if security_id in seen_ids or symbol in seen_symbols:
            raise ValueError(f"duplicate ID or symbol in current snapshot: {security_id}/{symbol}")
        seen_ids.add(security_id); seen_symbols.add(symbol)
        if len(row["source_blob_sha"].strip()) != 40:
            raise ValueError(f"invalid source Git blob SHA for {symbol}")
        output.append({
            **{k: row.get(k, "") for k in ("security_id","symbol","security_name","active_status","snapshot_date")},
            "instrument_type": "UNKNOWN", "effective_from": "", "effective_to": "",
            "source_url": "https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_security_id_snapshot_2026-11-25.csv",
            "retrieved_at_utc": "", "source_git_blob_sha": row["source_blob_sha"].strip(),
            "authorization_status": "not_assessed", "evidence_tier": "current_snapshot_only",
            "identity_scope": "snapshot_only", "canonical_promotion_allowed": "false",
        })
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader(); writer.writerows(output)
    return len(output)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True); parser.add_argument("--output", required=True)
    args=parser.parse_args()
    print({"records": normalize(Path(args.input), Path(args.output)), "canonical_promotion_allowed": False})

if __name__ == "__main__": main()
