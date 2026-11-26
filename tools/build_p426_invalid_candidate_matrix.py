#!/usr/bin/env python3
"""Compare 109 invalid ShareSansar backfill candidates with same-day page captures."""
import argparse
import csv
import hashlib
from decimal import Decimal, InvalidOperation
from pathlib import Path

FIELDS = [
    "symbol", "date", "external_open", "external_high", "external_low",
    "external_close", "external_volume", "external_turnover", "invalid_reason",
    "snapshot_open", "snapshot_high", "snapshot_low", "snapshot_close",
    "snapshot_volume", "snapshot_turnover", "snapshot_trades",
    "snapshot_ohlc_valid", "snapshot_matches_external",
    "external_series_sha256", "snapshot_file_sha256", "snapshot_commit",
    "snapshot_commit_time", "disposition",
]
SNAPSHOTS = {
    "2026-04-24": ("2026_04_24.csv", "83c5d4502cec1d77a5b7247510e7c22b10ccf3bf", "2026-04-24T12:09:13Z"),
    "2026-04-27": ("2026_04_27.csv", "6d6d88bad68e0825bbed53dd56e4d41834ab3e97", "2026-04-27T12:55:06Z"),
    "2026-04-28": ("2026_04_28.csv", "2dcb63476bb257191f4d0533421643716c61192c", "2026-04-28T13:00:39Z"),
    "2026-04-29": ("2026_04_29.csv", "bde9e1e0876042c8bdb299dae796861a3a83e037", "2026-04-29T12:56:37Z"),
}


def dec(value):
    try:
        return Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, TypeError):
        return None


def sha(data):
    return hashlib.sha256(data).hexdigest()


def valid_ohlc(o, h, l, c):
    return all(x is not None and x > 0 for x in (o, h, l, c)) and l <= min(o, c) <= max(o, c) <= h


def read_snapshot(path):
    raw = path.read_bytes()
    with path.open(newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    indexed = {}
    for row in rows:
        symbol = row.get("Symbol", "").strip().upper()
        if symbol:
            if symbol in indexed:
                raise ValueError(f"duplicate symbol in same-day snapshot: {symbol}")
            indexed[symbol] = row
    return raw, indexed


def build(queue_path, snapshot_dir, output_path, expected_count=109):
    with queue_path.open(newline="", encoding="utf-8-sig") as fh:
        queue = list(csv.DictReader(fh))
    if expected_count is not None and len(queue) != expected_count:
        raise ValueError(f"expected {expected_count} quarantined rows, found {len(queue)}")

    cache = {}
    output = []
    for item in queue:
        day = item["date"]
        symbol = item["symbol"].strip().upper()
        if day not in SNAPSHOTS:
            raise ValueError(f"no same-day snapshot metadata for {day}")
        filename, commit, commit_time = SNAPSHOTS[day]
        if day not in cache:
            raw, rows = read_snapshot(snapshot_dir / filename)
            cache[day] = (sha(raw), rows)
        snapshot_hash, indexed = cache[day]
        row = indexed.get(symbol)
        if row is None:
            snap = {k: "" for k in ("Open", "High", "Low", "Close", "Vol", "Turnover", "Trans.")}
            status = "NO_SAME_DAY_SNAPSHOT_ROW"
            valid = ""
            matches = ""
        else:
            snap = {k: row.get(k, "") for k in ("Open", "High", "Low", "Close", "Vol", "Turnover", "Trans.")}
            so, sh, sl, sc, sv = (dec(snap[k]) for k in ("Open", "High", "Low", "Close", "Vol"))
            eo, eh, el, ec, ev = (dec(item[k]) for k in ("open", "high", "low", "close", "volume"))
            valid = str(valid_ohlc(so, sh, sl, sc)).upper()
            matches = str((so, sh, sl, sc, sv) == (eo, eh, el, ec, ev)).upper()
            if matches == "TRUE" and valid == "FALSE":
                status = "SAME_DAY_SNAPSHOT_CONFIRMS_INVALID_CANDLE"
            elif valid == "TRUE":
                status = "SAME_DAY_SNAPSHOT_HAS_VALID_CANDLE_DIFFERENT_OR_EXTERNAL_INVALID"
            else:
                status = "SAME_DAY_SNAPSHOT_ALSO_INVALID_BUT_VALUES_DIFFER"
        eo, eh, el = (dec(item[k]) for k in ("open", "high", "low"))
        reason = "OPEN_ABOVE_HIGH" if eo > eh else "OPEN_BELOW_LOW" if eo < el else "OTHER_OHLC_INVALID"
        output.append({
            "symbol": symbol, "date": day,
            "external_open": item["open"], "external_high": item["high"],
            "external_low": item["low"], "external_close": item["close"],
            "external_volume": item["volume"], "external_turnover": item["turnover"],
            "invalid_reason": reason,
            "snapshot_open": snap["Open"], "snapshot_high": snap["High"],
            "snapshot_low": snap["Low"], "snapshot_close": snap["Close"],
            "snapshot_volume": snap["Vol"], "snapshot_turnover": snap["Turnover"],
            "snapshot_trades": snap["Trans."],
            "snapshot_ohlc_valid": valid, "snapshot_matches_external": matches,
            "external_series_sha256": item["external_sha256"],
            "snapshot_file_sha256": snapshot_hash,
            "snapshot_commit": commit, "snapshot_commit_time": commit_time,
            "disposition": status,
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
    parser.add_argument("--snapshot-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = build(args.queue, args.snapshot_dir, args.output)
    counts = {}
    for row in rows:
        counts[row["disposition"]] = counts.get(row["disposition"], 0) + 1
    print({"rows": len(rows), "dispositions": counts, "output": str(args.output)})
    if counts.get("SAME_DAY_SNAPSHOT_CONFIRMS_INVALID_CANDLE", 0) != 109:
        raise SystemExit("The full 109-row same-day invalid-candle match was not established")


if __name__ == "__main__":
    main()
