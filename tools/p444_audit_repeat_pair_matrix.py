"""Read-back audit for the P4.44 23,377-pair evidence artifact.

Validates row lineage, date order, identity scope, execution-evidence bundle
completeness, and fail-closed dispositions. This is read-only.
"""
import argparse
import csv
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path

BLOB_RE = re.compile(r"^[0-9a-f]{40}$")
SCOPES = {"historical_effective_dated_id", "current_snapshot_only", "unresolved"}
EXECUTION_FIELDS = (
    "execution_sources", "execution_security_ids", "execution_trade_counts",
    "execution_quantities", "execution_values", "execution_retrieved_at",
)
BASE_REQUIRED = {
    "pair_id", "symbol", "previous_date", "current_date", "source_path",
    "source_blob_sha", "previous_source_row", "current_source_row",
    "source_pair_tuple_equal", "identity_scope", "historical_stable_id",
    "current_snapshot_security_id", "previous_session_status",
    "current_session_status", "disposition", "promotion_allowed",
}
REQUIRED = BASE_REQUIRED | {
    f"{side}_{field}"
    for side in ("previous", "current")
    for field in EXECUTION_FIELDS
}


def _positive_row_number(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return False
    return number > 0 and str(number) == str(value).strip()


def audit(path, expected_pairs=23377, expected_symbols=209):
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        columns = set(reader.fieldnames or [])
        missing = sorted(REQUIRED - columns)
        rows = list(reader)

    issues = []
    if missing:
        issues.append({"code": "MISSING_COLUMNS", "columns": missing})

    symbols = set()
    pair_ids = set()
    counts = Counter()
    dates = []
    for n, row in enumerate(rows, 2):
        symbol = (row.get("symbol") or "").strip()
        pair_id = (row.get("pair_id") or "").strip()
        if not symbol:
            issues.append({"row": n, "code": "MISSING_SYMBOL"})
        symbols.add(symbol)
        if not pair_id:
            issues.append({"row": n, "code": "MISSING_PAIR_ID"})
        elif pair_id in pair_ids:
            issues.append({"row": n, "code": "DUPLICATE_PAIR_ID", "pair_id": pair_id})
        pair_ids.add(pair_id)

        if not (row.get("source_path") or "").strip():
            issues.append({"row": n, "code": "MISSING_SOURCE_PATH"})
        if not BLOB_RE.fullmatch(row.get("source_blob_sha", "")):
            issues.append({"row": n, "code": "INVALID_SOURCE_BLOB_SHA"})
        for field in ("previous_source_row", "current_source_row"):
            if not _positive_row_number(row.get(field, "")):
                issues.append({"row": n, "code": "INVALID_SOURCE_ROW_NUMBER", "field": field})

        try:
            previous = date.fromisoformat(row["previous_date"])
            current = date.fromisoformat(row["current_date"])
            if previous.isoformat() != row["previous_date"] or current.isoformat() != row["current_date"]:
                raise ValueError("non-canonical date")
            dates.extend((previous.isoformat(), current.isoformat()))
            if previous >= current:
                issues.append({"row": n, "code": "NON_INCREASING_PAIR_DATES"})
        except (ValueError, KeyError, TypeError):
            issues.append({"row": n, "code": "INVALID_PAIR_DATE"})

        if row.get("source_pair_tuple_equal") != "true":
            issues.append({"row": n, "code": "SOURCE_TUPLE_NOT_VERIFIED"})

        scope = row.get("identity_scope", "")
        historical_id = (row.get("historical_stable_id") or "").strip()
        current_id = (row.get("current_snapshot_security_id") or "").strip()
        if scope not in SCOPES:
            issues.append({"row": n, "code": "INVALID_IDENTITY_SCOPE", "value": scope})
        if scope == "historical_effective_dated_id" and not historical_id:
            issues.append({"row": n, "code": "HISTORICAL_ID_MISSING"})
        if scope != "historical_effective_dated_id" and historical_id:
            issues.append({"row": n, "code": "UNVERIFIED_HISTORICAL_ID_PRESENT"})
        if scope == "unresolved" and current_id:
            issues.append({"row": n, "code": "UNRESOLVED_SCOPE_HAS_CURRENT_ID"})
        if scope == "current_snapshot_only" and not current_id:
            issues.append({"row": n, "code": "CURRENT_SNAPSHOT_ID_MISSING"})
        counts["identity_" + scope] += 1

        for side in ("previous", "current"):
            evidence = [((row.get(f"{side}_{field}") or "").strip()) for field in EXECUTION_FIELDS]
            if any(evidence) and not all(evidence):
                issues.append({"row": n, "code": "PARTIAL_EXECUTION_EVIDENCE_BUNDLE", "side": side})
            if all(evidence):
                counts[f"{side}_execution_evidence_present"] += 1
            else:
                counts[f"{side}_execution_evidence_absent"] += 1
            counts[f"{side}_session_" + (row.get(f"{side}_session_status") or "missing")] += 1

        if row.get("disposition") != "HOLD_UNKNOWN_NO_INFERENCE":
            issues.append({"row": n, "code": "NON_HOLD_DISPOSITION"})
        if row.get("promotion_allowed") != "false":
            issues.append({"row": n, "code": "PROMOTION_NOT_FALSE"})

    if len(rows) != expected_pairs:
        issues.append({"code": "PAIR_COUNT_MISMATCH", "actual": len(rows), "expected": expected_pairs})
    if len(symbols) != expected_symbols:
        issues.append({"code": "SYMBOL_COUNT_MISMATCH", "actual": len(symbols), "expected": expected_symbols})

    return {
        "rows": len(rows),
        "symbols": len(symbols),
        "unique_pair_ids": len(pair_ids),
        "date_min": min(dates) if dates else None,
        "date_max": max(dates) if dates else None,
        "counts": dict(sorted(counts.items())),
        "issues": issues,
        "valid": not issues,
        "promotion_allowed": False,
        "canonical_data_modified": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("matrix")
    parser.add_argument("--expected-pairs", type=int, default=23377)
    parser.add_argument("--expected-symbols", type=int, default=209)
    parser.add_argument("--summary-output")
    args = parser.parse_args()
    result = audit(args.matrix, args.expected_pairs, args.expected_symbols)
    if args.summary_output:
        Path(args.summary_output).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
