#!/usr/bin/env python3
"""Use the public NEPSE frontend token flow to probe historical company floorsheets.
Secrets stay in memory: never print or persist access/refresh tokens or salts.
"""
import base64
import hashlib
import json
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

BASE="https://www.nepalstock.com"
UPSTREAM_REPO="basic-bgnr/NepseUnofficialApi"
UPSTREAM_COMMIT="180a550c60f1959983b854659e650a4c189a3c0f"
WASM_GIT_BLOB_SHA="06162abc9206c6a855648ed5c0abb2fd515aa555"
WASM_B64="AGFzbQEAAAABGgVgBX9/f39/AX9gAAF/YAAAYAF/AGABfwF/AwwLAgAAAAAAAAEDBAEEBQFwAQICBQYBAYACgAIGCAF/AUGwiQQLB5sBDgZtZW1vcnkCAARfcmR4AAEEX2NkeAABA2NkeAACA3JkeAADA2JkeAAEA25keAAFA21keAAGGV9faW5kaXJlY3RfZnVuY3Rpb25fdGFibGUBAAtfaW5pdGlhbGl6ZQAAEF9fZXJybm9fbG9jYXRpb24ACglzdGFja1NhdmUABwxzdGFja1Jlc3RvcmUACApzdGFja0FsbG9jAAkJBwEAQQELAQAK0QILAwABCzEAIAFB5ABtQQpvIAFBCm0iAEEKb2oiAiACIAEgAEEKbGtqQQJ0QYAIaigCAGpBFmoLLAAgAUEKbSIAQQpvIAEgAEEKbGtqIAFB5ABtQQpvakECdEGACGooAgBBFmoLMQAgAUHkAG1BCm8gAUEKbSIAQQpvaiICIAIgASAAQQpsa2pBAnRBgAhqKAIAakEgagsxACABQeQAbUEKbyABQQptIgBBCm9qIgIgAiABIABBCmxrakECdEGACGooAgBqQTxqCzIAIAFBCm0iAEEKbyICIAIgASAAQQpsa2ogAUHkAG1BCm9qQQJ0QYAIaigCAGpB2ABqCzIAIAFB5ABtQQpvIgAgACABQQptIgJBCm8gASACQQpsa2pqQQJ0QYAIaigCAGpB7gBqCwQAIwALBgAgACQACxAAIwAgAGtBcHEiACQAIAALBQBBoAkLC6UBAQBBgAgLnQEFAAAACAAAAAQAAAAHAAAACQAAAAQAAAAGAAAACQAAAAUAAAAFAAAABgAAAAUAAAADAAAABQAAAAQAAAAEAAAACQAAAAYAAAAGAAAACAAAAAgAAAAGAAAACAAAAAYAAAAFAAAACAAAAAQAAAAJAAAABQAAAAkAAAAIAAAABQAAAAMAAAAEAAAABwAAAAcAAAAEAAAABwAAAAMAAAAJ"
DUMMY_DATA=[147,117,239,143,157,312,161,612,512,804,411,527,170,511,421,667,764,621,301,106,133,793,411,511,312,423,344,346,653,758,342,222,236,811,711,611,122,447,128,199,183,135,489,703,800,745,152,863,134,211,142,564,375,793,212,153,138,153,648,611,151,649,318,143,117,756,119,141,717,113,112,146,162,660,693,261,362,354,251,641,157,178,631,192,734,445,192,883,187,122,591,731,852,384,565,596,451,772,624,691]
DATES=[("NMLBBL","2024-05-19",864),("NMLBBL","2024-05-16",0),("SMPDA","2024-08-18",5314),("SMPDA","2024-08-14",0)]
HEADERS={"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0","Accept":"application/json, text/plain, */*","Accept-Language":"en-US,en;q=0.5","Connection":"close","Host":"www.nepalstock.com","Referer":"www.nepalstock.com","Pragma":"no-cache","Cache-Control":"no-cache","TE":"Trailers"}

def git_blob_sha(data):
 return hashlib.sha1(f"blob {len(data)}\0".encode("ascii")+data).hexdigest()

def token_parser(token_response,wasm_path):
 import pywasm
 runtime=pywasm.core.Runtime();module=runtime.instance_from_file(str(wasm_path))
 def call(name,args):return runtime.invocate(module,name,args)[0]
 s=[token_response[f"salt{i}"] for i in range(1,6)]
 n=call("cdx",s);l=call("rdx",[s[0],s[1],s[3],s[2],s[4]]);o=call("bdx",[s[0],s[1],s[3],s[2],s[4]])
 p=call("ndx",[s[0],s[1],s[3],s[2],s[4]]);q=call("mdx",[s[0],s[1],s[3],s[2],s[4]])
 a=call("cdx",[s[1],s[0],s[2],s[4],s[3]]);b=call("rdx",[s[1],s[0],s[2],s[3],s[4]])
 c=call("bdx",[s[1],s[0],s[3],s[2],s[4]]);d=call("ndx",[s[1],s[0],s[3],s[2],s[4]])
 e=call("mdx",[s[1],s[0],s[3],s[2],s[4]])
 access=token_response["accessToken"];refresh=token_response["refreshToken"]
 positions=[n,l,o,p,q];refresh_positions=[a,b,c,d,e]
 if positions!=sorted(positions) or positions[-1]>=len(access) or refresh_positions!=sorted(refresh_positions) or refresh_positions[-1]>=len(refresh):
  raise ValueError("WASM returned invalid token splice positions")
 return ("".join(access[i:j] for i,j in zip([0]+[x+1 for x in positions],positions+[len(access)])),
         "".join(refresh[i:j] for i,j in zip([0]+[x+1 for x in refresh_positions],refresh_positions+[len(refresh)])))

def request(method,url,body=None,headers=None):
 h=dict(HEADERS);h.update(headers or {})
 data=json.dumps(body).encode("utf-8") if body is not None else None
 if body is not None:h["Content-Type"]="application/json"
 req=urllib.request.Request(url,data=data,headers=h,method=method)
 try:
  with urllib.request.urlopen(req,timeout=35) as res:return res.status,dict(res.headers.items()),res.read()
 except urllib.error.HTTPError as exc:return exc.code,dict(exc.headers.items()),exc.read()

def parse_json(raw):
 try:return json.loads(raw.decode("utf-8"))
 except Exception:return None

def metadata(status,headers,raw):
 return {"http_status":status,"content_type":headers.get("Content-Type") or headers.get("content-type"),"response_bytes":len(raw),"response_sha256":hashlib.sha256(raw).hexdigest(),"etag":headers.get("ETag") or headers.get("etag"),"last_modified":headers.get("Last-Modified") or headers.get("last-modified")}

def compute_floor_payload_id(dummy_id,salts,server_day):
 if not isinstance(dummy_id,int) or dummy_id<0 or dummy_id>=len(DUMMY_DATA):raise ValueError("market status id outside pinned dummy-data table")
 e=DUMMY_DATA[dummy_id]+dummy_id+2*server_day
 ix=1 if e%10<4 else 3
 return e+salts[ix]*server_day-salts[ix-1]

def capture(output_dir,requester=request,parser=token_parser,retrieved_at=None,include_controls=True):
 out=Path(output_dir);out.mkdir(parents=True,exist_ok=True);stamp=retrieved_at or datetime.now(ZoneInfo("UTC")).isoformat();records=[]
 wasm=base64.b64decode(WASM_B64);wasm_sha=git_blob_sha(wasm)
 if wasm_sha!=WASM_GIT_BLOB_SHA:raise ValueError("pinned upstream WASM Git blob SHA mismatch")
 with tempfile.TemporaryDirectory() as td:
  wasm_path=Path(td)/"css.wasm";wasm_path.write_bytes(wasm)
  token_url=BASE+"/api/authenticate/prove"
  ts,th,tb=requester("GET",token_url,None,{})
  token_rec={"name":"token_prove","url":token_url,**metadata(ts,th,tb)}
  token_obj=parse_json(tb)
  if ts!=200 or not isinstance(token_obj,dict):
   records.append(token_rec);result={"task":"P4.35","retrieved_at_utc":stamp,"wasm_source":{"repo":UPSTREAM_REPO,"commit":UPSTREAM_COMMIT,"git_blob_sha":wasm_sha},"authentication_status":"token_prove_failed","records":records}
   (out/"capture_report.json").write_text(json.dumps(result,indent=2)+"\n");return result
  token_rec["token_fields_present"]={k:(k in token_obj and bool(token_obj.get(k))) for k in ("accessToken","refreshToken","salt1","salt2","salt3","salt4","salt5","serverTime")}
  token_rec["body_saved"]=False;records.append(token_rec)
  access,refresh=parser(token_obj,wasm_path)
  salts=[int(token_obj[f"salt{i}"]) for i in range(1,6)]
  server_day=datetime.fromtimestamp(int(token_obj["serverTime"])/1000,ZoneInfo("Asia/Kathmandu")).day
  auth={"Authorization":f"Salter {access}"}
  # Fetch current market status and security master using the in-memory token.
  for name,path in (("market_status","/api/nots/nepse-data/market-open"),("security_list","/api/nots/security?nonDelisted=true")):
   url=BASE+path;status,headers,raw=requester("GET",url,None,auth);rec={"name":name,"url":url,**metadata(status,headers,raw)}
   obj=parse_json(raw)
   if status==200 and isinstance(obj,(dict,list)):
    filename=f"{name}.json";(out/filename).write_bytes(raw);rec["filename"]=filename
   else:rec["response_type"]="non_json" if obj is None else type(obj).__name__
   records.append(rec)
   if name=="market_status":market=obj if status==200 and isinstance(obj,dict) else {}
   else:securities=obj if status==200 and isinstance(obj,list) else []
  dummy_id=market.get("id") if isinstance(market,dict) else None
  if not isinstance(dummy_id,int):
   result={"task":"P4.35","retrieved_at_utc":stamp,"wasm_source":{"repo":UPSTREAM_REPO,"commit":UPSTREAM_COMMIT,"git_blob_sha":wasm_sha},"authentication_status":"market_status_unavailable","server_day_nepal":server_day,"records":records,"interpretation":"Token proof succeeded but authenticated market-status/security-list access did not. No historical floorsheet request was sent; UNKNOWN is retained."}
   (out/"capture_report.json").write_text(json.dumps(result,indent=2)+"\n");return result
  idmap={str(x.get("symbol","")).upper():x.get("id") for x in securities if isinstance(x,dict) and x.get("symbol") and isinstance(x.get("id"),int)}
  payload_id=compute_floor_payload_id(dummy_id,salts,server_day)
  utc_day=datetime.now(ZoneInfo("UTC")).day
  payload_options=[(server_day,payload_id)]
  if utc_day!=server_day:payload_options.append((utc_day,compute_floor_payload_id(dummy_id,salts,utc_day)))
  control_results=[]
  if include_controls:
   current_date=str(market.get("asOf",""))[:10]
   controls=[("marketwide_current",f"{BASE}/api/nots/nepse-data/floorsheet?&size=500&sort=contractId,desc",None)]
   for symbol in ("NMLBBL","SMPDA"):
    sid=idmap.get(symbol)
    if sid is not None and len(current_date)==10:
     controls.append((f"{symbol}_company_current",f"{BASE}/api/nots/security/floorsheet/{sid}?&businessDate={current_date}&size=500&sort=contractid,desc",symbol))
   for name,url,control_symbol in controls:
    status=headers=raw=None;day_used=None
    for payload_day,payload_value in payload_options:
     status,headers,raw=requester("POST",url,{"id":payload_value},auth)
     if status==200:day_used=payload_day;break
     if status!=403:break
    obj=parse_json(raw);rec={"name":name,"url":url,"payload_day_used":day_used,**metadata(status,headers,raw)}
    fs=obj.get("floorsheets") if isinstance(obj,dict) else None
    if status==200 and isinstance(fs,dict):
     content=fs.get("content",[])
     rec.update(status="page0_captured",content_count=len(content) if isinstance(content,list) else None,total_elements=fs.get("totalElements"),total_pages=fs.get("totalPages"))
     filename=f"control_{name}_page0.json";(out/filename).write_bytes(raw);rec["filename"]=filename
    else:
     rec["status"]="invalid_or_http_error"
     try:rec["response_snippet"]=raw.decode("utf-8","replace")[:240]
     except Exception:pass
    control_results.append(rec)
  floor_results=[]
  for symbol,date,expected_volume in DATES:
   sid=idmap.get(symbol);item={"symbol":symbol,"business_date":date,"security_id":sid,"expected_ohlcv_volume":expected_volume}
   if sid is None:item["status"]="security_id_missing";floor_results.append(item);continue
   total_rows=[];page_summaries=[];page_count=None;total_elements=None;failed=False;payload_day_used=None
   for page in range(0,1000):
    query=f"businessDate={date}&size=500&sort=contractid,desc"
    if page>0:query+=f"&page={page}"
    url=f"{BASE}/api/nots/security/floorsheet/{sid}?&{query}"
    attempts=payload_options if page==0 else [(payload_day_used,compute_floor_payload_id(dummy_id,salts,payload_day_used))]
    status=headers=raw=None
    for payload_day,payload_value in attempts:
     status,headers,raw=requester("POST",url,{"id":payload_value},auth)
     if status==200:
      payload_day_used=payload_day;break
     if status!=403:break
    page_meta=metadata(status,headers,raw);obj=parse_json(raw)
    ps={"page":page,"url":url,"payload_day_used":payload_day_used,**page_meta}
    if status!=200 or not isinstance(obj,dict) or not isinstance(obj.get("floorsheets"),dict):
     ps["status"]="invalid_or_http_error"
     try:ps["response_snippet"]=raw.decode("utf-8","replace")[:240]
     except Exception:pass
     page_summaries.append(ps);failed=True;break
    fs=obj["floorsheets"];content=fs.get("content")
    if not isinstance(content,list):ps["status"]="content_missing";page_summaries.append(ps);failed=True;break
    if page==0:
     total_elements=fs.get("totalElements");page_count=fs.get("totalPages")
    ps["content_count"]=len(content);ps["total_elements"]=fs.get("totalElements");ps["total_pages"]=fs.get("totalPages")
    filename=f"{symbol}_{date}_page_{page}.json";(out/filename).write_bytes(raw);ps["filename"]=filename
    page_summaries.append(ps);total_rows.extend(content)
    if page_count is None or not isinstance(page_count,int) or page_count<0:failed=True;break
    if page+1>=max(1,page_count):break
   qty=0;amount=0;bad_amount=0;ids=[];dates=[]
   for row in total_rows:
    cid=row.get("contractId",row.get("contractid",row.get("contract_no")))
    if cid is not None:ids.append(str(cid))
    d=row.get("businessDate",row.get("calculationDate",row.get("business_date")))
    if d is not None:dates.append(str(d)[:10])
    q=row.get("contractQuantity",row.get("quantity",row.get("qty")))
    rate=row.get("contractRate",row.get("rate",row.get("price")))
    amt=row.get("contractAmount",row.get("amount"))
    try:
     from decimal import Decimal
     dq=Decimal(str(q));dr=Decimal(str(rate));da=Decimal(str(amt));qty+=dq;amount+=da
     if abs(dq*dr-da)>Decimal("0.01") and da!=(dq*dr).to_integral_value(rounding="ROUND_FLOOR"):bad_amount+=1
    except Exception:bad_amount+=1
   unique_ids=len(set(ids));date_mismatches=sum(1 for d in dates if d!=date);missing_dates=len(total_rows)-len(dates)
   pagination_complete=(not failed and isinstance(total_elements,int) and isinstance(page_count,int) and len(total_rows)==total_elements and len(page_summaries)==max(1,page_count))
   content_valid=(len(ids)==len(total_rows) and unique_ids==len(ids) and bad_amount==0 and date_mismatches==0 and missing_dates==0)
   item.update(status="captured" if not failed else "request_or_schema_failure",pages=page_summaries,total_elements=total_elements,total_pages=page_count,rows=len(total_rows),unique_contract_ids=unique_ids,duplicate_contract_ids=len(ids)-unique_ids,target_shares=str(qty),target_turnover=str(amount),amount_arithmetic_errors=bad_amount,business_date_mismatches=date_mismatches,missing_business_dates=missing_dates,pagination_complete=pagination_complete,content_valid=content_valid,evidence_gate_pass=(pagination_complete and content_valid and qty==expected_volume),volume_matches_ohlcv=(qty==expected_volume))
   floor_results.append(item)
  result={"task":"P4.35","source":"NEPSE official API domain","retrieved_at_utc":stamp,"upstream_client":{"repo":UPSTREAM_REPO,"commit":UPSTREAM_COMMIT,"token_parser_path":"nepse/TokenUtils.py","wasm_path":"nepse/data/css.wasm","wasm_git_blob_sha":wasm_sha,"dummy_data_path":"nepse/data/DUMMY_DATA.json"},"authentication_status":"authenticated_market_and_security_list" if idmap else "authenticated_but_security_list_missing","server_day_nepal":server_day,"payload_id_sent":True,"payload_id_value_saved":False,"control_results":control_results,"floor_results":floor_results,"records":records,"interpretation":"Tokens and salts were held in memory only and not persisted. A page set is complete only when all pages were retrieved and summed row count equals upstream totalElements. Historical businessDate must be echoed by returned rows; missing or mismatched dates, absent totals, or contract identity failures keep the result UNKNOWN."}
  (out/"capture_report.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
  return result
if __name__=="__main__":
 result=capture("reference/p435_official_historical_floorsheets")
 for item in result.get("floor_results",[]):print(item["symbol"],item["business_date"],item["status"],"rows=",item.get("rows"),"totalElements=",item.get("total_elements"),"pages=",item.get("total_pages"),"complete=",item.get("pagination_complete"))
