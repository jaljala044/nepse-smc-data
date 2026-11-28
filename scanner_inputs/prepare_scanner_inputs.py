"""Combine the supplemental NEPSE inputs with an existing scanner data directory."""
import argparse
import csv
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import date
from decimal import Decimal, InvalidOperation

SUPPLEMENT = Path(__file__).resolve().parent
TABLE_EXTENSIONS = (".csv", ".xlsx", ".xls")


def rows(path):
    with path.open(newline="", encoding="utf-8-sig") as stream:
        yield from csv.DictReader(stream)


def business_key(row, fields):
    values = []
    for field in fields:
        value = str(row.get(field) or "").strip()
        if not value:
            raise ValueError(f"Missing key field: {field}")
        if field == "symbol":
            value = value.upper()
        elif field == "date":
            parsed = date.fromisoformat(value)
            if parsed.isoformat() != value:
                raise ValueError("Noncanonical date")
        elif field == "broker":
            if not value.isascii() or not value.isdigit() or int(value) <= 0:
                raise ValueError("Invalid broker ID")
            value = str(int(value))
        values.append(value)
    return tuple(values)


def numeric_signature(row, fields):
    values = []
    for field in fields:
        try:
            value = Decimal(str(row[field]).strip())
        except (InvalidOperation, KeyError, TypeError, ValueError):
            raise ValueError(f"Invalid numeric field: {field}") from None
        if not value.is_finite():
            raise ValueError(f"Nonfinite numeric field: {field}")
        values.append(value)
    return tuple(values)


def unique_rows(records, key_fields, numeric_fields):
    """Reject conflicting business keys; identical numeric observations count once."""
    seen = {}
    for row in records:
        key = business_key(row, key_fields)
        signature = numeric_signature(row, numeric_fields)
        if key in seen:
            if seen[key] != signature:
                raise ValueError(f"Conflicting duplicate key: {key}")
            continue
        seen[key] = signature
        yield row


def write(path, fields, values):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(values)


def has_table(directory, *names):
    return any((directory / f"{name}{suffix}").exists()
               for name in names for suffix in TABLE_EXTENSIONS)


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
        price_fields = ("open", "high", "low", "close", "volume")
        original_raw = list(rows(daily))
        original_rows = list(unique_rows(original_raw, ("symbol", "date"), price_fields))
        present = {business_key(row, ("symbol", "date")): numeric_signature(row, price_fields)
                   for row in original_rows}
        additions = []
        for path in [SUPPLEMENT / "benchmark_daily.csv", *sorted((SUPPLEMENT / "price_gap_fills").glob("*.csv"))]:
            for row in rows(path):
                key = business_key(row, ("symbol", "date"))
                signature = numeric_signature(row, price_fields)
                if key in present:
                    if present[key] != signature:
                        raise ValueError(f"Conflicting OHLCV overlap: {key}")
                    continue
                additions.append(row)
                present[key] = signature
        if additions or len(original_raw) != len(original_rows):
            extra = dict.fromkeys(field for row in additions for field in row if field not in fields)
            combined = sorted(original_rows + additions, key=lambda row: (row["symbol"], row["date"]))
            write(daily, [*fields, *extra], combined)
            # The scanner rebuilds both periods from daily prices after adding a historical session.
            price_history_changed = len(original_raw) != len(original_rows) or any(row["symbol"] != "NEPSE" for row in additions)
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
                records = (row for path in partitions for row in rows(path))
                writer.writerows(unique_rows(records, ("symbol", "date", "broker"),
                    ("buy_qty", "sell_qty", "buy_value", "sell_value")))
        elif broker_target.exists():
            # Existing supplied broker summaries must not silently contain duplicate keys.
            with broker_target.open(newline="", encoding="utf-8-sig") as stream:
                fields = csv.DictReader(stream).fieldnames
            records = list(unique_rows(rows(broker_target), ("symbol", "date", "broker"),
                ("buy_qty", "sell_qty", "buy_value", "sell_value")))
            write(broker_target, fields, records)
        stage.rename(output)
    print(f"Prepared {output} with {len(additions)} new daily price rows.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path, help="Existing data directory with daily_prices.csv")
    parser.add_argument("output", type=Path, help="A new output directory")
    args = parser.parse_args()
    prepare(args.original, args.output)
