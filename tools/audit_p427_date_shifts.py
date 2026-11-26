#!/usr/bin/env python3
"""Audit 490 one-calendar-day NEPSE historical date-shift candidates.

The tool compares immutable external candidate tuples with the raw SMC row on
the following calendar date, validates both dates against the pinned session
calendar, and checks same-day ShareSansar daily-page captures. It never edits
raw OHLCV files or changes candidate dates.
"""
import argparse
import csv
import hashlib
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

SHIFT_TARGETS = {
    "2026-03-01": ("2026-03-02", "2026_03_02.csv",
                   "e93c9fdd4841003770d76357a1c570562fd82e55",
                   "2026-03-02T11:48:58Z"),
    "2026-07-24": ("2026-07-25", "2026_07_25.csv",
                   "6d13e28cc7157834114cca241c8d1d1055fe87b7",
                   "2026-07-25T12:12:28Z"),
}
OPTIONAL_SOURCE_SNAPSHOTS = {
    "2026-03-01": ("2026_03_01.csv", "6f92cd975657f2b760c3dc9edf0317804962c1bf",
                   "2026-03-01T11:35:48Z"),
}
FIELDS = [
    "symbol", "external_date", "raw_date", "external_session_status",
    "raw_date_session_status", "open", "high", "low", "close", "volume",
    "raw_open", "raw_high", "raw_low", "raw_close", "raw_volume",
    "raw_tuple_matches", "derived_series_sha256_from_recovery_artifact", "raw_file_sha256_actual",
    "shifted_date_snapshot_open", "shifted_date_snapshot_high",
    "shifted_date_snapshot_low", "shifted_date_snapshot_close",
    "shifted_date_snapshot_volume", "shifted_snapshot_tuple_matches",
    "shifted_snapshot_file_sha256", "shifted_snapshot_commit",
    "shifted_snapshot_capture_time", "same_day_snapshot_row_present",
    "same_day_snapshot_tuple_matches", "same_day_snapshot_commit",
    "disposition",
]


def dec(value):
    try:
        return Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, TypeError):
        return None


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def tuple_from(row, keys):
    return tuple(dec(row.get(k, "")) for k in keys)


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def read_snapshot(path):
    raw = path.read_bytes()
    rows = read_csv(path)
    index = {}
    for row in rows:
        symbol = row.get("Symbol", "").strip().upper()
        if not symbol:
            continue
        if symbol in index:
            raise ValueError(f"duplicate symbol in snapshot {path}: {symbol}")
        index[symbol] = row
    return sha(raw), index


def read_raw(path):
    raw = path.read_bytes()
    rows = read_csv(path)
    index = {}
    for row in rows:
        day = row.get("Date", "").strip()
        if day in index:
            raise ValueError(f"duplicate raw date {day} in {path}")
        index[day] = row
    return sha(raw), index


def build(queue_path, raw_dir, calendar_path, snapshot_dir, output_path,
          expected_count=490):
    candidates = [r for r in read_csv(queue_path)
                  if r.get("status") == "ALREADY_RECOVERED_DATE_SHIFT"]
    if expected_count is not None and len(candidates) != expected_count:
        raise ValueError(f"expected {expected_count} shifted candidates, found {len(candidates)}")

    calendar_rows = read_csv(calendar_path)
    calendar = {}
    for row in calendar_rows:
        day = row.get("date", "").strip()
        if day:
            calendar[day] = row.get("status", "").strip()

    snapshot_cache = {}
    raw_cache = {}
    output = []
    for item in candidates:
        symbol = item["symbol"].strip().upper()
        external_date = item["date"].strip()
        if external_date not in SHIFT_TARGETS:
            raise ValueError(f"unexpected shifted date: {external_date}")
        raw_date, snapshot_name, snapshot_commit, snapshot_time = SHIFT_TARGETS[external_date]
        expected_raw_date = (date.fromisoformat(external_date) + timedelta(days=1)).isoformat()
        if raw_date != expected_raw_date:
            raise ValueError(f"shift map is not a one-day shift: {external_date} -> {raw_date}")

        raw_path = raw_dir / f"{symbol}_OHLCV.csv"
        if not raw_path.is_file():
            raw_sha, raw_rows = "", {}
        else:
            if symbol not in raw_cache:
                raw_cache[symbol] = read_raw(raw_path)
            raw_sha, raw_rows = raw_cache[symbol]
        raw_row = raw_rows.get(raw_date)

        if external_date not in snapshot_cache:
            snapshot_cache[external_date] = read_snapshot(snapshot_dir / snapshot_name)
        snapshot_sha, snapshot_rows = snapshot_cache[external_date]
        snap = snapshot_rows.get(symbol)

        same_day_snap_present = "FALSE"
        same_day_snap_match = "NOT_AVAILABLE"
        same_day_commit = ""
        if external_date in OPTIONAL_SOURCE_SNAPSHOTS:
            same_name, same_commit, _ = OPTIONAL_SOURCE_SNAPSHOTS[external_date]
            same_path = snapshot_dir / same_name
            if same_path.is_file():
                if f"same:{external_date}" not in snapshot_cache:
                    snapshot_cache[f"same:{external_date}"] = read_snapshot(same_path)
                _, same_rows = snapshot_cache[f"same:{external_date}"]
                same = same_rows.get(symbol)
                same_day_commit = same_commit
                if same:
                    same_day_snap_present = "TRUE"
                    same_day_snap_match = str(
                        tuple_from(same, ("Open", "High", "Low", "Close", "Vol"))
                        == tuple_from(item, ("open", "high", "low", "close", "volume"))
                    ).upper()

        external_tuple = tuple_from(item, ("open", "high", "low", "close", "volume"))
        raw_tuple = tuple_from(raw_row or {}, ("Open", "High", "Low", "Close", "Volume"))
        raw_match = raw_row is not None and raw_tuple == external_tuple
        

        snap_tuple = tuple_from(snap or {}, ("Open", "High", "Low", "Close", "Vol"))
        snap_match = snap is not None and snap_tuple == external_tuple

        ext_status = calendar.get(external_date, "NOT_IN_CALENDAR")
        raw_status = calendar.get(raw_date, "NOT_IN_CALENDAR")
        if raw_match and ext_status == "verified_open_observed" and raw_status == "verified_closed" and snap_match:
            disposition = "SECONDARY_CORROBORATED_ONE_DAY_DATE_SHIFT_PRIMARY_PENDING"
        elif raw_match and ext_status == "verified_open_observed" and raw_status == "verified_closed":
            disposition = "RAW_MATCH_AND_CALENDAR_SHIFT_CONFIRMED_SNAPSHOT_INCOMPLETE"
        else:
            disposition = "UNKNOWN_SHIFT_REQUIRES_ROW_REVIEW"

        output.append({
            "symbol": symbol, "external_date": external_date, "raw_date": raw_date,
            "external_session_status": ext_status, "raw_date_session_status": raw_status,
            "open": item["open"], "high": item["high"], "low": item["low"],
            "close": item["close"], "volume": item["volume"],
            "raw_open": raw_row.get("Open", "") if raw_row else "",
            "raw_high": raw_row.get("High", "") if raw_row else "",
            "raw_low": raw_row.get("Low", "") if raw_row else "",
            "raw_close": raw_row.get("Close", "") if raw_row else "",
            "raw_volume": raw_row.get("Volume", "") if raw_row else "",
            "raw_tuple_matches": str(raw_match).upper(),
            "derived_series_sha256_from_recovery_artifact": item.get("derived_sha256", ""),
            "raw_file_sha256_actual": raw_sha,
            "shifted_date_snapshot_open": snap.get("Open", "") if snap else "",
            "shifted_date_snapshot_high": snap.get("High", "") if snap else "",
            "shifted_date_snapshot_low": snap.get("Low", "") if snap else "",
            "shifted_date_snapshot_close": snap.get("Close", "") if snap else "",
            "shifted_date_snapshot_volume": snap.get("Vol", "") if snap else "",
            "shifted_snapshot_tuple_matches": str(snap_match).upper(),
            "shifted_snapshot_file_sha256": snapshot_sha,
            "shifted_snapshot_commit": snapshot_commit,
            "shifted_snapshot_capture_time": snapshot_time,
            "same_day_snapshot_row_present": same_day_snap_present,
            "same_day_snapshot_tuple_matches": same_day_snap_match,
            "same_day_snapshot_commit": same_day_commit,
            "disposition": disposition,
        })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(output)

    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--calendar", type=Path, required=True)
    parser.add_argument("--snapshot-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = build(args.queue, args.raw_dir, args.calendar, args.snapshot_dir, args.output)
    counts = {}
    for row in rows:
        counts[row["disposition"]] = counts.get(row["disposition"], 0) + 1
    print({"rows": len(rows), "dispositions": counts, "output": str(args.output)})
    if len(rows) != 490 or counts.get("UNKNOWN_SHIFT_REQUIRES_ROW_REVIEW", 0):
        raise SystemExit("Not all 490 date-shift candidates passed the full audit")


if __name__ == "__main__":
    main()
