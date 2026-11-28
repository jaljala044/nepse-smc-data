"""Combine the supplemental NEPSE inputs with an existing scanner data directory."""
import argparse
import csv
import hashlib
import json
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


def unique_rows_with_dispositions(records, key_fields, numeric_fields, source_path, source_sha256):
    """Return deduplicated rows plus a row-level audit tied to immutable source bytes."""
    seen = {}
    retained = []
    dispositions = []
    for row_number, row in enumerate(records, start=2):
        key = business_key(row, key_fields)
        signature = numeric_signature(row, numeric_fields)
        if key in seen:
            if seen[key] != signature:
                raise ValueError(f"Conflicting duplicate key: {key}")
            disposition = "duplicate_identical_collapsed"
        else:
            seen[key] = signature
            retained.append(row)
            disposition = "retained"
        dispositions.append({
            "source_path": str(source_path),
            "source_sha256": source_sha256,
            "source_row_number": row_number,
            "business_key": list(key),
            "numeric_signature": [str(value) for value in signature],
            "disposition": disposition,
        })
    return retained, dispositions


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
        raw_evidence = stage / "evidence" / "raw_inputs"
        raw_evidence.mkdir(parents=True, exist_ok=True)
        original_bytes = daily.read_bytes()
        original_sha256 = hashlib.sha256(original_bytes).hexdigest()
        (raw_evidence / "original_daily_prices.csv").write_bytes(original_bytes)
        original_raw = list(rows(daily))
        original_rows, source_dispositions = unique_rows_with_dispositions(
            original_raw, ("symbol", "date"), price_fields,
            "original/daily_prices.csv", original_sha256)
        present = {business_key(row, ("symbol", "date")): numeric_signature(row, price_fields)
                   for row in original_rows}
        additions = []
        raw_artifacts = [{
            "source_path": "original/daily_prices.csv",
            "evidence_path": "evidence/raw_inputs/original_daily_prices.csv",
            "sha256": original_sha256,
            "size_bytes": len(original_bytes),
        }]
        supplement_price_paths = [SUPPLEMENT / "benchmark_daily.csv", *sorted((SUPPLEMENT / "price_gap_fills").glob("*.csv"))]
        for source_path in supplement_price_paths:
            raw = source_path.read_bytes()
            relative = Path("supplement") / source_path.relative_to(SUPPLEMENT)
            target = raw_evidence / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            raw_artifacts.append({
                "source_path": str(source_path.relative_to(SUPPLEMENT)),
                "evidence_path": str(Path("evidence/raw_inputs") / relative),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "size_bytes": len(raw),
            })
        for path in supplement_price_paths:
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
                records = []
                for source_path in partitions:
                    raw = source_path.read_bytes()
                    relative = Path("supplement/broker_summary") / source_path.name
                    evidence_path = raw_evidence / relative
                    evidence_path.parent.mkdir(parents=True, exist_ok=True)
                    evidence_path.write_bytes(raw)
                    digest = hashlib.sha256(raw).hexdigest()
                    raw_artifacts.append({
                        "source_path": str(source_path.relative_to(SUPPLEMENT)),
                        "evidence_path": str(Path("evidence/raw_inputs") / relative),
                        "sha256": digest,
                        "size_bytes": len(raw),
                    })
                    source_rows, dispositions = unique_rows_with_dispositions(
                        list(rows(source_path)), ("symbol", "date", "broker"),
                        ("buy_qty", "sell_qty", "buy_value", "sell_value"),
                        str(source_path.relative_to(SUPPLEMENT)), digest)
                    records.extend(source_rows)
                    source_dispositions.extend(dispositions)
                writer.writerows(unique_rows(records, ("symbol", "date", "broker"),
                    ("buy_qty", "sell_qty", "buy_value", "sell_value")))
        elif broker_target.exists():
            # Existing supplied broker summaries must not silently contain duplicate keys.
            broker_bytes = broker_target.read_bytes()
            broker_sha256 = hashlib.sha256(broker_bytes).hexdigest()
            (raw_evidence / "original_broker_summary.csv").write_bytes(broker_bytes)
            with broker_target.open(newline="", encoding="utf-8-sig") as stream:
                fields = csv.DictReader(stream).fieldnames
            records, broker_dispositions = unique_rows_with_dispositions(
                list(rows(broker_target)), ("symbol", "date", "broker"),
                ("buy_qty", "sell_qty", "buy_value", "sell_value"),
                "original/broker_summary.csv", broker_sha256)
            source_dispositions.extend(broker_dispositions)
            write(broker_target, fields, records)
        manifest = {
            "schema_version": 1,
            "policy": "raw_inputs_preserved; identical_duplicates_collapsed_only_in_scanner_staging",
            "canonical_promotion_allowed": False,
            "raw_artifacts": raw_artifacts,
            "records": source_dispositions,
        }
        manifest_path = stage / "evidence" / "duplicate_disposition_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        stage.rename(output)
    print(f"Prepared {output} with {len(additions)} new daily price rows.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path, help="Existing data directory with daily_prices.csv")
    parser.add_argument("output", type=Path, help="A new output directory")
    args = parser.parse_args()
    prepare(args.original, args.output)
