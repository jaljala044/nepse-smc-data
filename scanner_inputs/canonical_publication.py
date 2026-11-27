"""Validate a new daily trade archive before exclusive publication.

This is a quarantine and integrity gate, not a source-rights or completeness certification.
"""
import csv
import io
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import date
from .historical_quarantine import load_holds
from .prepare_scanner_inputs import validate_floorsheet, verified_closed_dates


def publish_daily_floorsheet(raw, day, destination, overlay):
    if date.fromisoformat(day).isoformat() != day:
        raise ValueError("Invalid archive session")
    holds = load_holds(overlay)
    closed = verified_closed_dates()
    destination = Path(destination)
    if destination.name != f"floorsheet_{day}.csv" or destination.is_symlink():
        raise ValueError("Invalid archive destination")
    if destination.parent.is_symlink() or not destination.parent.is_dir():
        raise ValueError("Invalid archive directory")
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    fields = reader.fieldnames or []
    required = {"Contract_No", "Symbol", "Buyer", "Seller", "Quantity", "Rate", "Amount"}
    if len(set(fields)) != len(fields) or not required.issubset(fields) or "date" in fields:
        raise ValueError("Unexpected raw archive schema")
    with TemporaryDirectory(dir=destination.parent) as temp:
        original = Path(temp) / "original.csv"
        original.write_bytes(raw)
        normalized = Path(temp) / "normalized.csv"
        with normalized.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=[*fields, "date"])
            writer.writeheader()
            for row in reader:
                if None in row or any(v is None for v in row.values()):
                    raise ValueError("Malformed raw trade row")
                contract = row["Contract_No"].strip()
                if not contract.isascii() or not contract.isdecimal() or not contract.startswith(day.replace("-", "")):
                    raise ValueError("Contract session not established")
                writer.writerow(dict(row, date=day))
        validate_floorsheet(normalized, closed, holds)
        if destination.exists():
            if destination.read_bytes() == raw:
                return "unchanged"
            raise FileExistsError("Existing raw archive differs; overwrite prohibited")
        # Atomic exclusive hard link on the same filesystem; never replace.
        os.link(original, destination)
    return "published"
