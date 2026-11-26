#!/usr/bin/env python3
"""Full integrity audit for derived OHLCV v2; flags are reported, never silently repaired."""
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

OHLCV = ("Open", "High", "Low", "Close", "Volume")


def git_blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def dec(value):
    try:
        return Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, TypeError):
        return None


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def inspect_ohlcv(symbol, rows, calendar):
    invariant_flags = []
    repeats = []
    calendar_flags = []
    seen = Counter()
    previous = None
    previous_tuple = None
    previous_day = None
    date_order = [r.get("Date", "") for r in rows]
    if date_order != sorted(date_order):
        invariant_flags.append({
            "symbol": symbol, "date": "", "flag": "DATE_ORDER_NOT_SORTED",
            "details": "rows are not in ascending ISO date order",
        })
    for row in rows:
        day = row.get("Date", "")
        seen[day] += 1
        if seen[day] > 1:
            invariant_flags.append({
                "symbol": symbol, "date": day, "flag": "DUPLICATE_DATE",
                "details": f"{seen[day]} rows share this date",
            })
        values = {k: dec(row.get(k)) for k in OHLCV}
        o, h, l, c, v = (values[k] for k in OHLCV)
        reasons = []
        if any(x is None for x in values.values()):
            reasons.append("NON_NUMERIC_OR_MISSING")
        else:
            if min(o, h, l, c) <= 0:
                reasons.append("NONPOSITIVE_PRICE")
            if h < l:
                reasons.append("HIGH_BELOW_LOW")
            if o < l or o > h:
                reasons.append("OPEN_OUTSIDE_RANGE")
            if c < l or c > h:
                reasons.append("CLOSE_OUTSIDE_RANGE")
            if v < 0:
                reasons.append("NEGATIVE_VOLUME")
        for reason in reasons:
            invariant_flags.append({
                "symbol": symbol, "date": day, "flag": reason,
                "details": "|".join(str(row.get(k, "")) for k in OHLCV),
            })

        session_status = calendar.get(day, "outside_calendar")
        if session_status == "verified_closed":
            calendar_flags.append({
                "symbol": symbol, "date": day, "calendar_status": session_status,
                "flag": "ROW_ON_VERIFIED_CLOSED_DATE",
                "details": "retain for review; may be a repeated/forward-filled source candle",
            })
        elif session_status == "outside_calendar":
            calendar_flags.append({
                "symbol": symbol, "date": day, "calendar_status": session_status,
                "flag": "OUTSIDE_CALENDAR_EVIDENCE_WINDOW",
                "details": "session status unknown; do not infer open/closed",
            })

        current_tuple = tuple(values[k] for k in OHLCV)
        if previous is not None and current_tuple == previous_tuple:
            repeats.append({
                "symbol": symbol, "previous_date": previous_day, "date": day,
                "calendar_status": session_status,
                "classification": (
                    "CLOSED_SESSION_REPEAT_CANDIDATE" if session_status == "verified_closed"
                    else "OPEN_SESSION_REPEAT_REVIEW" if session_status == "verified_open_observed"
                    else "UNCLASSIFIED_ADJACENT_REPEAT"
                ),
                "ohlcv": "|".join(str(row.get(k, "")) for k in OHLCV),
            })
        previous = row
        previous_tuple = current_tuple
        previous_day = day
    return invariant_flags, repeats, calendar_flags, seen


def audit(v2_dir, raw_dir, calendar_path, corporate_actions_path, output_dir,
          expected_symbols=281, expected_official_rows=599, expected_correction_counts=None, split_review_path=None):
    v2_dir, raw_dir, output_dir = Path(v2_dir), Path(raw_dir), Path(output_dir)
    manifest = read_csv(v2_dir / "manifest.csv")
    if len(manifest) != expected_symbols or len({r["symbol"] for r in manifest}) != expected_symbols:
        raise ValueError(f"expected {expected_symbols} unique v2 symbols")
    calendar = {r["date"]: r["status"] for r in read_csv(calendar_path)}
    provenance = read_csv(v2_dir / "provenance_ledger.csv")
    if len(provenance) != expected_official_rows:
        raise ValueError(f"expected {expected_official_rows} official provenance rows")
    corrections = read_csv(v2_dir / "corrections.csv")
    correction_counts = Counter(r["field"] for r in corrections)
    expected_corrections = expected_correction_counts if expected_correction_counts is not None else {"Date": 490, "Row": 109, "Open": 109, "Close": 4, "Volume": 1}
    if dict(correction_counts) != expected_corrections:
        raise ValueError(f"correction ledger field counts differ: {dict(correction_counts)}")

    official_by_symbol = defaultdict(list)
    for row in provenance:
        official_by_symbol[row["symbol"]].append(row)

    invariant_flags, repeats, calendar_flags = [], [], []
    corporate_actions = read_csv(corporate_actions_path)
    actions_by_symbol = defaultdict(list)
    for action in corporate_actions:
        actions_by_symbol[action["symbol"].strip().upper()].append(action)

    corporate_coverage = []
    total_rows = 0
    official_rows_verified = 0
    raw_files_verified = 0
    symbols_with_actions = 0
    for base in manifest:
        symbol = base["symbol"]
        raw_path = raw_dir / f"{symbol}_OHLCV.csv"
        derived_path = v2_dir / f"{symbol}_OHLCV.csv"
        if not raw_path.is_file() or not derived_path.is_file():
            raise ValueError(f"missing raw or v2 file for {symbol}")
        if git_blob_sha(raw_path.read_bytes()) != base["raw_source_blob_sha"]:
            raise ValueError(f"raw source blob mismatch for {symbol}")
        raw_files_verified += 1
        derived_bytes = derived_path.read_bytes()
        if git_blob_sha(derived_bytes) != base["derived_blob_sha"]:
            raise ValueError(f"derived blob mismatch for {symbol}")
        rows = read_csv(derived_path)
        if len(rows) != int(base["rows"]):
            raise ValueError(f"manifest row count mismatch for {symbol}")
        total_rows += len(rows)
        flags, repeat_rows, cal_flags, seen = inspect_ohlcv(symbol, rows, calendar)
        invariant_flags.extend(flags)
        repeats.extend(repeat_rows)
        calendar_flags.extend(cal_flags)

        by_date = defaultdict(list)
        for row in rows:
            by_date[row["Date"]].append(row)
        for item in official_by_symbol.get(symbol, []):
            day = item["official_business_date"]
            matches = by_date.get(day, [])
            if len(matches) != 1:
                raise ValueError(f"official row missing/duplicate in v2: {symbol} {day}")
            actual = matches[0]
            expected = {
                "Open": item["official_open"], "High": item["official_high"],
                "Low": item["official_low"], "Close": item["official_close"],
                "Volume": item["official_volume"],
            }
            if any(dec(actual[k]) != dec(v) for k, v in expected.items()):
                raise ValueError(f"official provenance mismatch in v2: {symbol} {day}")
            official_rows_verified += 1

        events = actions_by_symbol.get(symbol, [])
        if events:
            symbols_with_actions += 1
            for event in events:
                event_day = event.get("event_date", "")
                bars_after = [r["Date"] for r in rows if r["Date"] >= event_day]
                corporate_coverage.append({
                    "symbol": symbol, "event_type": event.get("event_type", ""),
                    "announced_date": event.get("announced_date", ""),
                    "event_date": event_day, "quantity_ratio": event.get("quantity_ratio", ""),
                    "price_factor": event.get("price_factor", ""),
                    "first_bar_on_or_after_event": min(bars_after) if bars_after else "",
                    "event_bar_found": "TRUE" if bars_after else "FALSE",
                    "adjustment_status": "RAW_PRICE_BASIS_REVIEW_REQUIRED",
                    "notes": event.get("notes", ""),
                })
        else:
            corporate_coverage.append({
                "symbol": symbol, "event_type": "", "announced_date": "",
                "event_date": "", "quantity_ratio": "", "price_factor": "",
                "first_bar_on_or_after_event": "", "event_bar_found": "",
                "adjustment_status": "NO_ACTION_RECORD_NOT_VERIFIED",
                "notes": "No row in the current corporate_actions.csv; absence is not evidence of no corporate action",
            })

    if raw_files_verified != expected_symbols or official_rows_verified != expected_official_rows:
        raise ValueError("raw-source or official-row verification incomplete")

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "ohlcv_invariant_flags.csv", invariant_flags,
              ["symbol", "date", "flag", "details"])
    write_csv(output_dir / "adjacent_repeat_flags.csv", repeats,
              ["symbol", "previous_date", "date", "calendar_status", "classification", "ohlcv"])
    write_csv(output_dir / "calendar_alignment_flags.csv", calendar_flags,
              ["symbol", "date", "calendar_status", "flag", "details"])
    write_csv(output_dir / "corporate_action_coverage.csv", corporate_coverage,
              ["symbol", "event_type", "announced_date", "event_date", "quantity_ratio",
               "price_factor", "first_bar_on_or_after_event", "event_bar_found",
               "adjustment_status", "notes"])

    split_review = read_csv(split_review_path) if split_review_path and Path(split_review_path).is_file() else []
    split_flags = []
    for row in split_review:
        effective = row.get("verified_effective_date", "").strip()
        split_flags.append({
            "symbol": row.get("symbol", ""),
            "proposal_date": row.get("proposal_date", ""),
            "old_par_npr": row.get("old_par_npr", ""),
            "proposed_par_npr": row.get("proposed_par_npr", ""),
            "verified_effective_date": effective,
            "assessment": row.get("assessment", ""),
            "disposition": "NO_SPLIT_FACTOR_APPLIED_EFFECTIVE_DATE_UNKNOWN" if not effective else "EFFECTIVE_DATE_REQUIRES_PRIMARY_VALIDATION",
        })
    write_csv(output_dir / "split_review_flags.csv", split_flags,
              ["symbol", "proposal_date", "old_par_npr", "proposed_par_npr",
               "verified_effective_date", "assessment", "disposition"])

    symbols_with_no_action_records = expected_symbols - symbols_with_actions
    totals = {
        "status": "INTEGRITY_CHECKED_WITH_RETAINED_FLAGS",
        "symbols": expected_symbols,
        "derived_rows": total_rows,
        "raw_files_verified_byte_identical_to_manifest": raw_files_verified,
        "official_provenance_rows_verified": official_rows_verified,
        "official_correction_ledger_fields": dict(correction_counts),
        "ohlcv_invariant_flag_rows": len(invariant_flags),
        "adjacent_identical_ohlcv_rows": len(repeats),
        "calendar_alignment_flags": len(calendar_flags),
        "corporate_action_event_records": len(corporate_actions),
        "symbols_with_known_action_records": symbols_with_actions,
        "symbols_without_action_records_not_verified": symbols_with_no_action_records,
        "split_review_rows": len(split_review),
        "split_proposals_without_verified_effective_date": sum(
            1 for r in split_review if not r.get("verified_effective_date", "").strip()
        ),
        "raw_source_files_modified": 0,
        "flags_auto_repaired_or_deleted": 0,
    }
    (output_dir / "audit_totals.json").write_text(json.dumps(totals, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(totals, indent=2))
    return totals


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--v2-dir", type=Path, required=True)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--calendar", type=Path, required=True)
    parser.add_argument("--corporate-actions", type=Path, required=True)
    parser.add_argument("--split-review", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    audit(args.v2_dir, args.raw_dir, args.calendar, args.corporate_actions, args.output_dir,
          split_review_path=args.split_review)


if __name__ == "__main__":
    main()
