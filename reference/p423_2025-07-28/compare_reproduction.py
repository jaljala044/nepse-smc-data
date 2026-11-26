#!/usr/bin/env python3
"""Compare deterministic reconstruction against the submitted 86-symbol audit."""
import argparse, csv, json, sys
from decimal import Decimal

def norm(value):
    if value is None or value == "":
        return "UNKNOWN"
    try:
        return format(Decimal(str(value)).normalize(), "f")
    except Exception:
        return str(value)

def fail(message):
    print(f"REPRODUCTION MISMATCH: {message}", file=sys.stderr)
    raise SystemExit(1)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--submitted-csv", required=True)
    p.add_argument("--submitted-json", required=True)
    p.add_argument("--recomputed-json", required=True)
    a = p.parse_args()

    with open(a.submitted_csv, newline="", encoding="utf-8") as f:
        csv_rows = {r["symbol"]: r for r in csv.DictReader(f)}
    submitted = json.load(open(a.submitted_json, encoding="utf-8"))
    recomputed = json.load(open(a.recomputed_json, encoding="utf-8"))

    submitted_json_rows = {r["symbol"]: r for r in submitted["symbols"]}
    recomputed_rows = {r["symbol"]: r for r in recomputed["symbols"]}
    expected = set(csv_rows)
    if len(expected) != 86 or len(submitted_json_rows) != 86 or len(recomputed_rows) != 86:
        fail("expected exactly 86 unique symbols in each output")
    if expected != set(submitted_json_rows) or expected != set(recomputed_rows):
        fail("symbol coverage differs between submitted and recomputed outputs")

    numeric_fields = {
        "trade_count": "trade_count",
        "reconstructed_open": ("reconstructed", "open"),
        "reconstructed_high": ("reconstructed", "high"),
        "reconstructed_low": ("reconstructed", "low"),
        "reconstructed_close": ("reconstructed", "close"),
        "reconstructed_volume": ("reconstructed", "volume"),
        "reconstructed_turnover": ("reconstructed", "turnover"),
    }
    for symbol in sorted(expected):
        old_csv = csv_rows[symbol]
        old_json = submitted_json_rows[symbol]
        new = recomputed_rows[symbol]
        for field, path in numeric_fields.items():
            if isinstance(path, tuple):
                value = new[path[0]][path[1]]
            else:
                value = new[path]
            if norm(old_csv[field]) != norm(value):
                fail(f"{symbol} {field}: submitted CSV={old_csv[field]} recomputed={value}")
        for field in ("open", "high", "low", "close", "volume"):
            if norm(old_csv["canonical_" + field]) != norm(new["canonical"][field]):
                fail(f"{symbol} canonical {field} differs")
        for field in ("open", "high", "low", "close", "volume", "turnover"):
            if norm(old_csv["external_" + field]) != norm(new["external"][field]):
                fail(f"{symbol} external {field} differs")
        for field, value in new["comparison"].items():
            if old_csv[field] != value:
                fail(f"{symbol} {field}: submitted CSV={old_csv[field]} recomputed={value}")
        if old_csv["disposition"] != new["disposition"]:
            fail(f"{symbol} disposition differs")
        # Ensure the submitted JSON's per-symbol record independently agrees.
        for section in ("reconstructed", "canonical", "external", "comparison"):
            for key, value in new[section].items():
                if norm(old_json[section][key]) != norm(value):
                    fail(f"{symbol} submitted JSON {section}.{key} differs")
        if old_json["disposition"] != new["disposition"]:
            fail(f"{symbol} submitted JSON disposition differs")

    audit = recomputed["audit"]
    if audit["rows_seen"] != 170726:
        fail("archive row count changed")
    if audit["quantity_sum"] != "44124924":
        fail("archive quantity control total changed")
    if norm(audit["turnover_sum"]) != norm("19360873034.29"):
        fail("archive turnover control total changed")
    if audit["malformed_rows"] or audit["invalid_rows"] or audit["bad_date_rows"]:
        fail("archive contains malformed, invalid, or bad-date rows")
    if audit["duplicate_contract_ids"] or audit["duplicate_rows"] or audit["null_field_values"]:
        fail("archive contains duplicate or null rows")
    if any(r["reconstructed"]["open"] != "UNKNOWN" or r["reconstructed"]["close"] != "UNKNOWN"
           for r in recomputed["symbols"]):
        fail("open/close must remain UNKNOWN because archive timestamps are blank")
    print("PASS: 86/86 symbols, all submitted OHLCV/comparison fields, JSON records, and archive controls reproduce")
    
if __name__ == "__main__":
    main()
