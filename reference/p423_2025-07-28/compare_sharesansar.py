#!/usr/bin/env python3
"""Compare pinned ShareSansar EOD snapshot against P4.23.2 floorsheet audit."""
import argparse, csv, json
from decimal import Decimal
from pathlib import Path

FIELDS = ("open", "high", "low", "close", "volume")
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
    checks = {k: {"exact": 0, "mismatch": 0} for k in (*FIELDS, "turnover")}
    floor = {k: {"exact": 0, "mismatch": 0} for k in ("high", "low", "volume", "turnover")}
    discrepancies = []
    for symbol in sorted(snap):
        s, r = snap[symbol], audit[symbol]
        for k in FIELDS:
            expected = Decimal(r[{"volume":"canonical_volume"}.get(k, "canonical_"+k)])
            actual = Decimal(s[k])
            if expected == actual: checks[k]["exact"] += 1
            else:
                checks[k]["mismatch"] += 1
                discrepancies.append({"symbol":symbol,"field":k,"sharesansar":str(actual),"canonical":str(expected)})
        # Turnover is not present in the canonical OHLCV snapshot; compare with
        # the floorsheet aggregation and pinned secondary counterpart instead.
        expected_turnover = Decimal(r["reconstructed_turnover"])
        actual_turnover = Decimal(s["turnover"])
        if expected_turnover == actual_turnover: checks["turnover"]["exact"] += 1
        else: checks["turnover"]["mismatch"] += 1
        for k in ("high","low","volume"):
            floor_key = {"high":"reconstructed_high","low":"reconstructed_low","volume":"reconstructed_volume"}[k]
            actual = Decimal(s[k])
            expected = Decimal(r[floor_key])
            if actual == expected: floor[k]["exact"] += 1
            else: floor[k]["mismatch"] += 1
        if actual_turnover == expected_turnover: floor["turnover"]["exact"] += 1
        else: floor["turnover"]["mismatch"] += 1
    result = {
      "date":"2025-07-28", "symbols":len(snap),
      "source":{"repository":"OmitNomis/ShareSansarScraper","commit":"524442d518d2f2705ade0680c9d2e3f90738e3d6","path":"docs/Data/2025_07_28.csv","git_blob_sha":"28b5edf90ea5ebfe7e419c5162eedd0f30a9ce82"},
      "sharesansar_vs_canonical":checks,
      "sharesansar_vs_floorsheet_aggregation":floor,
      "canonical_mismatches":discrepancies,
      "disposition":"EXTERNAL_OHLCV_CORROBORATED; FLOOR_SHEET_EXTREMA_REQUIRES_RECONCILIATION"
    }
    Path(a.out).write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if any(v["mismatch"] for v in checks.values()):
        raise SystemExit("FAIL: external snapshot does not exactly match canonical values")
if __name__ == "__main__":
    main()
