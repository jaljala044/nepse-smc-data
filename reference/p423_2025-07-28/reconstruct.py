#!/usr/bin/env python3
"""Reconstruct candidate OHLCV evidence from a date-scoped NEPSE floorsheet JSON."""
from __future__ import annotations
import argparse, csv, hashlib, json
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

DATE = "2025-07-28"
EXPECTED_SHA256 = "4b37929a86d1f2a3f09526afc874186dd716e90eec2736904ef5ec37d4dd71e0"
COLUMNS = ["contractId", "stockId", "buyer", "seller", "qty", "rate", "amount", "time"]
UNKNOWN = "UNKNOWN"

def dec(value):
    if value is None or isinstance(value, bool):
        raise ValueError("not numeric")
    return value if isinstance(value, Decimal) else Decimal(str(value))

def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def aggregate_transactions(transactions, lookup, target_symbols):
    """Return aggregates and exhaustive row-level anomaly counters.

    Rows are never silently ignored: malformed/invalid rows and duplicate IDs are
    recorded in audit. Any affected target symbol is marked incomplete.
    """
    by_id = {str(k): v.get("symbol") for k, v in lookup.items()}
    grouped = defaultdict(list)
    audit = {"rows_seen": len(transactions), "malformed_rows": [], "invalid_rows": [],
             "bad_date_rows": [], "duplicate_contract_ids": [], "duplicate_rows": [],
             "unknown_stock_ids": set(), "null_field_values": 0}
    seen_ids, seen_rows = set(), set()
    incomplete = set()
    for idx, row in enumerate(transactions):
        if not isinstance(row, list) or len(row) != 8:
            audit["malformed_rows"].append(idx)
            continue
        cid, sid, buyer, seller, qty, rate, amount, time = row
        symbol = by_id.get(str(sid))
        if any(x is None for x in row):
            audit["null_field_values"] += 1
            if symbol in target_symbols: incomplete.add(symbol)
        if not str(cid).startswith(DATE.replace("-", "")):
            audit["bad_date_rows"].append(idx)
            if symbol in target_symbols: incomplete.add(symbol)
        if str(cid) in seen_ids:
            audit["duplicate_contract_ids"].append({"row": idx, "contractId": str(cid)})
            if symbol in target_symbols: incomplete.add(symbol)
        seen_ids.add(str(cid))
        key = json.dumps(row, separators=(",", ":"), default=str)
        if key in seen_rows:
            audit["duplicate_rows"].append(idx)
            if symbol in target_symbols: incomplete.add(symbol)
        seen_rows.add(key)
        if symbol is None:
            audit["unknown_stock_ids"].add(str(sid))
            continue
        try:
            q, rate_d, amount_d = dec(qty), dec(rate), dec(amount)
            if q <= 0 or rate_d <= 0 or amount_d < 0:
                raise ValueError("qty/rate must be positive and amount non-negative")
        except (ValueError, InvalidOperation):
            audit["invalid_rows"].append(idx)
            if symbol in target_symbols: incomplete.add(symbol)
            continue
        if symbol in target_symbols:
            grouped[symbol].append({"contractId": str(cid), "qty": q, "rate": rate_d,
                                    "amount": amount_d, "time": "" if time is None else str(time)})
    result = {}
    for symbol in target_symbols:
        trades = grouped.get(symbol, [])
        if not trades or symbol in incomplete:
            result[symbol] = {"trade_count": len(trades), "open": UNKNOWN, "high": UNKNOWN,
                              "low": UNKNOWN, "close": UNKNOWN, "volume": UNKNOWN,
                              "turnover": UNKNOWN, "incomplete": symbol in incomplete}
            continue
        times = [t["time"] for t in trades]
        ordered = False
        if all(times) and len(set(times)) == len(times):
            # Lexical ordering is safe only for normalized HH:MM:SS strings.
            import re
            ordered = all(re.fullmatch(r"\d{2}:\d{2}:\d{2}", x) for x in times)
        if ordered:
            trades = sorted(trades, key=lambda t: t["time"])
            opn, close = trades[0]["rate"], trades[-1]["rate"]
        else:
            opn = close = UNKNOWN
        result[symbol] = {"trade_count": len(trades), "open": opn,
                          "high": max(t["rate"] for t in trades),
                          "low": min(t["rate"] for t in trades), "close": close,
                          "volume": sum((t["qty"] for t in trades), Decimal(0)),
                          "turnover": sum((t["amount"] for t in trades), Decimal(0)),
                          "incomplete": False}
    audit["unknown_stock_ids"] = sorted(audit["unknown_stock_ids"])
    return result, audit

def jsonable(value):
    if isinstance(value, Decimal): return format(value, "f")
    if isinstance(value, dict): return {k: jsonable(v) for k, v in value.items()}
    if isinstance(value, list): return [jsonable(v) for v in value]
    return value

def status(a, b):
    if a == UNKNOWN or b in (None, "", UNKNOWN): return "UNKNOWN"
    return "EXACT_MATCH" if dec(a) == dec(b) else "MISMATCH"

def run(archive_path, lookup_path, canonical_path, external_path, out_dir):
    raw = Path(archive_path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError(f"archive SHA-256 mismatch: {digest}")
    archive = json.loads(raw, parse_float=Decimal)
    if archive.get("date") != DATE or archive.get("columns") != COLUMNS:
        raise ValueError("unexpected archive date or schema")
    lookup = json.loads(Path(lookup_path).read_text(encoding="utf-8"))
    canonical = {r["symbol"]: r for r in load_csv(canonical_path)}
    external_rows = load_csv(external_path)
    symbols = [r["symbol"] for r in external_rows]
    if len(symbols) != 86 or len(set(symbols)) != 86:
        raise ValueError("expected exactly 86 unique target symbols")
    agg, audit = aggregate_transactions(archive["transactions"], lookup, symbols)
    rows = []
    for ext in external_rows:
        sym = ext["symbol"]; a = agg[sym]; can = canonical.get(sym, {})
        row = {"date": DATE, "symbol": sym, "stock_id": UNKNOWN, **a,
               "canonical": {k: can.get(k, UNKNOWN) for k in ("open","high","low","close","volume")},
               "external": {k: ext.get("external_"+k, UNKNOWN) for k in ("open","high","low","close","volume","turnover")}}
        if sym in lookup_symbols(lookup): row["stock_id"] = next(k for k,v in lookup.items() if v.get("symbol")==sym)
        row["comparison"] = {
            "open_vs_canonical": "UNKNOWN_TIME_MISSING", "open_vs_external": "UNKNOWN_TIME_MISSING",
            "high_vs_canonical": status(a["high"], can.get("high", UNKNOWN)),
            "high_vs_external": status(a["high"], ext.get("external_high", UNKNOWN)),
            "low_vs_canonical": status(a["low"], can.get("low", UNKNOWN)),
            "low_vs_external": status(a["low"], ext.get("external_low", UNKNOWN)),
            "close_vs_canonical": "UNKNOWN_TIME_MISSING", "close_vs_external": "UNKNOWN_TIME_MISSING",
            "volume_vs_canonical": status(a["volume"], can.get("volume", UNKNOWN)),
            "volume_vs_external": status(a["volume"], ext.get("external_volume", UNKNOWN)),
            "turnover_vs_canonical": "UNAVAILABLE",
            "turnover_vs_external": status(a["turnover"], ext.get("external_turnover", UNKNOWN))}
        row["disposition"] = "CONFLICT_UNRESOLVED_PRIMARY_PENDING"
        rows.append(row)
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    payload = {"task":"P4.23.2","date":DATE,"source_sha256":digest,
               "archive_bytes":len(raw),"archive_rows":len(archive["transactions"]),
               "declared_trades":archive.get("totalTrades"),"declared_qty":archive.get("totalQty"),
               "declared_turnover":archive.get("totalAmount"),"audit":audit,"symbols":rows}
    (out_dir/"results.json").write_text(json.dumps(jsonable(payload), indent=2)+"\n", encoding="utf-8")
    fields = ["date","symbol","stock_id","trade_count","open","high","low","close","volume","turnover",
              "disposition"]
    with open(out_dir/"results.csv","w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in rows:
            w.writerow({k: (format(r[k],"f") if isinstance(r.get(k),Decimal) else r.get(k,UNKNOWN)) for k in fields})
    return payload

def lookup_symbols(lookup):
    return {v.get("symbol") for v in lookup.values()}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True);p.add_argument("--lookup",required=True)
    p.add_argument("--canonical",required=True);p.add_argument("--external",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    result=run(a.archive,a.lookup,a.canonical,a.external,a.out)
    print(f"wrote {len(result['symbols'])} symbols; SHA-256 verified; audit={result['audit']}")

if __name__=="__main__": main()
