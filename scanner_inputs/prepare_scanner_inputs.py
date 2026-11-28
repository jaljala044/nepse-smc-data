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


def contract_session_date(contract):
    """Interpret only long numeric IDs with a valid YYYYMMDD prefix."""
    value = str(contract or "").strip()
    if len(value) < 14 or not value.isascii() or not value.isdecimal():
        return None
    try:
        return date.fromisoformat(f"{value[:4]}-{value[4:6]}-{value[6:8]}").isoformat()
    except ValueError:
        return None


def validate_floorsheet_sessions(stage):
    """Reject mismatched date-coded contracts before publishing staged inputs."""
    for path in sorted(stage.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(stage)
        if relative.parts[0] == "evidence":
            continue
        name = path.name.lower()
        parents = {p.lower() for p in relative.parts[:-1]}
        if not (name.startswith(("floorsheet.", "floorsheet_")) or
                parents & {"floorsheet", "floorsheets", "02_floorsheet_daily"}):
            continue
        if path.suffix.lower() != ".csv":
            raise ValueError(f"Unsupported floorsheet format: {relative}")
        with path.open(newline="", encoding="utf-8-sig") as stream:
            reader = csv.DictReader(stream)
            headers = reader.fieldnames or []
            normalized = ["".join(c.lower() for c in h if c.isalnum()) for h in headers]
            if len(set(normalized)) != len(normalized):
                raise ValueError(f"Ambiguous floorsheet headers: {relative}")
            def column(aliases):
                matches = [h for h, n in zip(headers, normalized) if n in aliases]
                if len(matches) != 1:
                    raise ValueError(f"Missing or ambiguous floorsheet field: {relative}")
                return matches[0]
            contract_col = column({"contractno", "contractnumber", "contractid"})
            day_col = column({"date", "tradingdate", "tradedate", "businessdate", "calculationdate"})
            for number, row in enumerate(reader, 2):
                if None in row or any(v is None for v in row.values()):
                    raise ValueError(f"Malformed floorsheet row: {relative}:{number}")
                day = row[day_col].strip()
                if date.fromisoformat(day).isoformat() != day or not row[contract_col].strip():
                    raise ValueError(f"Invalid floorsheet identity: {relative}:{number}")
                prefix = contract_session_date(row[contract_col])
                if prefix is not None and prefix != day:
                    raise ValueError(f"Contract session prefix does not match row date: {relative}:{number}")


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
            source_path = str(path.relative_to(SUPPLEMENT))
            source_sha256 = next(item["sha256"] for item in raw_artifacts
                                 if item["source_path"] == source_path)
            for row_number, row in enumerate(rows(path), start=2):
                key = business_key(row, ("symbol", "date"))
                signature = numeric_signature(row, price_fields)
                if key in present:
                    if present[key] != signature:
                        raise ValueError(f"Conflicting OHLCV overlap: {key}")
                    disposition = "duplicate_identical_overlap_skipped"
                else:
                    additions.append(row)
                    present[key] = signature
                    disposition = "new_row_added_to_staging"
                source_dispositions.append({
                    "source_path": source_path,
                    "source_sha256": source_sha256,
                    "source_row_number": row_number,
                    "business_key": list(key),
                    "numeric_signature": [str(value) for value in signature],
                    "disposition": disposition,
                })
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
                broker_seen = {}
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
                    for row_number, row in enumerate(rows(evidence_path), start=2):
                        key = business_key(row, ("symbol", "date", "broker"))
                        signature = numeric_signature(row, ("buy_qty", "sell_qty", "buy_value", "sell_value"))
                        if key in broker_seen:
                            if broker_seen[key] != signature:
                                raise ValueError(f"Conflicting duplicate key: {key}")
                            disposition = "duplicate_identical_collapsed"
                        else:
                            broker_seen[key] = signature
                            records.append(row)
                            disposition = "retained"
                        source_dispositions.append({
                            "source_path": str(source_path.relative_to(SUPPLEMENT)),
                            "source_sha256": digest,
                            "source_row_number": row_number,
                            "business_key": list(key),
                            "numeric_signature": [str(value) for value in signature],
                            "disposition": disposition,
                        })
                writer.writerows(records)
        elif broker_target.exists():
            # Existing supplied broker summaries must not silently contain duplicate keys.
            broker_bytes = broker_target.read_bytes()
            broker_sha256 = hashlib.sha256(broker_bytes).hexdigest()
            (raw_evidence / "original_broker_summary.csv").write_bytes(broker_bytes)
            raw_artifacts.append({
                "source_path": "original/broker_summary.csv",
                "evidence_path": "evidence/raw_inputs/original_broker_summary.csv",
                "sha256": broker_sha256,
                "size_bytes": len(broker_bytes),
            })
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
        validate_floorsheet_sessions(stage)
        stage.rename(output)
    print(f"Prepared {output} with {len(additions)} new daily price rows.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path, help="Existing data directory with daily_prices.csv")
    parser.add_argument("output", type=Path, help="A new output directory")
    args = parser.parse_args()
    prepare(args.original, args.output)
