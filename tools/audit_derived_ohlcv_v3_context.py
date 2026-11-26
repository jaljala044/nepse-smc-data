#!/usr/bin/env python3
"""Recompute adjacent-repeat, session-calendar and corporate-action context on v3."""
import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def write_csv(path, rows, fields):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def build_context(v3_dir, calendar_path, corporate_actions_path, split_review_path, output_dir,
                  expected_symbols=281):
    v3_dir, output_dir = Path(v3_dir), Path(output_dir)
    manifest = read_csv(v3_dir / "manifest.csv")
    if len(manifest) != expected_symbols or len({r["symbol"] for r in manifest}) != expected_symbols:
        raise ValueError(f"expected {expected_symbols} unique v3 securities")
    calendar = {r["date"]: r["status"] for r in read_csv(calendar_path)}
    actions = read_csv(corporate_actions_path)
    split_review = read_csv(split_review_path)
    actions_by_symbol = defaultdict(list)
    for item in actions:
        actions_by_symbol[item["symbol"].strip().upper()].append(item)

    repeats, calendar_flags, corporate_coverage, split_flags = [], [], [], []
    repeat_counts = Counter()
    calendar_counts = Counter()
    symbols_with_actions = 0
    total_rows = 0

    for base in manifest:
        symbol = base["symbol"]
        path = v3_dir / f"{symbol}_OHLCV.csv"
        if not path.is_file():
            raise ValueError(f"missing v3 file for {symbol}")
        rows = read_csv(path)
        if len(rows) != int(base["rows"]):
            raise ValueError(f"v3 row count differs from manifest for {symbol}")
        dates = [r["Date"] for r in rows]
        if dates != sorted(dates) or len(dates) != len(set(dates)):
            raise ValueError(f"v3 dates unsorted or duplicated for {symbol}")
        total_rows += len(rows)
        previous = None
        previous_day = None
        for row in rows:
            day = row["Date"]
            status = calendar.get(day, "outside_calendar")
            if status == "verified_closed":
                calendar_flags.append({
                    "symbol": symbol, "date": day, "calendar_status": status,
                    "flag": "ROW_ON_VERIFIED_CLOSED_DATE",
                    "details": "Retain for review; may be a repeated/forward-filled source candle",
                })
                calendar_counts["ROW_ON_VERIFIED_CLOSED_DATE"] += 1
            elif status == "outside_calendar":
                calendar_flags.append({
                    "symbol": symbol, "date": day, "calendar_status": status,
                    "flag": "OUTSIDE_CALENDAR_EVIDENCE_WINDOW",
                    "details": "Session status unknown; do not infer open/closed",
                })
                calendar_counts["OUTSIDE_CALENDAR_EVIDENCE_WINDOW"] += 1

            current = tuple(row.get(k, "") for k in ("Open", "High", "Low", "Close", "Volume"))
            if previous is not None and current == previous:
                classification = (
                    "CLOSED_SESSION_REPEAT_CANDIDATE" if status == "verified_closed"
                    else "OPEN_SESSION_REPEAT_REVIEW" if status == "verified_open_observed"
                    else "UNCLASSIFIED_ADJACENT_REPEAT"
                )
                repeats.append({
                    "symbol": symbol, "previous_date": previous_day, "date": day,
                    "calendar_status": status, "classification": classification,
                    "ohlcv": "|".join(current),
                })
                repeat_counts[classification] += 1
            previous, previous_day = current, day

        events = actions_by_symbol.get(symbol, [])
        if events:
            symbols_with_actions += 1
            for event in events:
                event_day = event.get("event_date", "")
                after = [day for day in dates if event_day and day >= event_day]
                corporate_coverage.append({
                    "symbol": symbol, "event_type": event.get("event_type", ""),
                    "announced_date": event.get("announced_date", ""),
                    "event_date": event_day, "quantity_ratio": event.get("quantity_ratio", ""),
                    "price_factor": event.get("price_factor", ""),
                    "first_bar_on_or_after_event": min(after) if after else "",
                    "event_bar_found": "TRUE" if after else "FALSE",
                    "adjustment_status": "RAW_PRICE_BASIS_REVIEW_REQUIRED",
                    "notes": event.get("notes", ""),
                })
        else:
            corporate_coverage.append({
                "symbol": symbol, "event_type": "", "announced_date": "",
                "event_date": "", "quantity_ratio": "", "price_factor": "",
                "first_bar_on_or_after_event": "", "event_bar_found": "",
                "adjustment_status": "NO_ACTION_RECORD_NOT_VERIFIED",
                "notes": "No corporate-action row is not proof that no action occurred",
            })

    for item in split_review:
        effective = item.get("verified_effective_date", "").strip()
        split_flags.append({
            "symbol": item.get("symbol", ""), "proposal_date": item.get("proposal_date", ""),
            "old_par_npr": item.get("old_par_npr", ""),
            "proposed_par_npr": item.get("proposed_par_npr", ""),
            "verified_effective_date": effective, "assessment": item.get("assessment", ""),
            "disposition": "NO_SPLIT_FACTOR_APPLIED_EFFECTIVE_DATE_UNKNOWN" if not effective
                else "EFFECTIVE_DATE_REQUIRES_PRIMARY_VALIDATION",
        })

    write_csv(output_dir / "adjacent_repeat_flags.csv", repeats,
              ["symbol", "previous_date", "date", "calendar_status", "classification", "ohlcv"])
    write_csv(output_dir / "calendar_alignment_flags.csv", calendar_flags,
              ["symbol", "date", "calendar_status", "flag", "details"])
    write_csv(output_dir / "corporate_action_coverage.csv", corporate_coverage,
              ["symbol", "event_type", "announced_date", "event_date", "quantity_ratio",
               "price_factor", "first_bar_on_or_after_event", "event_bar_found",
               "adjustment_status", "notes"])
    write_csv(output_dir / "split_review_flags.csv", split_flags,
              ["symbol", "proposal_date", "old_par_npr", "proposed_par_npr",
               "verified_effective_date", "assessment", "disposition"])

    totals = {
        "status": "V3_CONTEXT_AUDIT_COMPLETE_WITH_UNKNOWN_CALENDAR_AND_CORPORATE_ACTIONS_RETAINED",
        "symbols": expected_symbols, "derived_rows": total_rows,
        "adjacent_identical_ohlcv_rows": len(repeats),
        "adjacent_repeat_classifications": dict(repeat_counts),
        "calendar_alignment_flags": len(calendar_flags),
        "calendar_flag_types": dict(calendar_counts),
        "corporate_action_event_records": len(actions),
        "symbols_with_known_action_records": symbols_with_actions,
        "symbols_without_action_records_not_verified": expected_symbols - symbols_with_actions,
        "split_review_rows": len(split_flags),
        "split_proposals_without_verified_effective_date": sum(not r["verified_effective_date"] for r in split_flags),
        "auto_repairs_or_deletions": 0,
    }
    (output_dir / "context_audit_totals.json").write_text(json.dumps(totals, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(totals, indent=2))
    return totals


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--v3-dir", type=Path, required=True)
    parser.add_argument("--calendar", type=Path, required=True)
    parser.add_argument("--corporate-actions", type=Path, required=True)
    parser.add_argument("--split-review", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--expected-symbols", type=int, default=281)
    args = parser.parse_args()
    build_context(args.v3_dir, args.calendar, args.corporate_actions,
                  args.split_review, args.output_dir, args.expected_symbols)


if __name__ == "__main__":
    main()
