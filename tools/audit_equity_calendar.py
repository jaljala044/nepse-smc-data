"""Read-only point-in-time OHLCV and calendar audit for the current equity universe.

This script deliberately does not infer listing dates or promote candidate weekdays
to confirmed sessions. It records archive observations and source hashes only.
"""
import argparse
import csv
import hashlib
import json
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def decimal_value(row, key):
    value = row.get(key, "")
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, TypeError, ValueError):
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smc", type=Path, required=True)
    parser.add_argument("--starter", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    reference = args.smc / "reference"
    universe_path = reference / "nepse_target_universe_candidates_2026-11-26.csv"
    universe_rows = read_csv(universe_path)
    symbols = sorted({
        row["symbol"].strip()
        for row in universe_rows
        if row.get("instrument_class_from_rendered_list", "").strip() == "Equity"
    })
    if len(symbols) != 281:
        raise ValueError(f"Expected 281 current equities, found {len(symbols)}")

    calendar_rows = read_csv(reference / "nepse_canonical_session_calendar_2025-2026.csv")
    calendar = {row["date"]: row["status"] for row in calendar_rows}
    summary = []
    flags = []

    for repository_name, root in (("starter", args.starter), ("smc", args.smc)):
        for symbol in symbols:
            path = root / "03_stock_charts_ohlcv" / f"{symbol}_OHLCV.csv"
            base = {"repository": repository_name, "symbol": symbol, "file_path": str(path.relative_to(root))}
            if not path.is_file():
                summary.append({**base, "status": "MISSING"})
                continue

            raw = path.read_bytes()
            sha256 = hashlib.sha256(raw).hexdigest()
            try:
                rows = read_csv(path)
            except (UnicodeDecodeError, csv.Error) as exc:
                summary.append({**base, "status": "UNREADABLE", "source_sha256": sha256, "error": str(exc)})
                continue

            counts = Counter()
            malformed = 0
            invalid_ohlc = 0
            nonpositive_volume = 0
            duplicate_dates = 0
            out_of_order = 0
            adjacent_identical = 0
            first_date = ""
            last_date = ""
            first_positive_volume_date = ""
            last_positive_volume_date = ""
            seen_dates = set()
            prior_values = None
            prior_date = ""

            for line_number, original in enumerate(rows, 2):
                row = {str(key).strip().lower(): value for key, value in original.items() if key is not None}
                required = ("date", "open", "high", "low", "close", "volume")
                if any(key not in row for key in required):
                    malformed += 1
                    flags.append({**base, "date": row.get("date", ""), "line": line_number,
                                  "flag": "missing_required_field", "source_sha256": sha256})
                    continue

                date = str(row.get("date", "")).strip()
                values = tuple(decimal_value(row, key) for key in ("open", "high", "low", "close", "volume"))
                if len(date) != 10 or any(value is None for value in values):
                    malformed += 1
                    flags.append({**base, "date": date, "line": line_number,
                                  "flag": "malformed_date_or_numeric_value", "source_sha256": sha256})
                    continue

                open_, high, low, close, volume = values
                if not first_date or date < first_date:
                    first_date = date
                if not last_date or date > last_date:
                    last_date = date
                if date in seen_dates:
                    duplicate_dates += 1
                    flags.append({**base, "date": date, "line": line_number,
                                  "flag": "duplicate_date", "source_sha256": sha256})
                seen_dates.add(date)
                if prior_date and date < prior_date:
                    out_of_order += 1
                    flags.append({**base, "date": date, "line": line_number,
                                  "flag": "out_of_order_date", "source_sha256": sha256})
                prior_date = date

                if not (min(open_, high, low, close) > 0 and high >= max(open_, low, close)
                        and low <= min(open_, high, close)):
                    invalid_ohlc += 1
                    flags.append({**base, "date": date, "line": line_number,
                                  "flag": "invalid_ohlc_bounds", "source_sha256": sha256})
                if volume <= 0:
                    nonpositive_volume += 1
                    flags.append({**base, "date": date, "line": line_number,
                                  "flag": "nonpositive_volume", "source_sha256": sha256})
                else:
                    if not first_positive_volume_date or date < first_positive_volume_date:
                        first_positive_volume_date = date
                    if not last_positive_volume_date or date > last_positive_volume_date:
                        last_positive_volume_date = date

                status = calendar.get(date, "outside_calendar")
                counts[status] += 1
                if status == "verified_closed":
                    flags.append({**base, "date": date, "line": line_number,
                                  "flag": "row_on_verified_closed_date", "source_sha256": sha256,
                                  "open": str(open_), "high": str(high), "low": str(low),
                                  "close": str(close), "volume": str(volume)})

                if values == prior_values:
                    adjacent_identical += 1
                    flags.append({**base, "date": date, "line": line_number,
                                  "flag": "adjacent_identical_ohlcv_review", "source_sha256": sha256,
                                  "open": str(open_), "high": str(high), "low": str(low),
                                  "close": str(close), "volume": str(volume)})
                prior_values = values

            summary.append({
                **base, "status": "AUDITED", "rows": len(rows), "first_archive_date": first_date,
                "last_archive_date": last_date, "first_positive_volume_date": first_positive_volume_date,
                "last_positive_volume_date": last_positive_volume_date, "malformed_rows": malformed,
                "duplicate_date_rows": duplicate_dates, "out_of_order_rows": out_of_order,
                "invalid_ohlc_rows": invalid_ohlc, "nonpositive_volume_rows": nonpositive_volume,
                "adjacent_identical_ohlcv_rows": adjacent_identical,
                "verified_closed_rows": counts["verified_closed"],
                "verified_open_observed_rows": counts["verified_open_observed"],
                "candidate_open_weekday_rows": counts["candidate_open_weekday"],
                "outside_calendar_rows": counts["outside_calendar"], "source_sha256": sha256,
            })

    summary_fields = sorted({key for row in summary for key in row})
    flag_fields = sorted({key for row in flags for key in row})
    for filename, records, fields in (
        ("summary.csv", summary, summary_fields),
        ("row_flags.csv", flags, flag_fields or ["repository", "symbol", "date", "line", "flag", "source_sha256"]),
    ):
        with (args.output / filename).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(records)

    totals = {}
    for repository_name in ("starter", "smc"):
        selected = [row for row in summary if row["repository"] == repository_name]
        totals[repository_name] = {
            "files_expected": len(symbols),
            "files_audited": sum(row["status"] == "AUDITED" for row in selected),
            "files_missing": sum(row["status"] == "MISSING" for row in selected),
            "files_unreadable": sum(row["status"] == "UNREADABLE" for row in selected),
        }
        for key in ("rows", "malformed_rows", "duplicate_date_rows", "out_of_order_rows",
                    "invalid_ohlc_rows", "nonpositive_volume_rows", "adjacent_identical_ohlcv_rows",
                    "verified_closed_rows", "verified_open_observed_rows",
                    "candidate_open_weekday_rows", "outside_calendar_rows"):
            totals[repository_name][key] = sum(row.get(key, 0) for row in selected)

    (args.output / "totals.json").write_text(json.dumps({
        "universe_size": len(symbols),
        "calendar_note": "candidate_open_weekday is not a confirmed session; verified_open_observed is sampled-security evidence only",
        "lifecycle_note": "archive first date is not a listing or first-trade date",
        "totals": totals,
        "promotion_allowed": False,
        "training_allowed": False,
    }, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(totals, indent=2))
    if any(value["files_missing"] or value["files_unreadable"] for value in totals.values()):
        raise SystemExit("Some equity OHLCV files are missing or unreadable; inspect summary.csv")


if __name__ == "__main__":
    main()
