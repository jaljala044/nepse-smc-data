#!/usr/bin/env python3
"""Cross-check candidate lifecycle dates against official NEPSE historical price-volume API."""
import json
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from capture_p435_authenticated_historical_floorsheets import (
    BASE, WASM_B64, WASM_GIT_BLOB_SHA, git_blob_sha, token_parser, request, metadata
)
import base64
import tempfile

WINDOWS=[
 {"symbol":"NMLBBL","start":"2024-05-16","end":"2024-05-19","candidate":"2024-05-19","prior":"2024-05-16","expected":{"open":599.60,"high":646.60,"low":599.60,"close":646.60,"volume":864}},
 {"symbol":"SMPDA","start":"2024-08-14","end":"2024-08-18","candidate":"2024-08-18","prior":"2024-08-14","expected":{"open":1078.10,"high":1162.70,"low":1078.10,"close":1162.70,"volume":5314}},
}
DATE_KEYS=("businessDate","business_date","date","tradeDate","transactionDate")
ALIASES={
 "open":("openPrice","open","openingPrice"),
 "high":("highPrice","high"),
 "low":("lowPrice","low"),
 "close":("closePrice","close","closingPrice","lastTradedPrice"),
 "volume":("totalTradedQuantity","totalTradeQuantity","totalQuantity","volume","quantity"),
 "turnover":("totalTradedValue","totalTurnover","turnover","amount"),
}
def first(row,names):
 for name in names:
  if name in row and row[name] is not None:return row[name]
 return None
def extract_content(obj):
 if isinstance(obj,list):return obj,{}
 if isinstance(obj,dict):
  for key in ("content","data","result"):
   if isinstance(obj.get(key),list):return obj[key],obj
 return None,obj if isinstance(obj,dict) else {}
def normalize_row(row):
 date_value=first(row,DATE_KEYS)
 result={"date":str(date_value)[:10] if date_value is not None else None}
 for key,names in ALIASES.items():result[key]=first(row,names)
 return result
def capture(output_dir,requester=request,parser=token_parser,retrieved_at=None):
 out=Path(output_dir);out.mkdir(parents=True,exist_ok=True);stamp=retrieved_at or datetime.now(timezone.utc).isoformat();records=[]
 wasm=base64.b64decode(WASM_B64);wasm_sha=git_blob_sha(wasm)
 if wasm_sha!=WASM_GIT_BLOB_SHA:raise ValueError("pinned WASM Git blob SHA mismatch")
 with tempfile.TemporaryDirectory() as td:
  wasm_path=Path(td)/"css.wasm";wasm_path.write_bytes(wasm)
  token_url=BASE+"/api/authenticate/prove";status,headers,raw=requester("GET",token_url,None,{})
  token_obj=None
  try:token_obj=json.loads(raw.decode("utf-8"))
  except Exception:pass
  token_record={"name":"token_prove","url":token_url,**metadata(status,headers,raw),"body_saved":False}
  if status!=200 or not isinstance(token_obj,dict):
   records.append(token_record);result={"task":"P4.36","retrieved_at_utc":stamp,"authentication_status":"token_prove_failed","records":records}
   (out/"capture_report.json").write_text(json.dumps(result,indent=2)+"\n");return result
  token_record["token_fields_present"]={k:(k in token_obj and bool(token_obj.get(k))) for k in ("accessToken","refreshToken","salt1","salt2","salt3","salt4","salt5","serverTime")}
  records.append(token_record)
  access,refresh=parser(token_obj,wasm_path);auth={"Authorization":f"Salter {access}"}
  security_url=BASE+"/api/nots/security?nonDelisted=true"
  ss,sh,sb=requester("GET",security_url,None,auth);security_obj=None
  try:security_obj=json.loads(sb.decode("utf-8"))
  except Exception:pass
  sec_rec={"name":"security_list","url":security_url,**metadata(ss,sh,sb)}
  if ss==200 and isinstance(security_obj,list):
   (out/"security_list.json").write_bytes(sb);sec_rec["filename"]="security_list.json"
  records.append(sec_rec)
  idmap={str(x.get("symbol","")).upper():x.get("id") for x in (security_obj or []) if isinstance(x,dict) and x.get("symbol") and isinstance(x.get("id"),int)}
  results=[]
  for window in WINDOWS:
   symbol=window["symbol"];sid=idmap.get(symbol)
   item={"symbol":symbol,"security_id":sid,"start_date":window["start"],"end_date":window["end"],"candidate_date":window["candidate"],"prior_date":window["prior"],"expected_ohlcv":window["expected"]}
   if sid is None:item["status"]="security_id_unavailable";results.append(item);continue
   query=urllib.parse.urlencode({"size":500,"startDate":window["start"],"endDate":window["end"]})
   url=f"{BASE}/api/nots/market/history/security/{sid}?&{query}"
   rs,rh,rb=requester("GET",url,None,auth);obj=None
   try:obj=json.loads(rb.decode("utf-8"))
   except Exception:pass
   page_meta=metadata(rs,rh,rb);content,top=extract_content(obj)
   page={"page":0,"url":url,**page_meta}
   if rs!=200 or not isinstance(content,list):
    page["status"]="http_error_or_unexpected_schema"
    try:page["response_snippet"]=rb.decode("utf-8","replace")[:240]
    except Exception:pass
    item.update(status="request_or_schema_failure",pages=[page],rows=0,dates=[])
    results.append(item);continue
   filename=f"{symbol}_{window['start']}_{window['end']}_page0.json";(out/filename).write_bytes(rb);page["filename"]=filename
   page["row_count"]=len(content);page["total_elements"]=top.get("totalElements");page["total_pages"]=top.get("totalPages")
   normalized=[normalize_row(row) for row in content if isinstance(row,dict)]
   date_mismatches=[x for x in normalized if x["date"] and not(window["start"]<=x["date"]<=window["end"])]
   duplicate_dates=sorted({d for d in [x["date"] for x in normalized] if d and [x["date"] for x in normalized].count(d)>1})
   candidate=[x for x in normalized if x["date"]==window["candidate"]]
   prior=[x for x in normalized if x["date"]==window["prior"]]
   candidate_row=candidate[0] if len(candidate)==1 else None
   matches={}
   if candidate_row:
    for k,v in window["expected"].items():
     actual=candidate_row.get(k)
     try:matches[k]=(float(actual)==float(v))
     except Exception:matches[k]=False
   item.update(status="captured",pages=[page],rows=len(content),normalized_rows=normalized,returned_dates=sorted(set(x["date"] for x in normalized if x["date"])),date_mismatches=len(date_mismatches),duplicate_dates=duplicate_dates,candidate_rows=len(candidate),prior_rows=len(prior),candidate_matches_expected=matches,candidate_all_expected_fields_match=(len(matches)==len(window["expected"]) and all(matches.values())),pagination_metadata={"totalElements":top.get("totalElements"),"totalPages":top.get("totalPages")} if isinstance(top,dict) else {},prior_zero_rows_observed=(len(prior)==0))
   results.append(item)
  result={"task":"P4.36","source":"NEPSE official market history API","retrieved_at_utc":stamp,"upstream_client":{"repo":"basic-bgnr/NepseUnofficialApi","commit":"180a550c60f1959983b854659e650a4c189a3c0f","wasm_git_blob_sha":wasm_sha},"authentication_status":"authenticated" if idmap else "security_list_unavailable","records":records,"security_results":results,"interpretation":"This endpoint is an official daily price-volume history cross-check, not a trade-level floorsheet. Candidate OHLCV matches corroborate daily bars only. A missing prior-date row is not NO_TRADE without documented complete date coverage and session-calendar confirmation. Token values are never persisted."}
  (out/"capture_report.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
  return result
if __name__=="__main__":
 result=capture("reference/p436_official_price_volume")
 for x in result.get("security_results",[]):print(x["symbol"],x["status"],"rows=",x.get("rows"),"dates=",x.get("returned_dates"),"candidate_match=",x.get("candidate_all_expected_fields_match"))
