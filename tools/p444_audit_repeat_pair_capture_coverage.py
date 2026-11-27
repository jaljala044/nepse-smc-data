"""Exact-symbol/date coverage audit between the P4.44 repeat matrix and NEPSE history captures.

This is a read-only coverage check. It never aliases predecessor/successor tickers,
infers identity, or promotes a repeated OHLCV pair.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

REQUIRED_MATRIX_FIELDS = ("pair_id", "symbol", "previous_date", "current_date")
REQUIRED_HISTORY_FIELDS = (
    "businessDate", "totalTrades", "totalTradedQuantity", "totalTradedValue"
)


def _iso_day(value: str, label: str) -> str:
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError(f"{label} must be canonical YYYY-MM-DD: {value!r}")
    return value


def audit(matrix_path: Path, symbols_root: Path) -> dict:
    matrix_path = Path(matrix_path)
    symbols_root = Path(symbols_root)
    with matrix_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = [field for field in REQUIRED_MATRIX_FIELDS if field not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"matrix missing required fields: {missing}")
        pairs = list(reader)

    pair_symbols: dict[str, list[dict]] = defaultdict(list)
    for row_number, row in enumerate(pairs, 2):
        symbol = (row.get("symbol") or "").strip()
        if not symbol:
            raise ValueError(f"matrix row {row_number} has empty symbol")
        previous = _iso_day(row["previous_date"], f"row {row_number} previous_date")
        current = _iso_day(row["current_date"], f"row {row_number} current_date")
        pair_symbols[symbol].append({
            "pair_id": row["pair_id"],
            "previous_date": previous,
            "current_date": current,
        })

    capture_paths = sorted(symbols_root.glob("*/response-01.bin"))
    capture_symbols: dict[str, dict] = {}
    for path in capture_paths:
        symbol = path.parent.name
        if symbol in capture_symbols:
            raise ValueError(f"duplicate capture payload for exact symbol {symbol}")
        document = json.loads(path.read_text(encoding="utf-8"))
        rows = document.get("content") if isinstance(document, dict) else None
        if not isinstance(rows, list):
            raise ValueError(f"{symbol}: response content must be an array")
        by_date: dict[str, dict] = {}
        for index, item in enumerate(rows):
            if not isinstance(item, dict):
                raise ValueError(f"{symbol}: row {index} must be an object")
            missing_fields = [field for field in REQUIRED_HISTORY_FIELDS if field not in item]
            if missing_fields:
                raise ValueError(f"{symbol}: row {index} missing fields {missing_fields}")
            day = _iso_day(item["businessDate"], f"{symbol} row {index} businessDate")
            if day in by_date:
                raise ValueError(f"{symbol}: duplicate businessDate {day}")
            by_date[day] = item
        capture_symbols[symbol] = by_date

    matched_symbols = sorted(set(pair_symbols) & set(capture_symbols))
    symbol_reports = []
    covered_endpoint_occurrences = 0
    total_endpoint_occurrences = 2 * len(pairs)
    covered_unique_endpoints = 0
    total_unique_endpoints = 0
    covered_pairs_both_endpoints = 0

    for symbol in sorted(pair_symbols):
        symbol_pairs = pair_symbols[symbol]
        dates = {
            day
            for pair in symbol_pairs
            for day in (pair["previous_date"], pair["current_date"])
        }
        total_unique_endpoints += len(dates)
        payload = capture_symbols.get(symbol)
        if payload is None:
            symbol_reports.append({
                "symbol": symbol,
                "pair_rows": len(symbol_pairs),
                "exact_symbol_capture_match": False,
                "capture_date_min": None,
                "capture_date_max": None,
                "unique_endpoint_dates": len(dates),
                "covered_unique_endpoint_dates": 0,
                "covered_endpoint_occurrences": 0,
                "pairs_with_both_endpoints_covered": 0,
                "disposition": "NO_EXACT_SYMBOL_CAPTURE; no alias inference",
            })
            continue

        covered_dates = dates & set(payload)
        covered_unique_endpoints += len(covered_dates)
        occurrence_hits = 0
        both_hits = 0
        for pair in symbol_pairs:
            prev_hit = pair["previous_date"] in payload
            curr_hit = pair["current_date"] in payload
            occurrence_hits += int(prev_hit) + int(curr_hit)
            both_hits += int(prev_hit and curr_hit)
        covered_endpoint_occurrences += occurrence_hits
        covered_pairs_both_endpoints += both_hits
        symbol_reports.append({
            "symbol": symbol,
            "pair_rows": len(symbol_pairs),
            "exact_symbol_capture_match": True,
            "capture_date_min": min(payload) if payload else None,
            "capture_date_max": max(payload) if payload else None,
            "unique_endpoint_dates": len(dates),
            "covered_unique_endpoint_dates": len(covered_dates),
            "covered_endpoint_occurrences": occurrence_hits,
            "pairs_with_both_endpoints_covered": both_hits,
            "positive_trade_endpoint_rows": sum(
                1 for day in covered_dates if payload[day]["totalTrades"] > 0
            ),
            "disposition": "DATE_COVERAGE_ONLY; execution evidence requires exact endpoint hits",
        })

    return {
        "task": "P4.44 repeat-pair endpoint coverage against pinned per-security history capture",
        "matrix_path": str(matrix_path),
        "matrix_pair_rows": len(pairs),
        "matrix_symbols": len(pair_symbols),
        "capture_symbols": len(capture_symbols),
        "exact_symbol_intersection_count": len(matched_symbols),
        "exact_symbol_intersection": matched_symbols,
        "endpoint_occurrences_total": total_endpoint_occurrences,
        "endpoint_occurrences_covered": covered_endpoint_occurrences,
        "unique_endpoint_dates_total": total_unique_endpoints,
        "unique_endpoint_dates_covered": covered_unique_endpoints,
        "pairs_with_both_endpoints_covered": covered_pairs_both_endpoints,
        "promotion_allowed": False,
        "canonical_data_modified": False,
        "identity_policy": "Exact symbol only. No predecessor/successor or ticker-similarity alias is inferred.",
        "limitations": [
            "The capture is limited to its recorded date window and cannot cover older endpoints.",
            "An exact current symbol match does not prove historical security-ID continuity.",
            "The capture is not assumed complete for exchange sessions.",
            "Missing endpoint rows are not evidence of no trade.",
        ],
        "symbol_reports": symbol_reports,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", required=True, type=Path)
    parser.add_argument("--symbols-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = audit(args.matrix, args.symbols_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in (
        "matrix_pair_rows", "matrix_symbols", "capture_symbols",
        "exact_symbol_intersection_count", "exact_symbol_intersection",
        "endpoint_occurrences_total", "endpoint_occurrences_covered",
        "unique_endpoint_dates_total", "unique_endpoint_dates_covered",
        "pairs_with_both_endpoints_covered",
    )}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
