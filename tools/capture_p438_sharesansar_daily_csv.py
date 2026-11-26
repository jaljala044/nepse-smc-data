#!/usr/bin/env python3
"""Capture pinned ShareSansar daily-market CSVs for P4.38 secondary triangulation."""
import csv
import hashlib
import io
import json
import urllib.request
from decimal import Decimal, InvalidOperation
from datetime import datetime, timezone
from pathlib import Path

UPSTREAM_REPO="OmitNomis/ShareSansarScraper"
UPSTREAM_COMMIT="524442d518d2f2705ade0680c9d2e3f90738e3d6"
BASE=f"https://raw.githubusercontent.com/{UPSTREAM_REPO}/{UPSTREAM_COMMIT}/"
FILES=[
 {"name":"README.md","path":"README.md","size_bytes":6688,"git_blob_sha":"4c8da344a80c284572e32a702094008c444856da","kind":"readme"},
 {"name":"2024_05_16.csv","path":"docs/Data/2024_05_16.csv","size_bytes":45048,"git_blob_sha":"13c32e676ee615da6e0534d35eae2938f615d9e2","kind":"daily","date":"2024-05-16","expected_rows":315,"target_symbol":"NMLBBL","target_role":"prior"},
 {"name":"2024_05_19.csv","path":"docs/Data/2024_05_19.csv","size_bytes":46196,"git_blob_sha":"764b0e048b48a5716998c52e6ca370d3959436e5","kind":"daily","date":"2024-05-19","expected_rows":323,"target_symbol":"NMLBBL","target_role":"candidate"},
 {"name":"2024_08_14.csv","path":"docs/Data/2024_08_14.csv","size_bytes":49567,"git_blob_sha":"d80ed95cd98e6abc3ddc6c2c85485f060d3442fc","kind":"daily","date":"2024-08-14","expected_rows":332,"target_symbol":"SMPDA","target_role":"prior"},
 {"name":"2024_08_18.csv","path":"docs/Data/2024_08_18.csv","size_bytes":49725,"git_blob_sha":"3838b8175e0fda6015a753d1145838150c2fbdf8","kind":"daily","date":"2024-08-18","expected_rows":330,"target_symbol":"SMPDA","target_role":"candidate"},
]
EXPECTED={
 ("NMLBBL","2024-05-19"):{"open":"599.60","high":"646.60","low":"599.60","close":"646.60","volume":"864","turnover":"557461.60","transactions":15,"floorsheet_rows":15},
 ("SMPDA","2024-08-18"):{"open":"1078.10","high":"1162.70","low":"1078.10","close":"1162.70","volume":"5314","turnover":"6175193.80","transactions":192,"floorsheet_rows":192},
}
def git_blob_sha(data):
 return hashlib.sha1(f"blob {len(data)}\0".encode("ascii")+data).hexdigest()
def fetch(url):
 req=urllib.request.Request(url,headers={"User-Agent":"NEPSE-P438-SecondaryEvidenceAudit/1.0"})
 with urllib.request.urlopen(req,timeout=35) as response:return response.status,response.read()
def dec(value):
 if value is None:return None
 value=str(value).strip().replace(",","")
 if value in ("","-"):return None
 try:return Decimal(value)
 except InvalidOperation:return None
def audit_csv(raw,record):
 text=raw.decode("utf-8-sig")
 reader=csv.DictReader(io.StringIO(text))
 header=reader.fieldnames or []
 rows=list(reader)
 symbols=[str(row.get("Symbol","")).strip().upper() for row in rows]
 serials=[int(row["S.No"]) for row in rows if str(row.get("S.No","")).isdigit()]
 duplicate_symbols=sorted({s for s in symbols if symbols.count(s)>1})
 target=record["target_symbol"]
 matches=[row for row in rows if str(row.get("Symbol","")).strip().upper()==target]
 target_row=matches[0] if len(matches)==1 else None
 normalized=None
 if target_row:
  normalized={
   "symbol":target,
   "open":str(dec(target_row.get("Open"))),
   "high":str(dec(target_row.get("High"))),
   "low":str(dec(target_row.get("Low"))),
   "close":str(dec(target_row.get("Close"))),
   "volume":str(dec(target_row.get("Vol"))),
   "turnover":str(dec(target_row.get("Turnover"))),
   "transactions":int(target_row["Trans."]) if str(target_row.get("Trans","")).isdigit() else int(target_row["Trans."]) if str(target_row.get("Trans.","")).isdigit() else None,
   "source_row":target_row,
  }
 expected=EXPECTED.get((target,record["date"]))
 parity={}
 if expected and normalized:
  for key in ("open","high","low","close","volume","turnover"):
   parity[key]=normalized[key]==expected[key]
  parity["transactions"]=normalized["transactions"]==expected["transactions"]
  parity["floorsheet_row_count"]=normalized["transactions"]==expected["floorsheet_rows"]
 return {
  "date":record["date"],"target_symbol":target,"target_role":record["target_role"],
  "header":header,"row_count":len(rows),"expected_row_count":record["expected_rows"],
  "row_count_matches":len(rows)==record["expected_rows"],
  "symbol_count":len(set(symbols)),"duplicate_symbols":duplicate_symbols,
  "serial_sequence_valid":serials==list(range(1,len(rows)+1)),
  "target_row_count":len(matches),"target_row":normalized,
  "target_absent_in_secondary_table":len(matches)==0,
  "expected_candidate_parity":parity,
  "candidate_fields_match":bool(parity) and all(parity.values()),
 }
def capture(output_dir,fetcher=fetch,retrieved_at=None):
 out=Path(output_dir);out.mkdir(parents=True,exist_ok=True);stamp=retrieved_at or datetime.now(timezone.utc).isoformat()
 files=[];daily_results=[];readme_text=""
 for record in FILES:
  url=BASE+record["path"]
  try:
   status,raw=fetcher(url)
   rec={"name":record["name"],"path":record["path"],"url":url,"http_status":status,"response_bytes":len(raw),"expected_bytes":record["size_bytes"],"git_blob_sha":git_blob_sha(raw),"expected_git_blob_sha":record["git_blob_sha"],"sha256":hashlib.sha256(raw).hexdigest()}
   rec["size_matches"]=len(raw)==record["size_bytes"];rec["git_blob_matches"]=rec["git_blob_sha"]==record["git_blob_sha"]
   filename=record["name"];(out/filename).write_bytes(raw);rec["filename"]=filename
   if status!=200 or not rec["size_matches"] or not rec["git_blob_matches"]:
    rec["status"]="SOURCE_INTEGRITY_FAILURE"
   else:
    rec["status"]="CAPTURED"
    if record["kind"]=="readme":
     readme_text=raw.decode("utf-8","replace")
     rec["source_policy_markers"]={"scrapes_sharesansar_today_price":"ShareSansar today's-share-price page" in readme_text,"skips_market_closed_days":"market was closed" in readme_text,"archive_since_march_2024":"March 2024" in readme_text}
    else:
     audit=audit_csv(raw,record);rec["audit"]=audit;daily_results.append(audit)
   files.append(rec)
  except Exception as exc:
   files.append({"name":record["name"],"path":record["path"],"url":url,"status":"FETCH_FAILED","error":f"{type(exc).__name__}: {exc}"})
 source_policy_ok=bool(readme_text) and "ShareSansar today's-share-price page" in readme_text and "market was closed" in readme_text
 candidate_checks=[x for x in daily_results if x["target_role"]=="candidate"]
 prior_checks=[x for x in daily_results if x["target_role"]=="prior"]
 result={
  "task":"P4.38","source_tier":"SECONDARY_PROVIDER_ARCHIVE",
  "provider":"ShareSansar daily share-price page, archived by OmitNomis/ShareSansarScraper",
  "upstream_repo":UPSTREAM_REPO,"upstream_commit":UPSTREAM_COMMIT,
  "retrieved_at_utc":stamp,"source_capture_policy_verified":source_policy_ok,
  "source_policy":"The pinned README states that a Scrapy job captures ShareSansar's daily share-price table and skips days when the market is closed. This is provider-level secondary evidence, not NEPSE primary evidence.",
  "files":files,"daily_results":daily_results,
  "summary":{
   "all_five_files_integrity_verified":len(files)==5 and all(x.get("status")=="CAPTURED" for x in files),
   "candidate_rows_match_historical_floorsheet":len(candidate_checks)==2 and all(x["candidate_fields_match"] for x in candidate_checks),
   "both_prior_tables_contain_other_market_rows":len(prior_checks)==2 and all(x["row_count"]>0 for x in prior_checks),
   "both_target_symbols_absent_on_prior_dates":len(prior_checks)==2 and all(x["target_absent_in_secondary_table"] for x in prior_checks),
   "candidate_transaction_counts_match_floorsheet_rows":len(candidate_checks)==2 and all(x["expected_candidate_parity"].get("floorsheet_row_count") for x in candidate_checks),
  },
  "disposition":"Secondary corroboration only. Missing target rows on prior dates are not promoted to primary NO_TRADE. No canonical OHLCV or lifecycle valid_from is changed.",
 }
 (out/"capture_report.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 return result
if __name__=="__main__":
 result=capture("reference/p438_sharesansar_daily_csv")
 print(json.dumps(result["summary"],indent=2))
 for item in result["daily_results"]:
  print(item["date"],item["target_symbol"],"rows=",item["row_count"],"target_rows=",item["target_row_count"],"candidate_match=",item["candidate_fields_match"])
