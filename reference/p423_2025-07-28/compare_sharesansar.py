#!/usr/bin/env python3
"""Compare pinned ShareSansar EOD snapshot against P4.23.2 floorsheet audit."""
import argparse
import csv
import json
from decimal import Decimal
from pathlib import Path

CANONICAL = {
    "open": "canonical_open",
    "high": "canonical_high",
    "low": "canonical_low",
    "close": "canonical_close",
    "volume": "canonical_volume",
}
FLOORSHEET = {
    "high": "reconstructed_high",
    "low": "reconstructed_low",
    "volume": "reconstructed_volume",
    "turnover": "reconstructed_turnover",
}

def read(path):
    with Path(path).open(newline="", encoding="utf-8") as f:
        return {r["symbol"]: r for r in csv.DictReader(f)}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--snapshot", required=True)
    p.add_argument("--results", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    snap, audit = read(a.snapshot), read(a.results)
    if len(snap) != 86 or len(audit) != 86 or set(snap) != set(audit):
        raise SystemExit("FAIL: expected identical 86-symbol universes")

    canonical = {k: {"exact": 0, "mismatch": 0} for k in CANONICAL}
    floor = {k: {"exact": 0, "mismatch": 0} for k in FLOORSHEET}
    discrepancies = []
    for symbol in sorted(snap):
        s, r = snap[symbol], audit[symbol]
        for field, canonical_field in CANONICAL.items():
            actual, expected = Decimal(s[field]), Decimal(r[canonical_field])
            if actual == expected:
                canonical[field]["exact"] += 1
            else:
                canonical[field]["mismatch"] += 1
                discrepancies.append({"symbol": symbol, "comparison": "canonical",
                    "field": field, "sharesansar": str(actual), "canonical": str(expected)})
        for field, floor_field in FLOORSHEET.items():
            actual, expected = Decimal(s[field]), Decimal(r[floor_field])
            if actual == expected:
                floor[field]["exact"] += 1
            else:
                floor[field]["mismatch"] += 1
                discrepancies.append({"symbol": symbol, "comparison": "floorsheet",
                    "field": field, "sharesansar": str(actual), "floorsheet": str(expected)})

    result = {
        "date": "2025-07-28",
        "symbols": len(snap),
        "source": {
            "repository": "OmitNomis/ShareSansarScraper",
            "commit": "524442d518d2f2705ade0680c9d2e3f90738e3d6",
            "path": "docs/Data/2025_07_28.csv",
            "git_blob_sha": "28b5edf90ea5ebfe7e419c5162eedd0f30a9ce82",
        },
        "sharesansar_vs_canonical": canonical,
        "sharesansar_vs_floorsheet_aggregation": floor,
        "discrepancies": discrepancies,
        "disposition": (
            "EXTERNAL_OHLCV_CORROBORATED" if all(v["mismatch"] == 0 for v in canonical.values())
            else "CANONICAL_MISMATCH_REQUIRES_INVESTIGATION"
        ),
    }
    Path(a.out).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if any(v["mismatch"] for v in canonical.values()):
        raise SystemExit("FAIL: external snapshot does not exactly match canonical values")

if __name__ == "__main__":
    main()
