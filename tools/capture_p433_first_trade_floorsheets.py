#!/usr/bin/env python3
"""Capture four date-scoped third-party floorsheets for P4.33; fail closed on gaps."""
import csv
import hashlib
import io
import json
import urllib.request
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

BASE = "https://huggingface.co/datasets/urekmazino69/Nepse-floorsheet-and-indices/resolve/main/floorsheet"
TARGETS = [
    {"symbol":"NMLBBL","date":"2024-05-19","role":"candidate_first_positive_volume_date"},
    {"symbol":"NMLBBL","date":"2024-05-16","role":"immediately_preceding_candidate_session"},
    {"symbol":"SMPDA","date":"2024-08-18","role":"candidate_first_positive_volume_date"},
    {"symbol":"SMPDA","date":"2024-08-14","role":"immediately_preceding_candidate_session"},
]
ALIASES = {
    "contract_no":("contract_no","contractno","contract_id","contractid"),
    "date":("calculation_date","business_date","businessdate","date"),
    "symbol":("stock_symbol","symbol","scrip"),
    "quantity":("quantity","qty"),
    "rate":("rate","price"),
    "amount":("amount","amt","total_amount"),
}

def pick(row, key):
    for name in ALIASES[key]:
        if name in row and str(row[name]).strip():
            return str(row[name]).strip()
    return ""

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"NEPSE-P433-Evidence-Audit/1.0"})
    with urllib.request.urlopen(req,timeout=45) as res:
        return res.status,dict(res.headers.items()),res.read()

def validate_rows(raw, symbol, date):
    text=raw.decode("utf-8-sig")
    reader=csv.DictReader(io.StringIO(text))
    headers=[(h or "").strip().lower() for h in (reader.fieldnames or [])]
    if not headers:
        return {"status":"schema_unknown","row_count":0,"errors":["CSV has no header"],"symbol_contracts":0}
    rows=[{(k or "").strip().lower():(v or "").strip() for k,v in row.items()} for row in reader]
    errors=[]
    missing=[k for k in ("contract_no","date","symbol","quantity","rate","amount") if not any(a in headers for a in ALIASES[k])]
    if missing: errors.append("missing required column(s): "+",".join(missing))
    ids=[]; target_rows=[]; arithmetic_errors=0; date_mismatches=0; invalid_numeric=0
    for i,row in enumerate(rows,2):
        cid=pick(row,"contract_no")
        if not cid: errors.append(f"row {i}: missing contract id")
        ids.append(cid)
        rowdate=pick(row,"date")[:10]
        if rowdate and rowdate!=date: date_mismatches+=1
        rowsymbol=pick(row,"symbol").upper()
        if rowsymbol==symbol: target_rows.append(row)
        if not all(pick(row,k) for k in ("quantity","rate","amount")): invalid_numeric+=1; continue
        try:
            qty=Decimal(pick(row,"quantity").replace(",",""))
            rate=Decimal(pick(row,"rate").replace(",",""))
            amount=Decimal(pick(row,"amount").replace(",",""))
            if qty<=0 or rate<=0 or amount<=0: invalid_numeric+=1
            elif abs(qty*rate-amount)>Decimal("0.01") and amount!= (qty*rate).to_integral_value(rounding="ROUND_FLOOR"):
                arithmetic_errors+=1
        except (InvalidOperation,ValueError): invalid_numeric+=1
    duplicate_ids=len(ids)-len(set(ids))
    if duplicate_ids: errors.append(f"duplicate contract ids: {duplicate_ids}")
    if date_mismatches: errors.append(f"business-date mismatches: {date_mismatches}")
    if arithmetic_errors: errors.append(f"quantity*rate amount mismatches: {arithmetic_errors}")
    if invalid_numeric: errors.append(f"invalid numeric rows: {invalid_numeric}")
    return {
        "status":"validated" if not errors else "validation_failed",
        "row_count":len(rows),"headers":reader.fieldnames or [],
        "duplicate_contract_ids":duplicate_ids,"date_mismatches":date_mismatches,
        "arithmetic_errors":arithmetic_errors,"invalid_numeric_rows":invalid_numeric,
        "target_symbol_contracts":len(target_rows),
        "target_symbol_quantity":str(sum((Decimal(pick(r,"quantity").replace(",","")) for r in target_rows if pick(r,"quantity")),Decimal(0))),
        "errors":errors
    }

def capture(output_dir, fetcher=fetch, retrieved_at=None):
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
    stamp=retrieved_at or datetime.now(timezone.utc).isoformat()
    records=[]
    for target in TARGETS:
        rec=dict(target); rec["source_url"]=f"{BASE}/{target['date']}.csv"; rec["retrieved_at_utc"]=stamp
        try:
            status,headers,body=fetcher(rec["source_url"])
            rec.update(http_status=status,content_type=headers.get("Content-Type") or headers.get("content-type"),response_bytes=len(body),response_sha256=hashlib.sha256(body).hexdigest())
            if status!=200:
                rec["capture_status"]="http_error"
            elif not body or body.lstrip().startswith((b"<!DOCTYPE",b"<html")):
                rec["capture_status"]="non_csv_response"
            else:
                name=f"floorsheet_{target['date']}.csv"
                (out/name).write_bytes(body)
                rec["filename"]=name
                rec["validation"]=validate_rows(body,target["symbol"],target["date"])
                rec["capture_status"]="captured"
        except Exception as exc:
            rec["capture_status"]="unavailable"; rec["error"]=f"{type(exc).__name__}: {exc}"
        records.append(rec)
    report={
        "task":"P4.33","source_class":"third_party_huggingface_archive_claiming_nepse_floorsheet_data",
        "dataset":"urekmazino69/Nepse-floorsheet-and-indices","retrieved_at_utc":stamp,
        "records":records,
        "interpretation":"A downloaded CSV and valid contract rows are third-party archive evidence only. Dataset completeness, exchange-origin and full-session pagination are not independently proven. A zero-symbol-row result never establishes NO_TRADE. First-trade boundaries remain UNKNOWN pending complete primary or independently validated full-session evidence."
    }
    (out/"capture_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return report

if __name__=="__main__":
    result=capture("reference/p433_floorsheets")
    for r in result["records"]:
        v=r.get("validation",{})
        print(f"{r['symbol']} {r['date']}: {r['capture_status']} rows={v.get('row_count','?')} target_contracts={v.get('target_symbol_contracts','?')} sha256={r.get('response_sha256','-')}")
    if any(r["capture_status"]!="captured" for r in result["records"]):
        print("UNKNOWN: one or more exact-date archive objects were unavailable.")
