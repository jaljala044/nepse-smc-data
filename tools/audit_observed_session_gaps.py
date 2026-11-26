#!/usr/bin/env python3
"""Compare equity OHLCV archive rows with positive market-session observations.

This is an observational gap audit only. Missing rows are never labelled NO_TRADE.
"""
import argparse
import csv
from collections import Counter
from datetime import date
from pathlib import Path

OPEN_STATUS = "verified_open_observed"


def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def parse_date(value):
    value = (value or "").strip()
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10]).isoformat()
    except ValueError:
        return None


def load_universe(path, expected_count):
    rows = read_csv(path)
    symbols = sorted({
        (row.get("symbol") or "").strip().upper()
        for row in rows
        if (row.get("symbol") or "").strip()
        and (not row.get("instrument_class_from_rendered_list")
             or row.get("instrument_class_from_rendered_list", "").strip() == "Equity")
    })
    if len(symbols) != expected_count:
        raise ValueError(f"expected {expected_count} unique equity symbols, got {len(symbols)}")
    return symbols


def load_observed_dates(path):
    dates = sorted({
        parsed for row in read_csv(path)
        if row.get("status") == OPEN_STATUS
        for parsed in [parse_date(row.get("date"))]
        if parsed
    })
    if not dates:
        raise ValueError("no positive observed-open dates in canonical calendar")
    return dates


def audit_symbol(symbol, observed_dates, ohlcv_dir):
    path = Path(ohlcv_dir) / f"{symbol}_OHLCV.csv"
    observed = set(observed_dates)
    counts = Counter()
    positive_volume_dates = set()
    if not path.is_file():
        return {
            "symbol": symbol, "file_status": "MISSING_FILE",
            "observed_session_dates": len(observed_dates), "present_date_count": 0,
            "missing_archive_date_count": len(observed_dates), "duplicate_date_count": 0,
            "invalid_date_row_count": 0, "positive_volume_date_count": 0,
            "first_observed_date": "", "last_observed_date": "",
            "classification": "ARCHIVE_GAP_REVIEW_REQUIRED",
            "missing_dates": sorted(observed),
        }
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "Date" not in reader.fieldnames:
            raise ValueError(f"{path}: missing Date column")
        for row in reader:
            parsed = parse_date(row.get("Date"))
            if not parsed:
                counts["invalid"] += 1
                continue
            if parsed in observed:
                counts[parsed] += 1
                try:
                    volume = float((row.get("Volume") or "0").replace(",", ""))
                except ValueError:
                    volume = 0.0
                if volume > 0:
                    positive_volume_dates.add(parsed)
    present = set(counts)
    duplicate_count = sum(n - 1 for n in counts.values() if n > 1)
    missing = observed - present
    return {
        "symbol": symbol, "file_status": "PRESENT",
        "observed_session_dates": len(observed_dates), "present_date_count": len(present),
        "missing_archive_date_count": len(missing), "duplicate_date_count": duplicate_count,
        "invalid_date_row_count": counts["invalid"], "positive_volume_date_count": len(positive_volume_dates),
        "first_observed_date": min(present) if present else "",
        "last_observed_date": max(present) if present else "",
        "classification": "ARCHIVE_GAP_REVIEW_REQUIRED" if missing or duplicate_count or counts["invalid"] else "OBSERVATIONS_COMPLETE_FOR_SAMPLE_ONLY",
        "missing_dates": sorted(missing),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--universe", type=Path, required=True)
    parser.add_argument("--calendar", type=Path, required=True)
    parser.add_argument("--ohlcv-dir", type=Path, required=True)
    parser.add_argument("--expected-symbol-count", type=int, default=281)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--detail-output", type=Path, required=True)
    args = parser.parse_args()
    symbols = load_universe(args.universe, args.expected_symbol_count)
    dates = load_observed_dates(args.calendar)
    rows = [audit_symbol(symbol, dates, args.ohlcv_dir) for symbol in symbols]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = [key for key in rows[0] if key != "missing_dates"]
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({key: row[key] for key in fields} for row in rows)
    args.detail_output.parent.mkdir(parents=True, exist_ok=True)
    with args.detail_output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["symbol", "observed_date", "gap_type"])
        writer.writeheader()
        for row in rows:
            for missing_date in row["missing_dates"]:
                writer.writerow({"symbol": row["symbol"], "observed_date": missing_date,
                                 "gap_type": "OHLCV_ROW_ABSENT_NOT_NO_TRADE"})
    print(f"symbols={len(rows)} observed_market_dates={len(dates)}")
    print("missing_files=" + str(sum(r["file_status"] == "MISSING_FILE" for r in rows)))
    print("symbols_with_archive_gaps=" + str(sum(r["classification"] == "ARCHIVE_GAP_REVIEW_REQUIRED" for r in rows)))
    print("missing_date_cells=" + str(sum(int(r["missing_archive_date_count"]) for r in rows)))
    print("duplicate_date_rows=" + str(sum(int(r["duplicate_date_count"]) for r in rows)))
    print("top_20_archive_gap_symbols=" + ",".join(
        f'{r["symbol"]}:{r["missing_archive_date_count"]}'
        for r in sorted(rows, key=lambda x: (-int(x["missing_archive_date_count"]), x["symbol"]))[:20]
    ))
    print("IMPORTANT: missing OHLCV rows are archive gaps, not NO_TRADE evidence.")


if __name__ == "__main__":
    main()
