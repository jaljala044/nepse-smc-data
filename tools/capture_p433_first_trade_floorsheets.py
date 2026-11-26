#!/usr/bin/env python3
"""Capture and verify four exact-date compressed HF floorsheets; never infer NO_TRADE."""
import csv
import gzip
import hashlib
import io
import json
import urllib.request
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_FLOOR
from pathlib import Path

BASE="https://huggingface.co/datasets/urekmazino69/Nepse-floorsheet-and-indices/resolve/main/"
TREE_PATH=Path("reference/p433_floorsheets/huggingface_repo_tree.json")
TARGETS=[
 {"symbol":"NMLBBL","date":"2024-05-19","role":"candidate_first_positive_volume_date"},
 {"symbol":"NMLBBL","date":"2024-05-16","role":"immediately_preceding_candidate_session"},
 {"symbol":"SMPDA","date":"2024-08-18","role":"candidate_first_positive_volume_date"},
 {"symbol":"SMPDA","date":"2024-08-14","role":"immediately_preceding_candidate_session"},
]
ALIASES={"contract_no":("contract_no","contractno","contract_id","contractid"),"date":("calculation_date","business_date","businessdate","date"),"symbol":("stock_symbol","symbol","scrip"),"quantity":("quantity","qty"),"rate":("rate","price"),"amount":("amount","amt","total_amount")}
def pick(row,key):
 for name in ALIASES[key]:
  if name in row and str(row[name]).strip(): return str(row[name]).strip()
 return ""
def fetch(url):
 req=urllib.request.Request(url,headers={"User-Agent":"NEPSE-P433-Evidence-Audit/1.0"})
 with urllib.request.urlopen(req,timeout=60) as res: return res.status,dict(res.headers.items()),res.read()
def validate_rows(raw,symbol,date):
 reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
 headers=[(h or "").strip().lower() for h in (reader.fieldnames or [])]
 if not headers:return {"status":"schema_unknown","row_count":0,"errors":["CSV has no header"],"target_symbol_contracts":0}
 rows=[{(k or "").strip().lower():(v or "").strip() for k,v in row.items()} for row in reader]
 errors=[];missing=[k for k in ALIASES if not any(a in headers for a in ALIASES[k])]
 if missing:errors.append("missing required columns: "+",".join(missing))
 ids=[];target=[];date_mismatch=0;arithmetic=0;invalid=0
 for i,row in enumerate(rows,2):
  cid=pick(row,"contract_no")
  if not cid:errors.append(f"row {i}: missing contract id")
  ids.append(cid)
  d=pick(row,"date")[:10]
  if d and d!=date:date_mismatch+=1
  if pick(row,"symbol").upper()==symbol:target.append(row)
  if not all(pick(row,k) for k in ("quantity","rate","amount")):invalid+=1;continue
  try:
   q=Decimal(pick(row,"quantity").replace(",",""));rate=Decimal(pick(row,"rate").replace(",",""));amt=Decimal(pick(row,"amount").replace(",",""))
   if q<=0 or rate<=0 or amt<=0:invalid+=1
   elif abs(q*rate-amt)>Decimal("0.01") and amt!=q.to_integral_value(rounding=ROUND_FLOOR)*rate if False else False: pass
   elif abs(q*rate-amt)>Decimal("0.01") and amt!=(q*rate).to_integral_value(rounding=ROUND_FLOOR):arithmetic+=1
  except (InvalidOperation,ValueError):invalid+=1
 dup=len(ids)-len(set(ids))
 if dup:errors.append(f"duplicate contract ids: {dup}")
 if date_mismatch:errors.append(f"business-date mismatches: {date_mismatch}")
 if arithmetic:errors.append(f"quantity*rate amount mismatches: {arithmetic}")
 if invalid:errors.append(f"invalid numeric rows: {invalid}")
 qty=sum((Decimal(pick(r,"quantity").replace(",","")) for r in target if pick(r,"quantity")),Decimal(0))
 return {"status":"validated" if not errors else "validation_failed","row_count":len(rows),"headers":reader.fieldnames or [],"duplicate_contract_ids":dup,"date_mismatches":date_mismatch,"arithmetic_errors":arithmetic,"invalid_numeric_rows":invalid,"target_symbol_contracts":len(target),"target_symbol_quantity":str(qty),"errors":errors}
def tree_metadata():
 if not TREE_PATH.exists():return {}
 data=json.loads(TREE_PATH.read_text(encoding="utf-8"))
 return {x["path"]:x for x in data.get("files",[])}
def capture(output_dir,fetcher=fetch,retrieved_at=None,metadata=None):
 out=Path(output_dir);out.mkdir(parents=True,exist_ok=True);stamp=retrieved_at or datetime.now(timezone.utc).isoformat();metadata=metadata if metadata is not None else tree_metadata();records=[]
 for target in TARGETS:
  rec=dict(target);path=f"floorsheet/{target['date']}.csv.gz";rec["source_url"]=BASE+path;rec["source_path"]=path;rec["retrieved_at_utc"]=stamp
  meta=metadata.get(path)
  if meta:rec["source_git_oid"]=meta.get("oid");rec["expected_compressed_bytes"]=meta.get("size");rec["expected_lfs_sha256"]=(meta.get("lfs") or {}).get("oid")
  try:
   status,headers,compressed=fetcher(rec["source_url"]);rec.update(http_status=status,content_type=headers.get("Content-Type") or headers.get("content-type"),compressed_bytes=len(compressed),compressed_sha256=hashlib.sha256(compressed).hexdigest())
   if status!=200:rec["capture_status"]="http_error"
   elif not compressed.startswith(b"\x1f\x8b"):rec["capture_status"]="non_gzip_response"
   else:
    raw=gzip.decompress(compressed);rec["uncompressed_bytes"]=len(raw);rec["uncompressed_sha256"]=hashlib.sha256(raw).hexdigest()
    if meta and meta.get("size")!=len(compressed):rec["integrity_error"]="compressed size differs from HF tree metadata"
    if meta and (meta.get("lfs") or {}).get("oid")!=rec["compressed_sha256"]:rec["integrity_error"]="LFS SHA-256 differs from downloaded bytes"
    gz_name=f"floorsheet_{target['date']}.csv.gz";csv_name=f"floorsheet_{target['date']}.csv"
    (out/gz_name).write_bytes(compressed);(out/csv_name).write_bytes(raw);rec["compressed_filename"]=gz_name;rec["filename"]=csv_name
    rec["validation"]=validate_rows(raw,target["symbol"],target["date"])
    rec["capture_status"]="captured" if "integrity_error" not in rec else "integrity_failed"
  except Exception as exc:rec["capture_status"]="unavailable";rec["error"]=f"{type(exc).__name__}: {exc}"
  records.append(rec)
 result={"task":"P4.33","source_class":"third_party_huggingface_archive_claiming_nepse_floorsheet_data","dataset":"urekmazino69/Nepse-floorsheet-and-indices","retrieved_at_utc":stamp,"records":records,"interpretation":"The dataset card and repository are third-party evidence. Captured files and validated contracts do not independently prove exchange origin or full-session completeness. Zero target rows never establishes NO_TRADE. First-trade boundaries remain UNKNOWN pending complete primary or independently validated session evidence."}
 (out/"capture_report.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 return result
if __name__=="__main__":
 result=capture("reference/p433_floorsheets")
 for r in result["records"]:
  v=r.get("validation",{});print(f"{r['symbol']} {r['date']}: {r['capture_status']} rows={v.get('row_count','?')} target_contracts={v.get('target_symbol_contracts','?')} sha256={r.get('compressed_sha256','-')}")
