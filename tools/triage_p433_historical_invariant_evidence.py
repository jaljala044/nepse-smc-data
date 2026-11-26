#!/usr/bin/env python3
"""Classify historical v3 invariant flags against currently pinned primary-source coverage."""
import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

FIELDS = [
    "symbol", "date", "flag", "official_eod_status", "floorsheet_archive_status",
    "floorsheet_archive_commit", "corporate_action_status", "secondary_history_status",
    "disposition", "reason",
]


def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def build(flags_path, floorsheet_manifest_path, corporate_actions_path, output_path,
          summary_path, as_of_date="2026-11-26", official_history_days=365,
          expected_flags=1368):
    flags = read_csv(flags_path)
    if expected_flags is not None and len(flags) != expected_flags:
        raise ValueError(f"expected {expected_flags} historical flags, found {len(flags)}")
    inventory = read_csv(floorsheet_manifest_path)
    if not inventory:
        raise ValueError("floorsheet archive inventory is empty")
    available_dates = {r["date"] for r in inventory}
    commits = {r.get("source_commit", "") for r in inventory}
    if len(commits) != 1:
        raise ValueError("floorsheet inventory must pin exactly one source commit")
    floorsheet_commit = next(iter(commits))
    first_floor_date = min(available_dates)
    last_floor_date = max(available_dates)

    actions = read_csv(corporate_actions_path)
    action_symbols = {r.get("symbol", "").strip().upper() for r in actions}
    as_of = date.fromisoformat(as_of_date)
    official_start = as_of - timedelta(days=official_history_days)

    rows = []
    by_symbol = Counter()
    by_flag = Counter()
    by_year = Counter()
    for item in flags:
        symbol, day, flag = item["symbol"].strip().upper(), item["date"], item["flag"]
        d = date.fromisoformat(day)
        if d < official_start:
            official_status = "OUTSIDE_CURRENT_ROLLING_HISTORY_WINDOW"
        else:
            official_status = "WITHIN_WINDOW_BUT_ROW_NOT_YET_RETRIEVED"
        floor_status = "PINNED_DAILY_FILE_PRESENT" if day in available_dates else "NO_PINNED_DAILY_FILE_FOR_DATE"
        action_status = "ACTION_RECORD_PRESENT_REVIEW_REQUIRED" if symbol in action_symbols else "NO_ACTION_RECORD_NOT_PROOF_OF_NONE"
        rows.append({
            "symbol": symbol, "date": day, "flag": flag,
            "official_eod_status": official_status,
            "floorsheet_archive_status": floor_status,
            "floorsheet_archive_commit": floorsheet_commit if floor_status == "PINNED_DAILY_FILE_PRESENT" else "",
            "corporate_action_status": action_status,
            "secondary_history_status": "NOT_VALIDATED_FOR_EXACT_SYMBOL_DATE",
            "disposition": "UNKNOWN_HISTORICAL_PRIMARY_SOURCE_NOT_AVAILABLE",
            "reason": (
                f"Flag predates official rolling window start {official_start.isoformat()}; "
                f"pinned floorsheet archive covers {first_floor_date} to {last_floor_date}; "
                "no exact-date primary evidence is currently available"
            ),
        })
        by_symbol[symbol] += 1
        by_flag[flag] += 1
        by_year[day[:4]] += 1

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "status": "ALL_HISTORICAL_FLAGS_RETAINED_UNKNOWN_NO_UNSUPPORTED_REPAIR",
        "as_of_date": as_of_date,
        "official_history_days": official_history_days,
        "official_history_window_start": official_start.isoformat(),
        "floorsheet_archive_files": len(inventory),
        "floorsheet_archive_first_date": first_floor_date,
        "floorsheet_archive_last_date": last_floor_date,
        "floorsheet_archive_source_commit": floorsheet_commit,
        "historical_flag_rows": len(rows),
        "official_eod_outside_window": sum(r["official_eod_status"] == "OUTSIDE_CURRENT_ROLLING_HISTORY_WINDOW" for r in rows),
        "floorsheet_date_missing": sum(r["floorsheet_archive_status"] == "NO_PINNED_DAILY_FILE_FOR_DATE" for r in rows),
        "corporate_action_record_present": sum(r["corporate_action_status"] == "ACTION_RECORD_PRESENT_REVIEW_REQUIRED" for r in rows),
        "no_action_record_not_proof": sum(r["corporate_action_status"] == "NO_ACTION_RECORD_NOT_PROOF_OF_NONE" for r in rows),
        "secondary_history_exact_date_validated": 0,
        "promoted_or_repaired_rows": 0,
        "flags_by_type": dict(by_flag),
        "flags_by_year": dict(by_year),
        "top_symbols": dict(by_symbol.most_common(20)),
    }
    Path(summary_path).write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--flags", type=Path, required=True)
    parser.add_argument("--floorsheet-manifest", type=Path, required=True)
    parser.add_argument("--corporate-actions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--as-of-date", default="2026-11-26")
    parser.add_argument("--official-history-days", type=int, default=365)
    parser.add_argument("--expected-flags", type=int, default=1368)
    args = parser.parse_args()
    build(args.flags, args.floorsheet_manifest, args.corporate_actions,
          args.output, args.summary, args.as_of_date, args.official_history_days,
          args.expected_flags)


if __name__ == "__main__":
    main()
