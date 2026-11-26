"""Combine the supplemental NEPSE inputs with an existing scanner data directory."""
import argparse
import csv
import shutil
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from tempfile import TemporaryDirectory

SUPPLEMENT = Path(__file__).resolve().parent
TABLE_EXTENSIONS = (".csv", ".xlsx", ".xls")


def rows(path):
    with path.open(newline="", encoding="utf-8-sig") as stream:
        yield from csv.DictReader(stream)


def write(path, fields, values):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(values)


def has_table(directory, *names):
    return any((directory / f"{name}{suffix}").exists()
               for name in names for suffix in TABLE_EXTENSIONS)


def validate_daily(values, closed_dates):
    """Fail closed before publishing; never silently remove or repair rows."""
    seen = set()
    for number, row in enumerate(values, 2):
        symbol = row["symbol"].strip().upper()
        day = row["date"].strip()
        try:
            if not symbol or date.fromisoformat(day).isoformat() != day:
                raise ValueError("invalid symbol/date")
            o, h, l, c, v = (Decimal(row[k]) for k in ("open", "high", "low", "close", "volume"))
            if not all(x.is_finite() for x in (o, h, l, c, v)):
                raise ValueError("non-finite OHLCV")
            if min(o, h, l, c) <= 0 or v < 0 or h < max(o, l, c) or l > min(o, h, c):
                raise ValueError("invalid OHLCV")
            if day in closed_dates:
                raise ValueError("verified closed session")
            key = (symbol, day)
            if key in seen:
                raise ValueError("duplicate symbol/date")
            seen.add(key)
        except (ValueError, InvalidOperation, TypeError, KeyError, AttributeError) as exc:
            raise ValueError(f"Rejected daily row {number}: {symbol} {day}: {exc}") from exc


def verified_closed_dates():
    reference = SUPPLEMENT.parent / "reference"
    calendar = reference / "nepse_canonical_session_calendar_2025-2026.csv"
    positive = reference / "nepse_positive_open_sessions_2025-11-26_2026-11-25.csv"
    closed = {r["date"] for r in rows(calendar)
              if r["status"] == "verified_closed" and r["scope"] == "all_securities"}
    opened = {r["date"] for r in rows(positive) if r["status"] == "verified_open"}
    if not closed or not opened or closed & opened:
        raise ValueError("Missing or conflicting session evidence")
    return closed


def prepare(original, output):
    if output.exists():
        raise FileExistsError(f"Choose a new output folder: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output.parent) as temp:
        stage = Path(temp) / "scanner-data"
        shutil.copytree(original, stage)
        daily = stage / "daily_prices.csv"
        with daily.open(newline="", encoding="utf-8-sig") as stream:
            fields = csv.DictReader(stream).fieldnames
        if not fields or not {"symbol", "date", "open", "high", "low", "close", "volume"}.issubset(fields):
            raise ValueError("Expected a scanner-format daily_prices.csv in the input folder.")
        original_rows = list(rows(daily))
        closed_dates = verified_closed_dates()
        validate_daily(original_rows, closed_dates)
        present = {(row["symbol"].strip().upper(), row["date"]) for row in original_rows}
        additions = []
        for path in [SUPPLEMENT / "benchmark_daily.csv", *sorted((SUPPLEMENT / "price_gap_fills").glob("*.csv"))]:
            for row in rows(path):
                key = row["symbol"], row["date"]
                if key not in present:
                    additions.append(row)
                    present.add(key)
        validate_daily(original_rows + additions, closed_dates)
        if additions:
            extra = dict.fromkeys(field for row in additions for field in row if field not in fields)
            combined = sorted(original_rows + additions, key=lambda row: (row["symbol"], row["date"]))
            write(daily, [*fields, *extra], combined)
            # The scanner rebuilds both periods from daily prices after adding a historical session.
            price_history_changed = any(row["symbol"] != "NEPSE" for row in additions)
            if price_history_changed:
                for name in ("weekly_prices", "monthly_prices"):
                    for suffix in TABLE_EXTENSIONS:
                        (stage / f"{name}{suffix}").unlink(missing_ok=True)
        for name in ("sectors", "sector_data", "corporate_actions"):
            destination = stage / f"{name}.csv"
            if not has_table(stage, name):
                shutil.copyfile(SUPPLEMENT / destination.name, destination)
        broker_target = stage / "broker_summary.csv"
        if not has_table(stage, "broker_summary", "brokers", "floorsheet"):
            partitions = sorted((SUPPLEMENT / "broker_summary").glob("*.csv"))
            if not partitions:
                raise ValueError("Missing supplemental broker session files.")
            expected = ["symbol", "date", "broker", "buy_qty", "sell_qty", "buy_value", "sell_value"]
            with broker_target.open("w", newline="", encoding="utf-8") as target:
                writer = csv.DictWriter(target, expected)
                writer.writeheader()
                for path in partitions:
                    writer.writerows(rows(path))
        stage.rename(output)
    print(f"Prepared {output} with {len(additions)} new daily price rows.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path, help="Existing data directory with daily_prices.csv")
    parser.add_argument("output", type=Path, help="A new output directory")
    args = parser.parse_args()
    prepare(args.original, args.output)
