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
 ids=[];record_ids=[];target=[];date_mismatch=0;arithmetic=0;invalid=0;blank_ids=0
 signatures=set();duplicate_rows=0;id_rows={};symbol_contracts={};contract_symbols={}
 for i,row in enumerate(rows,2):
  cid=pick(row,"contract_no")
  if not cid:blank_ids+=1
  ids.append(cid)
  rid=row.get("id","").strip()
  if rid:record_ids.append(rid)
  sym=pick(row,"symbol").upper()
  if cid:
   id_rows.setdefault(cid,[]).append(row)
   symbol_contracts.setdefault((sym,cid),[]).append(row)
   contract_symbols.setdefault(cid,set()).add(sym)
  sig=tuple(row.get(k,"") for k in sorted(row))
  if sig in signatures:duplicate_rows+=1
  signatures.add(sig)
  d=pick(row,"date")[:10]
  if d and d!=date:date_mismatch+=1
  if pick(row,"symbol").upper()==symbol:target.append(row)
  if not all(pick(row,k) for k in ("quantity","rate","amount")):invalid+=1;continue
  try:
   q=Decimal(pick(row,"quantity").replace(",",""));rate=Decimal(pick(row,"rate").replace(",",""));amt=Decimal(pick(row,"amount").replace(",",""))
   if q<=0 or rate<=0 or amt<=0:invalid+=1
   elif abs(q*rate-amt)>Decimal("0.01") and amt!=(q*rate).to_integral_value(rounding=ROUND_FLOOR):arithmetic+=1
  except (InvalidOperation,ValueError):invalid+=1
 dup_groups=[(k,v) for k,v in symbol_contracts.items() if len(v)>1]
 dup=sum(len(v)-1 for _,v in dup_groups)
 duplicate_examples=[{"symbol":k[0],"contract_no":k[1],"occurrences":len(v),"record_ids":[x.get("id","") for x in v[:5]]} for k,v in dup_groups[:5]]
 cross_symbol=[{"contract_no":k,"symbols":sorted(v)} for k,v in contract_symbols.items() if len(v)>1]
 duplicate_record_ids=len(record_ids)-len(set(record_ids))
 if dup:errors.append(f"duplicate contract numbers within same symbol: {dup}")
 if duplicate_record_ids:errors.append(f"duplicate row IDs: {duplicate_record_ids}")
 if date_mismatch:errors.append(f"business-date mismatches: {date_mismatch}")
 if arithmetic:errors.append(f"quantity*rate amount mismatches: {arithmetic}")
 if invalid:errors.append(f"invalid numeric rows: {invalid}")
 qty=sum((Decimal(pick(r,"quantity").replace(",","")) for r in target if pick(r,"quantity")),Decimal(0))
 amt=sum((Decimal(pick(r,"amount").replace(",","")) for r in target if pick(r,"amount")),Decimal(0))
 target_contract_numbers=[pick(r,"contract_no") for r in target if pick(r,"contract_no")]
 target_record_ids=[r.get("id","") for r in target if r.get("id","")]
 target_duplicate_contract_numbers=len(target_contract_numbers)-len(set(target_contract_numbers))
 target_duplicate_record_ids=len(target_record_ids)-len(set(target_record_ids))
 return {"status":"validated" if not errors else "validation_failed","row_count":len(rows),"headers":reader.fieldnames or [],"unique_contract_numbers":len(set(ids)),"duplicate_contract_numbers_within_symbol":dup,"duplicate_contract_number_groups_within_symbol":len(dup_groups),"duplicate_contract_number_examples":duplicate_examples,"cross_symbol_contract_number_collisions":len(cross_symbol),"cross_symbol_contract_number_examples":cross_symbol[:5],"blank_contract_numbers":blank_ids,"unique_record_ids":len(set(record_ids)),"duplicate_record_ids":duplicate_record_ids,"duplicate_full_rows":duplicate_rows,"date_mismatches":date_mismatch,"arithmetic_errors":arithmetic,"invalid_numeric_rows":invalid,"target_symbol_contracts":len(target),"target_symbol_unique_contract_numbers":len(set(target_contract_numbers)),"target_symbol_duplicate_contract_numbers":target_duplicate_contract_numbers,"target_symbol_unique_record_ids":len(set(target_record_ids)),"target_symbol_duplicate_record_ids":target_duplicate_record_ids,"target_symbol_quantity":str(qty),"target_symbol_turnover":str(amt),"target_contract_samples":[{"contract_no":r.get("contract_no",""),"id":r.get("id",""),"quantity":r.get("quantity",""),"rate":r.get("rate",""),"amount":r.get("amount","")} for r in target[:5]],"errors":errors}
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
