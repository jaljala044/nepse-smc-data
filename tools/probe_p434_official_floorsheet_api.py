#!/usr/bin/env python3
"""Probe official NEPSE historical floorsheet route without bypassing authentication."""
import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE="https://www.nepalstock.com"
DATES=[("NMLBBL","2024-05-19"),("NMLBBL","2024-05-16"),("SMPDA","2024-08-18"),("SMPDA","2024-08-14")]
HEADERS={"User-Agent":"Mozilla/5.0 (compatible; NEPSE-P434-EvidenceProbe/1.0)","Accept":"application/json, text/plain, */*","Accept-Language":"en-US,en;q=0.9","Referer":"https://www.nepalstock.com/","Origin":"https://www.nepalstock.com","Content-Type":"application/json"}
def request(method,url,body=None):
 data=json.dumps(body).encode() if body is not None else None
 req=urllib.request.Request(url,data=data,headers=HEADERS,method=method)
 try:
  with urllib.request.urlopen(req,timeout=25) as res:return res.status,dict(res.headers.items()),res.read()
 except urllib.error.HTTPError as exc:return exc.code,dict(exc.headers.items()),exc.read()
def safe_json(raw):
 try:return json.loads(raw.decode("utf-8"))
 except Exception:return None
def summary(raw):
 obj=safe_json(raw)
 if isinstance(obj,dict):
  return {"json_type":"object","keys":sorted(obj.keys()),"floorsheet_keys":sorted(obj.get("floorsheets",{}).keys()) if isinstance(obj.get("floorsheets"),dict) else [],"content_count":len(obj.get("floorsheets",{}).get("content",[])) if isinstance(obj.get("floorsheets"),dict) else None,"total_elements":obj.get("floorsheets",{}).get("totalElements") if isinstance(obj.get("floorsheets"),dict) else None,"total_pages":obj.get("floorsheets",{}).get("totalPages") if isinstance(obj.get("floorsheets"),dict) else None}
 if isinstance(obj,list):return {"json_type":"array","count":len(obj),"first_keys":sorted(obj[0].keys()) if obj and isinstance(obj[0],dict) else []}
 return {"json_type":"non_json"}
def probe(output_dir,requester=request,retrieved_at=None):
 out=Path(output_dir);out.mkdir(parents=True,exist_ok=True);stamp=retrieved_at or datetime.now(timezone.utc).isoformat();records=[]
 endpoints=[
  ("market_status","GET",BASE+"/api/nots/nepse-data/market-open",None,True),
  ("security_list","GET",BASE+"/api/nots/security?nonDelisted=true",None,True),
  ("token_prove","GET",BASE+"/api/authenticate/prove",None,False),
 ]
 for name,method,url,body,save in endpoints:
  try:
   status,headers,raw=requester(method,url,body)
   rec={"name":name,"method":method,"url":url,"http_status":status,"content_type":headers.get("Content-Type") or headers.get("content-type"),"response_bytes":len(raw),"response_sha256":hashlib.sha256(raw).hexdigest(),"response_summary":summary(raw)}
   if name=="token_prove":
    obj=safe_json(raw)
    if isinstance(obj,dict):rec["token_fields_present"]={k:(k in obj and bool(obj.get(k))) for k in ("accessToken","refreshToken","salt1","salt2","salt3","salt4","salt5","serverTime")}
    rec["body_saved"]=False
   elif save:
    filename=f"{name}.json";(out/filename).write_bytes(raw);rec["filename"]=filename
   records.append(rec)
  except Exception as exc:records.append({"name":name,"method":method,"url":url,"error":f"{type(exc).__name__}: {exc}"})
 security_rec=next((x for x in records if x["name"]=="security_list"),{})
 sec_raw=(out/"security_list.json").read_bytes() if (out/"security_list.json").exists() else b""
 securities=safe_json(sec_raw);idmap={}
 if isinstance(securities,list):
  for item in securities:
   if isinstance(item,dict) and item.get("symbol") and item.get("id") is not None:idmap[str(item["symbol"]).upper()]=item["id"]
 for symbol,date in DATES:
  sid=idmap.get(symbol);rec={"symbol":symbol,"business_date":date,"security_id":sid}
  if sid is None:rec["status"]="skipped_security_id_unavailable";records.append(rec);continue
  query=urllib.parse.urlencode({"businessDate":date,"size":500,"sort":"contractid,desc","page":0})
  url=f"{BASE}/api/nots/security/floorsheet/{sid}?&{query}"
  try:
   status,headers,raw=requester("POST",url,{"id":0})
   rec.update(method="POST",url=url,http_status=status,content_type=headers.get("Content-Type") or headers.get("content-type"),response_bytes=len(raw),response_sha256=hashlib.sha256(raw).hexdigest(),response_summary=summary(raw))
   obj=safe_json(raw)
   if status==200 and isinstance(obj,dict) and isinstance(obj.get("floorsheets"),dict):
    name=f"{symbol}_{date}_page0.json";(out/name).write_bytes(raw);rec["filename"]=name;rec["status"]="page0_captured"
   else:rec["status"]="not_authenticated_or_unexpected_response"
  except Exception as exc:rec["status"]="request_failed";rec["error"]=f"{type(exc).__name__}: {exc}"
  records.append(rec)
 result={"task":"P4.34","source":"NEPSE official web/API domain","retrieved_at_utc":stamp,"authentication_policy":"No token challenge was solved and no access-control bypass was attempted. Token response values are never persisted.","records":records,"interpretation":"A 200 page-0 response is not complete-session evidence. Capture every page and require upstream totalElements/totalPages plus contract-level validation. A 401/403 or unexpected payload means official historical access remains unavailable by this probe; UNKNOWN is retained."}
 (out/"probe_report.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 return result
if __name__=="__main__":
 result=probe("reference/p434_official_api_probe")
 for r in result["records"]:print(r.get("name",r.get("symbol","?")),r.get("business_date",""),r.get("http_status",r.get("status",r.get("error",""))),r.get("response_summary",{}))
