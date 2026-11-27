"""Independent structural and aggregate audit of recovered daily EOD CSVs.

This checks pinned source identity, CSV structure, per-security symbol uniqueness,
serial continuity and aggregate reconciliation. It does NOT prove underlying
floorsheet completeness or independently authenticate the transaction count.
"""
import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from decimal import Decimal
from pathlib import Path

SOURCE_COMMIT = "524442d518d2f2705ade0680c9d2e3f90738e3d6"
INVENTORY = Path("reference/P443_SESSION_CONTROL_SECONDARY_SOURCE_INVENTORY.csv")
BASELINE = Path("scanner_inputs/market_summary_daily.csv")
RECOVERY = "session_recovery.csv"
REQUIRED = {"S.No", "Symbol", "Vol", "Turnover", "Trans."}


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def parse_number(value, integral=False):
    value = (value or "").strip()
    if not re.fullmatch(r"(?:[0-9]+|[0-9]{1,3}(?:,[0-9]{3})+)(?:\\.[0-9]+)?", value):
        raise ValueError("invalid numeric field")
    number = Decimal(value.replace(",", ""))
    if not number.is_finite() or number < 0:
        raise ValueError("negative or non-finite numeric field")
    if integral and number != number.to_integral_value():
        raise ValueError("non-integral count field")
    return number


def audit_file(source, item, expected, recovery):
    path = item["path"]
    if path != "docs/Data/" + item["date"].replace("-", "_") + ".csv":
        raise ValueError("unexpected source path")
    raw = subprocess.check_output(
        ["git", "-C", str(source), "show", SOURCE_COMMIT + ":" + path]
    )
    git_blob = hashlib.sha1(f"blob {len(raw)}\\0".encode() + raw).hexdigest()
    if len(raw) != int(item["bytes"]) or git_blob != item["git_blob_sha"]:
        raise ValueError("pinned source byte-size or Git blob SHA mismatch")

    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(text.splitlines())
    headers = reader.fieldnames or []
    if len(headers) != len(set(headers)) or not REQUIRED.issubset(headers):
        raise ValueError("missing or duplicate CSV headers")

    symbols = []
    quantity = Decimal(0)
    turnover = Decimal(0)
    transactions = Decimal(0)
    serials = []
    row_count = 0
    for row in reader:
        if None in row or any(row.get(key) is None for key in REQUIRED):
            raise ValueError("malformed row width or missing required value")
        symbol = (row.get("Symbol") or "").strip().upper()
        if not symbol:
            raise ValueError("blank symbol")
        symbols.append(symbol)
        serials.append(int(parse_number(row["S.No"], integral=True)))
        quantity += parse_number(row["Vol"], integral=True)
        turnover += parse_number(row["Turnover"])
        transactions += parse_number(row["Trans."], integral=True)
        row_count += 1

    if not row_count or len(set(symbols)) != row_count:
        raise ValueError("empty file or duplicate symbol")
    if serials != list(range(1, row_count + 1)):
        raise ValueError("S.No sequence is not contiguous from 1")

    expected_symbols = int(expected["traded_securities"])
    expected_quantity = int(expected["traded_shares"])
    expected_turnover = Decimal(expected["turnover_npr"])
    baseline_match = (
        row_count == expected_symbols
        and quantity == expected_quantity
        and turnover == expected_turnover
    )
    recovered_match = (
        str(int(transactions)) == recovery["transactions"]
        and recovery["symbols"] == str(row_count)
        and recovery["quantity"] == str(int(quantity))
        and Decimal(recovery["turnover"]) == turnover
    )
    if not recovered_match:
        raise ValueError("independent totals differ from recovery artifact")

    return {
        "date": item["date"],
        "source_path": path,
        "source_blob_expected": item["git_blob_sha"],
        "source_blob_recomputed": git_blob,
        "source_bytes_expected": int(item["bytes"]),
        "source_bytes_actual": len(raw),
        "rows": row_count,
        "unique_symbols": len(set(symbols)),
        "duplicate_symbols": 0,
        "serial_sequence_contiguous": True,
        "quantity": str(int(quantity)),
        "turnover_npr": str(turnover),
        "transactions": str(int(transactions)),
        "baseline_symbols_volume_turnover_match": baseline_match,
        "independent_recovery_totals_match": recovered_match,
        "recovery_status": recovery["status"],
        "publication_allowed": recovery["publication_allowed"],
        "status": "PASS_AGGREGATE_AND_STRUCTURE" if baseline_match else "SOURCE_INTEGRITY_OK_BASELINE_CONFLICT",
    }


def main(source, output):
    inventory = read_csv(INVENTORY)
    baseline_rows = read_csv(BASELINE)
    recovery_rows = read_csv(output / RECOVERY)
    baseline = {row["date"]: row for row in baseline_rows}
    recovery = {row["date"]: row for row in recovery_rows}
    if len(inventory) != 149 or len({x["date"] for x in inventory}) != 149:
        raise ValueError("unexpected source inventory scope")
    if len(baseline) != len(baseline_rows) or len(recovery) != 149:
        raise ValueError("duplicate or missing date in baseline/recovery")

    results = []
    errors = []
    for item in inventory:
        day = item["date"]
        try:
            result = audit_file(source, item, baseline[day], recovery[day])
            if result["publication_allowed"] != "false":
                raise ValueError("publication gate unexpectedly enabled")
            if day == "2026-03-01":
                if result["baseline_symbols_volume_turnover_match"]:
                    raise ValueError("expected March 1 conflict disappeared")
            elif not result["baseline_symbols_volume_turnover_match"]:
                raise ValueError("unexpected baseline conflict")
            results.append(result)
        except Exception as exc:
            errors.append({"date": day, "error": str(exc)})

    counts = Counter(x["status"] for x in results)
    summary = {
        "source_commit": SOURCE_COMMIT,
        "inventory_rows": len(inventory),
        "audited_rows": len(results),
        "error_rows": len(errors),
        "counts": dict(counts),
        "independent_totals_match_rows": sum(x["independent_recovery_totals_match"] for x in results),
        "publication_allowed_rows": sum(x["publication_allowed"] == "true" for x in results),
        "limitations": [
            "Per-security daily EOD CSV structural/aggregate checks only.",
            "No underlying floor-sheet trade rows or independent transaction-count benchmark were checked.",
            "Matching symbols, volume and turnover does not prove that the source session file is complete.",
            "No official approval, date shift, canonical modification or promotion is authorized."
        ],
    }
    output.mkdir(parents=True, exist_ok=True)
    with (output / "independent_source_audit.csv").open("w", encoding="utf-8", newline="") as stream:
        fields = list(results[0]) if results else ["date", "status"]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)
    (output / "independent_source_audit.json").write_text(json.dumps({"summary": summary, "errors": errors}, indent=2))
    print(json.dumps(summary, indent=2))
    if errors or len(results) != 149 or counts != {
        "PASS_AGGREGATE_AND_STRUCTURE": 148,
        "SOURCE_INTEGRITY_OK_BASELINE_CONFLICT": 1,
    }:
        raise SystemExit("independent source audit did not meet expected held-candidate profile")


if __name__ == "__main__":
    import sys
    main(Path(sys.argv[1]), Path(sys.argv[2]))
