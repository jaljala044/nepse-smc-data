#!/usr/bin/env python3
"""Build a deterministic row-level matrix for the 2025-07-28 archive conflicts.

This is an audit/export tool only. It never changes raw OHLCV files and never
promotes secondary archive values to canonical prices.
"""
import argparse
import csv
import hashlib
from decimal import Decimal, InvalidOperation
from pathlib import Path

OUTPUT_FIELDS = [
    "date", "symbol",
    "smc_open", "smc_high", "smc_low", "smc_close", "smc_volume",
    "external_open", "external_high", "external_low", "external_close",
    "external_volume", "external_turnover",
    "close_delta_external_minus_smc", "volume_delta_external_minus_smc",
    "ohlcv_equal", "raw_file_sha256", "external_archive_sha256",
    "external_source_repo", "external_source_commit", "external_source_path",
    "primary_source_window", "canonical_disposition", "evidence_note",
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decimal_or_none(value):
    if value is None or str(value).strip() == "":
        return None
    try:
        return Decimal(str(value))
    except InvalidOperation:
        return None


def build_matrix(external_csv: Path, raw_dir: Path, output_csv: Path):
    external_bytes = external_csv.read_bytes()
    external_hash = sha256(external_bytes)
    results = []

    with external_csv.open(newline="", encoding="utf-8-sig") as fh:
        for ext in csv.DictReader(fh):
            day = ext["date"].strip()
            symbol = ext["symbol"].strip().upper()
            raw_path = raw_dir / f"{symbol}_OHLCV.csv"
            base = {
                "date": day,
                "symbol": symbol,
                "external_open": ext.get("external_open", ""),
                "external_high": ext.get("external_high", ""),
                "external_low": ext.get("external_low", ""),
                "external_close": ext.get("external_close", ""),
                "external_volume": ext.get("external_volume", ""),
                "external_turnover": ext.get("external_turnover", ""),
                "external_archive_sha256": external_hash,
                "external_source_repo": ext.get("source_repository", ""),
                "external_source_commit": ext.get("source_commit", ""),
                "external_source_path": ext.get("source_path", ""),
                "primary_source_window": "OUTSIDE_OFFICIAL_365D_HISTORY_WINDOW",
                "canonical_disposition": "UNKNOWN_SOURCE_CONFLICT",
                "evidence_note": "Pinned secondary archive counterpart only; official NEPSE rolling history window cannot serve this date; do not promote.",
            }

            if not raw_path.exists():
                results.append({**base, "ohlcv_equal": "UNKNOWN_RAW_FILE_MISSING",
                                "raw_file_sha256": "", "smc_open": "", "smc_high": "",
                                "smc_low": "", "smc_close": "", "smc_volume": "",
                                "close_delta_external_minus_smc": "",
                                "volume_delta_external_minus_smc": ""})
                continue

            raw_bytes = raw_path.read_bytes()
            raw_hash = sha256(raw_bytes)
            with raw_path.open(newline="", encoding="utf-8-sig") as raw_fh:
                matches = [r for r in csv.DictReader(raw_fh) if r.get("Date") == day]

            if len(matches) != 1:
                results.append({**base, "ohlcv_equal": "UNKNOWN_RAW_DATE_NOT_UNIQUE",
                                "raw_file_sha256": raw_hash, "smc_open": "", "smc_high": "",
                                "smc_low": "", "smc_close": "", "smc_volume": "",
                                "close_delta_external_minus_smc": "",
                                "volume_delta_external_minus_smc": ""})
                continue

            raw = matches[0]
            smc = {field: raw.get(field, "") for field in ("Open", "High", "Low", "Close", "Volume")}
            pairs = [
                (decimal_or_none(smc["Open"]), decimal_or_none(base["external_open"])),
                (decimal_or_none(smc["High"]), decimal_or_none(base["external_high"])),
                (decimal_or_none(smc["Low"]), decimal_or_none(base["external_low"])),
                (decimal_or_none(smc["Close"]), decimal_or_none(base["external_close"])),
                (decimal_or_none(smc["Volume"]), decimal_or_none(base["external_volume"])),
            ]
            equal = all(a is not None and b is not None and a == b for a, b in pairs)
            smc_close, ext_close = pairs[3]
            smc_volume, ext_volume = pairs[4]
            results.append({
                **base,
                "smc_open": smc["Open"], "smc_high": smc["High"],
                "smc_low": smc["Low"], "smc_close": smc["Close"],
                "smc_volume": smc["Volume"],
                "close_delta_external_minus_smc": str(ext_close - smc_close) if ext_close is not None and smc_close is not None else "",
                "volume_delta_external_minus_smc": str(ext_volume - smc_volume) if ext_volume is not None and smc_volume is not None else "",
                "ohlcv_equal": "TRUE" if equal else "FALSE",
                "raw_file_sha256": raw_hash,
            })

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTPUT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--external-csv", type=Path,
                        default=Path("reference/p423_2025-07-28_external_conflict_counterpart_2026-11-26.csv"))
    parser.add_argument("--raw-dir", type=Path, default=Path("03_stock_charts_ohlcv"))
    parser.add_argument("--output", type=Path,
                        default=Path("reference/p424_2025-07-28_conflict_matrix_2026-11-26.csv"))
    args = parser.parse_args()
    rows = build_matrix(args.external_csv, args.raw_dir, args.output)
    counts = {}
    for row in rows:
        counts[row["ohlcv_equal"]] = counts.get(row["ohlcv_equal"], 0) + 1
    print({"rows": len(rows), "dispositions": len({r["canonical_disposition"] for r in rows}),
           "comparison_status": counts, "output": str(args.output)})
    if len(rows) != 86:
        raise SystemExit(f"Expected 86 counterpart rows; found {len(rows)}")
    if any(r["canonical_disposition"] != "UNKNOWN_SOURCE_CONFLICT" for r in rows):
        raise SystemExit("A secondary-only row was incorrectly promoted")


if __name__ == "__main__":
    main()
