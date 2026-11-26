#!/usr/bin/env python3
"""Read-only row-quality inventory for the 281-equity OHLCV archive.

Flags anomalies for review; it never edits source files or infers NO_TRADE.
"""
import argparse, csv, hashlib, math
from collections import Counter
from datetime import date
from pathlib import Path

NUMERIC = ("Open", "High", "Low", "Close", "Volume")

def parse_day(value):
    try:
        return date.fromisoformat((value or "").strip()[:10])
    except (TypeError, ValueError):
        return None

def number(value):
    try:
        result = float((value or "").replace(",", "").strip())
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None

def audit_file(symbol, root):
    path = Path(root) / f"{symbol}_OHLCV.csv"
    base = {"symbol": symbol, "file_status": "MISSING_FILE", "rows": 0,
            "sha256": "", "first_date": "", "last_date": "", "duplicate_dates": 0,
            "invalid_date_rows": 0, "invalid_numeric_rows": 0, "ohlc_invariant_rows": 0,
            "zero_volume_rows": 0, "negative_volume_rows": 0, "out_of_order_rows": 0,
            "exact_carry_forward_rows": 0, "classification": "MISSING_FILE_REVIEW"}
    if not path.is_file():
        return base
    raw = path.read_bytes()
    base["sha256"] = hashlib.sha256(raw).hexdigest()
    seen = Counter()
    dates, prev = [], None
    try:
        with path.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or not {"Date", *NUMERIC}.issubset(reader.fieldnames):
                base["file_status"] = "SCHEMA_FAIL"
                base["classification"] = "SCHEMA_REVIEW_REQUIRED"
                return base
            for row in reader:
                base["rows"] += 1
                day = parse_day(row.get("Date"))
                if day is None:
                    base["invalid_date_rows"] += 1
                    continue
                dates.append(day)
                seen[day] += 1
                vals = {k: number(row.get(k)) for k in NUMERIC}
                if any(v is None for v in vals.values()):
                    base["invalid_numeric_rows"] += 1
                    prev = (day, vals)
                    continue
                o,h,l,c,v = (vals[k] for k in NUMERIC)
                if h < max(o,l,c) or l > min(o,h,c) or min(o,h,l,c) <= 0:
                    base["ohlc_invariant_rows"] += 1
                if v == 0: base["zero_volume_rows"] += 1
                if v < 0: base["negative_volume_rows"] += 1
                if prev and day < prev[0]: base["out_of_order_rows"] += 1
                if prev and all(vals[k] == prev[1].get(k) for k in NUMERIC):
                    base["exact_carry_forward_rows"] += 1
                prev = (day, vals)
    except (UnicodeDecodeError, csv.Error):
        base["file_status"] = "READ_FAIL"
        base["classification"] = "READ_REVIEW_REQUIRED"
        return base
    base["file_status"] = "PRESENT"
    base["duplicate_dates"] = sum(n-1 for n in seen.values() if n > 1)
    if dates:
        base["first_date"], base["last_date"] = min(dates).isoformat(), max(dates).isoformat()
    flags = sum(base[k] for k in ("invalid_date_rows","invalid_numeric_rows","ohlc_invariant_rows","negative_volume_rows","out_of_order_rows","duplicate_dates"))
    base["classification"] = "REVIEW_FLAGS_PRESENT" if flags else "NO_BASIC_FLAGS_IN_THIS_CHECK"
    return base

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--universe",required=True); ap.add_argument("--ohlcv-dir",required=True)
    ap.add_argument("--expected-symbol-count",type=int,default=281)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()
    with open(a.universe,newline="",encoding="utf-8-sig") as f:
        rows=list(csv.DictReader(f))
    symbols=sorted({(r.get("symbol") or "").strip().upper() for r in rows if (r.get("symbol") or "").strip()})
    if len(symbols)!=a.expected_symbol_count:
        raise SystemExit(f"universe guard failed: expected {a.expected_symbol_count}, got {len(symbols)}")
    results=[audit_file(s,a.ohlcv_dir) for s in symbols]
    Path(a.output).parent.mkdir(parents=True,exist_ok=True)
    with open(a.output,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(results[0])); w.writeheader(); w.writerows(results)
    print(f"symbols={len(results)} files_present={sum(r['file_status']=='PRESENT' for r in results)} "
          f"missing={sum(r['file_status']=='MISSING_FILE' for r in results)} "
          f"flagged={sum(r['classification']=='REVIEW_FLAGS_PRESENT' for r in results)}")
if __name__=="__main__": main()
