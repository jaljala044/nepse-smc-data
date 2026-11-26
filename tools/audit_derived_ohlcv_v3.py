#!/usr/bin/env python3
"""Audit derived OHLCV v3 against immutable v2, raw sources and official evidence."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path


def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def dec(value):
    try:
        return Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, TypeError):
        return None


def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def inspect(rows, symbol):
    flags = []
    for row in rows:
        values = {k: dec(row.get(k)) for k in ("Open", "High", "Low", "Close", "Volume")}
        o, h, l, c, v = (values[k] for k in ("Open", "High", "Low", "Close", "Volume"))
        if any(x is None for x in values.values()):
            flags.append((symbol, row.get("Date", ""), "NON_NUMERIC_OR_MISSING"))
            continue
        if min(o, h, l, c) <= 0:
            flags.append((symbol, row.get("Date", ""), "NONPOSITIVE_PRICE"))
        if h < l:
            flags.append((symbol, row.get("Date", ""), "HIGH_BELOW_LOW"))
        if o < l or o > h:
            flags.append((symbol, row.get("Date", ""), "OPEN_OUTSIDE_RANGE"))
        if c < l or c > h:
            flags.append((symbol, row.get("Date", ""), "CLOSE_OUTSIDE_RANGE"))
        if v < 0:
            flags.append((symbol, row.get("Date", ""), "NEGATIVE_VOLUME"))
    return flags


def audit(v2_dir, v3_dir, raw_dir, matrix_path, correction_path, output_dir,
          expected_symbols=281, expected_corrections=11):
    v2_dir, v3_dir, raw_dir, output_dir = map(Path, (v2_dir, v3_dir, raw_dir, output_dir))
    v2_manifest = read_csv(v2_dir / "manifest.csv")
    v3_manifest = read_csv(v3_dir / "manifest.csv")
    if len(v2_manifest) != expected_symbols or len(v3_manifest) != expected_symbols:
        raise ValueError("v2/v3 manifest coverage mismatch")
    if {r["symbol"] for r in v2_manifest} != {r["symbol"] for r in v3_manifest}:
        raise ValueError("v2/v3 symbol universe differs")

    matrix = read_csv(matrix_path)
    corrections = read_csv(correction_path)
    if len(matrix) != expected_corrections or len(corrections) != expected_corrections:
        raise ValueError("official matrix/correction row count mismatch")
    official = {(r["symbol"], r["business_date"]): r for r in matrix}
    correction_keys = {(r["symbol"], r["business_date"]) for r in corrections}
    if len(official) != expected_corrections or correction_keys != set(official):
        raise ValueError("official correction keys are duplicated or incomplete")
    for row in corrections:
        if row.get("field") != "Open" or row.get("disposition") != "PRIMARY_OFFICIAL_NEPSE_EOD_OPEN_CORRECTION":
            raise ValueError("unsupported correction in P4.30 ledger")

    v2_provenance = read_csv(v2_dir / "provenance_ledger.csv")
    v3_provenance = read_csv(v3_dir / "provenance_ledger.csv")
    if len(v3_provenance) != len(v2_provenance) + expected_corrections:
        raise ValueError("v3 provenance ledger did not preserve v2 rows and append all new evidence")
    added_provenance = [r for r in v3_provenance if r.get("action") == "OFFICIAL_OPEN_FIELD_CORRECTION"]
    if len(added_provenance) != expected_corrections:
        raise ValueError("v3 provenance ledger missing official Open evidence rows")
    for item in added_provenance:
        key = (item.get("symbol"), item.get("official_business_date"))
        if key not in official or item.get("official_payload_sha256") != official[key].get("official_payload_sha256"):
            raise ValueError(f"new v3 provenance does not match official matrix: {key}")
    v2_corrections = read_csv(v2_dir / "corrections.csv")
    v3_corrections = read_csv(v3_dir / "corrections.csv")
    if len(v3_corrections) != len(v2_corrections) + expected_corrections:
        raise ValueError("v3 correction ledger did not preserve v2 corrections and append all new Open corrections")
    v2_by_symbol = {r["symbol"]: r for r in v2_manifest}
    v3_by_symbol = {r["symbol"]: r for r in v3_manifest}
    raw_verified = v2_verified = v3_verified = total_rows = 0
    all_flags = []
    changed_rows = 0

    for symbol, v3base in v3_by_symbol.items():
        v2base = v2_by_symbol[symbol]
        raw_path = raw_dir / f"{symbol}_OHLCV.csv"
        v2_path = v2_dir / f"{symbol}_OHLCV.csv"
        v3_path = v3_dir / f"{symbol}_OHLCV.csv"
        if not all(p.is_file() for p in (raw_path, v2_path, v3_path)):
            raise ValueError(f"missing source/derived file for {symbol}")
        if blob(raw_path.read_bytes()) != v3base["raw_source_blob_sha"] or v3base["raw_source_blob_sha"] != v2base["raw_source_blob_sha"]:
            raise ValueError(f"raw source blob changed for {symbol}")
        if blob(v2_path.read_bytes()) != v3base["v2_source_blob_sha"] or v3base["v2_source_blob_sha"] != v2base["derived_blob_sha"]:
            raise ValueError(f"v2 source blob changed for {symbol}")
        if blob(v3_path.read_bytes()) != v3base["derived_blob_sha"]:
            raise ValueError(f"v3 derived blob mismatch for {symbol}")
        raw_verified += 1
        v2_verified += 1
        v3_verified += 1

        v2rows, v3rows = read_csv(v2_path), read_csv(v3_path)
        if len(v2rows) != len(v3rows) or len(v3rows) != int(v3base["rows"]):
            raise ValueError(f"row count mismatch for {symbol}")
        if len({r["Date"] for r in v2rows}) != len(v2rows) or len({r["Date"] for r in v3rows}) != len(v3rows):
            raise ValueError(f"duplicate dates for {symbol}")
        total_rows += len(v3rows)
        targets = {day: row for (sym, day), row in official.items() if sym == symbol}
        for old, new in zip(v2rows, v3rows):
            if old["Date"] != new["Date"]:
                raise ValueError(f"v2/v3 date changed for {symbol}")
            key = (symbol, old["Date"])
            if key in official:
                item = official[key]
                corr = next(r for r in corrections if (r["symbol"], r["business_date"]) == key)
                if dec(old["Open"]) != dec(corr["candidate_value"]) or dec(new["Open"]) != dec(item["official_open"]):
                    raise ValueError(f"official Open correction mismatch for {key}")
                if any(dec(old[k]) != dec(new[k]) for k in ("High", "Low", "Close", "Volume")):
                    raise ValueError(f"non-Open field changed for {key}")
                changed_rows += 1
            elif old != new:
                raise ValueError(f"unapproved v2-to-v3 change for {key}")
        all_flags.extend(inspect(v3rows, symbol))

    if min(raw_verified, v2_verified, v3_verified) != expected_symbols or changed_rows != expected_corrections:
        raise ValueError("incomplete raw/v2/v3 verification or official correction count")
    flag_counts = Counter(flag for _, _, flag in all_flags)
    if sum(flag_counts.values()) != 1368 or flag_counts.get("OPEN_OUTSIDE_RANGE", 0) != 1314:
        raise ValueError(f"unexpected remaining invariant flag counts: {dict(flag_counts)}")
    if any(day.startswith("2026-") for _, day, _ in all_flags):
        raise ValueError("recent 2026 invariant flags remain after official corrections")

    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "remaining_invariant_flags.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["symbol", "date", "flag"])
        writer.writerows(all_flags)
    totals = {
        "status": "V3_OFFICIAL_OPEN_CORRECTIONS_VERIFIED_WITH_HISTORICAL_FLAGS_RETAINED",
        "symbols": expected_symbols, "derived_rows": total_rows,
        "raw_files_verified": raw_verified, "v2_files_verified": v2_verified,
        "v3_files_verified": v3_verified, "official_open_corrections_verified": changed_rows,
        "remaining_ohlcv_invariant_flags": sum(flag_counts.values()),
        "remaining_flags_by_type": dict(flag_counts),
        "recent_2026_flags_remaining": 0,
        "unapproved_v2_to_v3_changes": 0,
    }
    (output_dir / "audit_totals.json").write_text(json.dumps(totals, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(totals, indent=2))
    return totals


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--v2-dir", type=Path, required=True)
    parser.add_argument("--v3-dir", type=Path, required=True)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--corrections", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    audit(args.v2_dir, args.v3_dir, args.raw_dir, args.matrix, args.corrections, args.output_dir)


if __name__ == "__main__":
    main()
