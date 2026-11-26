#!/usr/bin/env python3
"""Compare NEPSE pipeline Parquet, SocrateAI full-session CSV, and local extract.

This is an audit-only tool: it downloads nothing, changes no canonical data, and
never upgrades a source status. It compares normalized executed-trade tuples.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

DEFAULT_DATE = "2026-11-20"


def dec(value: Any) -> Decimal:
    return Decimal(str(value).strip().replace(",", ""))


def amount(value: Any) -> Decimal:
    if isinstance(value, (int, float, Decimal)):
        return dec(value).quantize(Decimal("0.01"))
    s = str(value).strip().replace(",", "").upper().replace(" ", "")
    m = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)(K|LAC\.?|LAKH|L|CR\.?|CRORE)?", s)
    if not m:
        raise ValueError(f"unsupported amount: {value!r}")
    n = dec(m.group(1))
    suffix = (m.group(2) or "").rstrip(".")
    factor = {"": 1, "K": 1000, "L": 100000, "LAC": 100000,
              "LAKH": 100000, "CR": 10000000, "CRORE": 10000000}[suffix]
    return (n * factor).quantize(Decimal("0.01"))


def pick(row: dict[str, Any], *names: str) -> Any:
    for name in names:
        if name in row and row[name] not in (None, ""):
            return row[name]
    raise KeyError(f"missing all aliases {names}; got {sorted(row)}")


def norm_date(v: Any) -> str:
    return str(v).strip()[:10]


def norm_row(row: dict[str, Any], source: str) -> tuple:
    if source == "parquet":
        d = pick(row, "business_date")
        symbol = pick(row, "stock_symbol")
        buyer = pick(row, "buyer_member_id")
        seller = pick(row, "seller_member_id")
        qty = pick(row, "contract_quantity")
        rate = pick(row, "contract_rate")
        amt = pick(row, "contract_amount")
    else:
        d = pick(row, "date", "Trading_Date", "trading_date")
        symbol = pick(row, "symbol", "Symbol")
        buyer = pick(row, "buyer", "Buyer")
        seller = pick(row, "seller", "Seller")
        qty = pick(row, "quantity", "Quantity")
        rate = pick(row, "rate", "Rate")
        amt = pick(row, "amount", "Amount")
    return (
        norm_date(d),
        str(symbol).strip().upper(),
        str(int(dec(buyer))),
        str(int(dec(seller))),
        int(dec(qty)),
        dec(rate).quantize(Decimal("0.0001")),
        amount(amt),
    )


def read_csv(path: Path, label: str) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{label}: no CSV rows")
    return rows


def read_parquet(path: Path) -> list[dict[str, Any]]:
    try:
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise SystemExit("pyarrow is required: pip install pyarrow") from exc
    return pq.read_table(path).to_pylist()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def summarize(rows: list[dict[str, Any]], source: str) -> tuple[dict, Counter]:
    keys = Counter()
    symbols = Counter()
    symbol_shares = Counter()
    symbol_turnover = defaultdict(lambda: Decimal("0"))
    symbol_broker_pairs = defaultdict(Counter)
    unl_contracts = []
    shares = 0
    turnover = Decimal("0")
    dates = Counter()
    invalid = 0
    for row in rows:
        try:
            key = norm_row(row, source)
            keys[key] += 1
            dates[key[0]] += 1
            symbols[key[1]] += 1
            symbol_shares[key[1]] += key[4]
            symbol_turnover[key[1]] += key[6]
            symbol_broker_pairs[key[1]][(key[2], key[3])] += 1
            shares += key[4]
            turnover += key[6]
            if key[1] == "UNL":
                unl_contracts.append({
                    "date": key[0], "symbol": key[1], "buyer": key[2],
                    "seller": key[3], "quantity": key[4],
                    "rate": str(key[5]), "amount_npr": str(key[6])
                })
        except (KeyError, ValueError, InvalidOperation, TypeError):
            invalid += 1
    meta = {
        "rows": len(rows),
        "valid_rows": sum(keys.values()),
        "invalid_rows": invalid,
        "duplicate_normalized_trade_keys": sum(v - 1 for v in keys.values() if v > 1),
        "distinct_symbols": len(symbols),
        "shares": shares,
        "turnover_npr": str(turnover.quantize(Decimal("0.01"))),
        "date_counts": dict(sorted(dates.items())),
        "symbol_counts": dict(sorted(symbols.items())),
        "symbol_metrics": {
            sym: {
                "trades": symbols[sym],
                "shares": symbol_shares[sym],
                "turnover_npr": str(symbol_turnover[sym].quantize(Decimal("0.01"))),
                "top_buyer_seller_pairs": [
                    {"buyer": pair[0], "seller": pair[1], "trades": n}
                    for pair, n in symbol_broker_pairs[sym].most_common(5)
                ],
            }
            for sym in sorted(symbols)
        },
        "unl_contracts": unl_contracts,
        "sha256": None,
    }
    return meta, keys


def compare_core(left: Counter, right: Counter) -> dict:
    """Compare trade identity without amount, then quantify rounded amount drift."""
    l_by_core = defaultdict(list)
    r_by_core = defaultdict(list)
    for key, count in left.items():
        l_by_core[key[:-1]].extend([key[-1]] * count)
    for key, count in right.items():
        r_by_core[key[:-1]].extend([key[-1]] * count)
    matched = 0
    deltas = []
    left_only = 0
    right_only = 0
    for core in set(l_by_core) | set(r_by_core):
        la = sorted(l_by_core.get(core, []))
        ra = sorted(r_by_core.get(core, []))
        n = min(len(la), len(ra))
        matched += n
        deltas.extend(abs(la[i] - ra[i]) for i in range(n))
        left_only += max(len(la) - len(ra), 0)
        right_only += max(len(ra) - len(la), 0)
    bands = {"exact": 0, "le_1_npr": 0, "le_10_npr": 0, "le_100_npr": 0,
             "le_500_npr": 0, "le_50000_npr": 0, "gt_50000_npr": 0}
    for delta in deltas:
        if delta == 0:
            bands["exact"] += 1
        if delta <= Decimal("1"):
            bands["le_1_npr"] += 1
        if delta <= Decimal("10"):
            bands["le_10_npr"] += 1
        if delta <= Decimal("100"):
            bands["le_100_npr"] += 1
        if delta <= Decimal("500"):
            bands["le_500_npr"] += 1
        if delta <= Decimal("50000"):
            bands["le_50000_npr"] += 1
        else:
            bands["gt_50000_npr"] += 1
    return {
        "matched_trade_identity_rows_excluding_amount": matched,
        "left_only_trade_identity_rows": left_only,
        "right_only_trade_identity_rows": right_only,
        "max_amount_delta_npr": str(max(deltas, default=Decimal("0"))),
        "amount_delta_bands_npr": bands,
    }


def compare(left: Counter, right: Counter) -> dict:
    common = left & right
    left_only = left - right
    right_only = right - left
    return {
        "matched_trade_rows": sum(common.values()),
        "left_only_trade_rows": sum(left_only.values()),
        "right_only_trade_rows": sum(right_only.values()),
        "left_only_examples": [list(k) for k in list(left_only)[:10]],
        "right_only_examples": [list(k) for k in list(right_only)[:10]],
        "exact_multiset_match": not left_only and not right_only,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=DEFAULT_DATE)
    ap.add_argument("--parquet", type=Path, required=True)
    ap.add_argument("--candidate", type=Path, required=True)
    ap.add_argument("--local", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    audit_date = args.date

    datasets = {
        "independent_nepse_pipeline_parquet": (read_parquet(args.parquet), "parquet", args.parquet),
        "socrateai_full_session_csv": (read_csv(args.candidate, "candidate"), "csv", args.candidate),
    }
    if args.local:
        datasets["local_partial_extract"] = (read_csv(args.local, "local"), "csv", args.local)

    summaries = {}
    counters = {}
    for name, (rows, source, path) in datasets.items():
        meta, keys = summarize(rows, source)
        meta["sha256"] = sha256(path)
        summaries[name] = meta
        counters[name] = keys

    comparisons = {
        "pipeline_vs_socrateai": compare(
            counters["independent_nepse_pipeline_parquet"],
            counters["socrateai_full_session_csv"],
        )
    }
    gates = {
        "pipeline_and_candidate_same_date": (
            summaries["independent_nepse_pipeline_parquet"]["date_counts"]
            == {audit_date: summaries["independent_nepse_pipeline_parquet"]["rows"]}
            and summaries["socrateai_full_session_csv"]["date_counts"]
            == {audit_date: summaries["socrateai_full_session_csv"]["rows"]}
        ),
        "pipeline_candidate_equal_rows_and_symbols": (
            summaries["independent_nepse_pipeline_parquet"]["rows"]
            == summaries["socrateai_full_session_csv"]["rows"]
            and summaries["independent_nepse_pipeline_parquet"]["distinct_symbols"]
            == summaries["socrateai_full_session_csv"]["distinct_symbols"]
        ),
        "pipeline_candidate_exact_trade_multiset": (
            not (counters["independent_nepse_pipeline_parquet"] - counters["socrateai_full_session_csv"])
            and not (counters["socrateai_full_session_csv"] - counters["independent_nepse_pipeline_parquet"])
        ),
    }
    if args.local:
        local_key = "local_partial_extract"
        comparisons["pipeline_vs_local_partial"] = compare(
            counters["independent_nepse_pipeline_parquet"], counters[local_key]
        )
        comparisons["pipeline_vs_local_identity_without_amount"] = compare_core(
            counters["independent_nepse_pipeline_parquet"], counters[local_key]
        )
        comparisons["socrateai_vs_local_partial"] = compare(
            counters["socrateai_full_session_csv"], counters[local_key]
        )
        comparisons["socrateai_vs_local_identity_without_amount"] = compare_core(
            counters["socrateai_full_session_csv"], counters[local_key]
        )
        gates["local_extract_is_full_session"] = (
            summaries[local_key]["rows"] == summaries["independent_nepse_pipeline_parquet"]["rows"]
        )

    report = {
        "audit_date": audit_date,
        "classification": "AUDIT_ONLY_NOT_CANONICAL",
        "sources": summaries,
        "comparisons": comparisons,
        "gates": gates,
        "limitations": [
            "This job compares the published Parquet bytes and CSV records; capture logs must be separately checked for upstream totalElements and complete pagination.",
            "A matching published partition does not replace missing private bronze raw-page replay evidence.",
            "This audit does not promote canonical data or authorize NO_TRADE inference.",
            "Only 2026-11-20 currently has separately verified upstream totalElements, full-page capture and quality-gate logs in the project evidence register.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, default=str))
    if any(meta["invalid_rows"] for meta in summaries.values()):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
