"""Measure exact repeat-pair date-key coverage in the existing source-lineage register.

This audit exports missing keys with their pinned OHLCV source references. It does
not infer trading sessions, instrument identity, execution evidence, or corrections.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path

PAIR_FIELDS = (
    "path", "blob_sha", "symbol", "date", "row", "previous_date",
    "previous_row", "pair_classification",
)
LINEAGE_FIELDS = ("symbol", "date", "path", "blob_sha", "row")


def _day(value: str, label: str) -> str:
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError(f"{label} must be canonical YYYY-MM-DD: {value!r}")
    return value


def _read_unique(path: Path, fields: tuple[str, ...], key_fields: tuple[str, ...]):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = [field for field in fields if field not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"{path}: missing required fields {missing}")
        rows = list(reader)
    seen = {}
    for number, row in enumerate(rows, 2):
        key = tuple((row.get(field) or "").strip() for field in key_fields)
        if any(not part for part in key):
            raise ValueError(f"{path}: row {number} has empty key {key_fields}")
        if key in seen:
            raise ValueError(f"{path}: duplicate key {key!r} at rows {seen[key]} and {number}")
        seen[key] = number
    return rows


def audit(pair_path: Path, lineage_path: Path) -> dict:
    pairs = _read_unique(pair_path, PAIR_FIELDS, ("symbol", "date"))
    lineage = _read_unique(lineage_path, LINEAGE_FIELDS, ("symbol", "date"))

    lineage_keys = {
        ((row["symbol"] or "").strip(), _day(row["date"].strip(), "lineage date"))
        for row in lineage
    }
    pair_rows = []
    symbol_totals = Counter()
    symbol_covered = Counter()
    missing_rows = []

    for number, row in enumerate(pairs, 2):
        symbol = (row["symbol"] or "").strip()
        day = _day((row["date"] or "").strip(), f"pair row {number} date")
        _day((row["previous_date"] or "").strip(), f"pair row {number} previous_date")
        key = (symbol, day)
        covered = key in lineage_keys
        symbol_totals[symbol] += 1
        symbol_covered[symbol] += int(covered)
        record = {
            "symbol": symbol,
            "date": day,
            "path": (row["path"] or "").strip(),
            "blob_sha": (row["blob_sha"] or "").strip(),
            "row": (row["row"] or "").strip(),
            "previous_date": (row["previous_date"] or "").strip(),
            "previous_row": (row["previous_row"] or "").strip(),
            "pair_classification": (row["pair_classification"] or "").strip(),
            "lineage_covered": str(covered).lower(),
            "required_evidence": "effective-dated identity; authoritative session date; exact security-date execution evidence",
            "promotion_allowed": "false",
        }
        pair_rows.append(record)
        if not covered:
            missing_rows.append(record)

    symbol_states = Counter()
    symbol_report = []
    for symbol in sorted(symbol_totals):
        total = symbol_totals[symbol]
        covered = symbol_covered[symbol]
        state = "NO_LINEAGE" if covered == 0 else "FULL_LINEAGE" if covered == total else "PARTIAL_LINEAGE"
        symbol_states[state] += 1
        symbol_report.append({
            "symbol": symbol,
            "repeat_pair_keys": total,
            "lineage_matches": covered,
            "lineage_gaps": total - covered,
            "coverage_state": state,
        })

    return {
        "task": "P4.43 work package 18 exact repeat-pair date-lineage coverage audit",
        "pair_rows": len(pair_rows),
        "pair_symbols": len(symbol_totals),
        "lineage_keys": len(lineage_keys),
        "lineage_symbols": len({symbol for symbol, _ in lineage_keys}),
        "exact_intersection": len(pair_rows) - len(missing_rows),
        "uncovered_pair_keys": len(missing_rows),
        "lineage_keys_outside_pair_set": len(lineage_keys - {(r["symbol"], r["date"]) for r in pair_rows}),
        "symbol_coverage_states": dict(sorted(symbol_states.items())),
        "promotion_allowed": False,
        "canonical_data_modified": False,
        "interpretation": "Coverage gaps identify absent rows in this lineage register only; they do not establish missing trades, closed sessions, date shifts, or invalid OHLCV.",
        "limitations": [
            "Exact symbol/date matching only; no ticker aliases or successor inference.",
            "The lineage register is an evidence index, not proof of historical instrument identity.",
            "No trading-session status or execution record is inferred from absence.",
        ],
        "symbols": symbol_report,
        "missing_pair_rows": missing_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pairs", required=True, type=Path)
    parser.add_argument("--lineage", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    result = audit(args.pairs, args.lineage)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    fields = list(PAIR_FIELDS) + ["lineage_covered", "required_evidence", "promotion_allowed"]
    with (args.output_dir / "P443_REPEAT_PAIR_LINEAGE_GAPS_2026-11-27.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(result["missing_pair_rows"])
    (args.output_dir / "P443_REPEAT_PAIR_LINEAGE_COVERAGE_2026-11-27.json").write_text(
        json.dumps({key: value for key, value in result.items() if key not in {"symbols", "missing_pair_rows"}},
                   indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({key: result[key] for key in (
        "pair_rows", "pair_symbols", "lineage_keys", "lineage_symbols",
        "exact_intersection", "uncovered_pair_keys",
        "lineage_keys_outside_pair_set", "symbol_coverage_states",
    )}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
