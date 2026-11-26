#!/usr/bin/env python3
"""Capture official NEPSE historical EOD records using authenticated frontend token flow.

EOD records are not floorsheets and do not prove individual executed contracts.
Tokens and salts remain in memory and are never persisted or printed.
"""
import base64
import json
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from capture_p435_authenticated_historical_floorsheets import (
    BASE, WASM_B64, WASM_GIT_BLOB_SHA, git_blob_sha, token_parser, request,
    parse_json, metadata,
)

WINDOWS = [
    {"symbol":"NMLBBL","known_security_id":396,"start":"2024-05-01","end":"2024-05-31",
     "targets":[{"date":"2024-05-19","expected_volume":864,"role":"candidate"},{"date":"2024-05-16","expected_volume":0,"role":"prior_session"}]},
    {"symbol":"SMPDA","known_security_id":2896,"start":"2024-08-01","end":"2024-08-31",
     "targets":[{"date":"2024-08-18","expected_volume":5314,"role":"candidate"},{"date":"2024-08-14","expected_volume":0,"role":"prior_session"}]},
    {"symbol":"NMLBBL","known_security_id":396,"start":"2026-11-01","end":"2026-11-26","targets":[],"control":True},
    {"symbol":"SMPDA","known_security_id":2896,"start":"2026-11-01","end":"2026-11-26","targets":[],"control":True},
]
HISTORY_PATH="/api/nots/market/history/security/{security_id}"

def find_rows(obj):
    if isinstance(obj,list):
        return obj,"$"
    if not isinstance(obj,dict):
        return None,None
    for key in ("content","securityHistory","data","history","records","result"):
        value=obj.get(key)
        if isinstance(value,list):
            return value,f"$.{key}"
        if isinstance(value,dict):
            rows,path=find_rows(value)
            if rows is not None:
                return rows,f"$.{key}{path[1:]}"
    return None,None

def find_total(obj):
    if not isinstance(obj,dict):
        return None,None,None
    for key in ("securityHistory","data","result"):
        nested=obj.get(key)
        if isinstance(nested,dict):
            te,tp=nested.get("totalElements"),nested.get("totalPages")
            if isinstance(te,int) and isinstance(tp,int):
                return te,tp,f"$.{key}"
    te,tp=obj.get("totalElements"),obj.get("totalPages")
    if isinstance(te,int) and isinstance(tp,int):
        return te,tp,"$"
    return None,None,None

def first_value(row,names):
    for name in names:
        if name in row and row[name] is not None:
            return row[name],name
    return None,None

def inspect_rows(rows):
    date_fields=("businessDate","date","tradeDate","transactionDate")
    symbol_fields=("symbol","stockSymbol","securitySymbol")
    volume_fields=("totalTradedQuantity","totalTradedQty","totalVolume","volume","totalTradedShares")
    ohlc_fields={"open":("openPrice","open"),"high":("highPrice","high"),
                 "low":("lowPrice","low"),"close":("closePrice","close","closingPrice")}
    output=[]
    for row in rows:
        if not isinstance(row,dict):
            output.append({"row_type":type(row).__name__})
            continue
        date,date_key=first_value(row,date_fields)
        symbol,symbol_key=first_value(row,symbol_fields)
        volume,volume_key=first_value(row,volume_fields)
        ohlc={}
        for label,aliases in ohlc_fields.items():
            value,_=first_value(row,aliases)
            ohlc[label]=str(value) if value is not None else None
        output.append({
            "date":str(date)[:10] if date is not None else None,
            "date_field":date_key,
            "symbol":str(symbol).upper() if symbol is not None else None,
            "symbol_field":symbol_key,
            "volume":str(volume) if volume is not None else None,
            "volume_field":volume_key,
            "ohlc":ohlc,
            "has_all_ohlc":all(v is not None for v in ohlc.values()),
        })
    return output

def capture(output_dir,requester=request,parser=token_parser,retrieved_at=None):
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    stamp=retrieved_at or datetime.now(ZoneInfo("UTC")).isoformat()
    wasm=base64.b64decode(WASM_B64)
    wasm_sha=git_blob_sha(wasm)
    if wasm_sha!=WASM_GIT_BLOB_SHA:
        raise ValueError("pinned upstream WASM Git blob SHA mismatch")
    records=[];window_results=[];target_results=[]
    with tempfile.TemporaryDirectory() as td:
        wasm_path=Path(td)/"css.wasm";wasm_path.write_bytes(wasm)
        token_url=BASE+"/api/authenticate/prove"
        st,sh,sb=requester("GET",token_url,None,{})
        token_obj=parse_json(sb)
        token_record={"name":"token_prove","url":token_url,**metadata(st,sh,sb)}
        if st!=200 or not isinstance(token_obj,dict):
            records.append(token_record)
            report={"task":"P4.36","retrieved_at_utc":stamp,"authentication_status":"token_prove_failed","records":records,"windows":[],"target_results":[]}
            (out/"capture_report.json").write_text(json.dumps(report,indent=2)+"\n")
            return report
        token_record["token_fields_present"]={k:bool(token_obj.get(k)) for k in ("accessToken","refreshToken","salt1","salt2","salt3","salt4","salt5","serverTime")}
        token_record["body_saved"]=False;records.append(token_record)
        access,_refresh=parser(token_obj,wasm_path)
        auth={"Authorization":f"Salter {access}"}
        sec_url=BASE+"/api/nots/security?nonDelisted=true"
        ss,shh,sbody=requester("GET",sec_url,None,auth)
        securities=parse_json(sbody)
        sec_record={"name":"security_list","url":sec_url,**metadata(ss,shh,sbody)}
        if ss==200 and isinstance(securities,list):
            (out/"security_list.json").write_bytes(sbody);sec_record["filename"]="security_list.json"
        else:
            securities=[]
        records.append(sec_record)
        id_map={str(x.get("symbol","")).upper():x.get("id") for x in securities if isinstance(x,dict) and isinstance(x.get("id"),int)}
        for wi,window in enumerate(WINDOWS):
            symbol=window["symbol"];sid=id_map.get(symbol)
            wr={"symbol":symbol,"security_id":sid,"known_security_id":window["known_security_id"],
                "start_date":window["start"],"end_date":window["end"],"control_window":bool(window.get("control"))}
            if sid is None:
                wr["status"]="security_id_missing";window_results.append(wr);continue
            url=BASE+HISTORY_PATH.format(security_id=sid)+f"?size=500&startDate={window['start']}&endDate={window['end']}&page=0"
            all_rows=[];pages=[];total_elements=None;total_pages=None;failed=False
            for page in range(0,100):
                page_url=BASE+HISTORY_PATH.format(security_id=sid)+f"?size=500&startDate={window['start']}&endDate={window['end']}&page={page}"
                status,headers,raw=requester("GET",page_url,None,auth)
                obj=parse_json(raw);page_record={"page":page,"url":page_url,**metadata(status,headers,raw)}
                if status!=200 or obj is None:
                    page_record["status"]="http_or_json_failure"
                    page_record["response_snippet"]=raw.decode("utf-8","replace")[:240]
                    pages.append(page_record);failed=True;break
                rows,rows_path=find_rows(obj)
                if rows is None:
                    page_record["status"]="row_collection_not_identified"
                    page_record["top_level_keys"]=sorted(obj.keys()) if isinstance(obj,dict) else None
                    pages.append(page_record);failed=True;break
                te,tp,total_path=find_total(obj)
                if page==0:
                    total_elements,total_pages=te,tp
                page_record.update(status="captured",rows_path=rows_path,row_count=len(rows),
                                   total_elements=te,total_pages=tp,total_metadata_path=total_path)
                filename=f"{symbol}_{window['start']}_{window['end']}_page_{page}.json"
                (out/filename).write_bytes(raw);page_record["filename"]=filename
                pages.append(page_record);all_rows.extend(rows)
                if tp is None or tp==0 or page+1>=tp:
                    break
            inspected=inspect_rows(all_rows)
            observed_dates=sorted(set(r["date"] for r in inspected if r.get("date")))
            wr.update(status="captured" if not failed else "request_or_schema_failure",
                      pages=pages,rows=len(all_rows),total_elements=total_elements,total_pages=total_pages,
                      pagination_complete=(not failed and isinstance(total_elements,int) and isinstance(total_pages,int)
                                           and len(all_rows)==total_elements and len(pages)==max(1,total_pages)),
                      observed_dates=observed_dates,
                      observed_symbols=sorted(set(r["symbol"] for r in inspected if r.get("symbol"))),
                      date_fields_observed=sorted(set(r["date_field"] for r in inspected if r.get("date_field"))),
                      volume_fields_observed=sorted(set(r["volume_field"] for r in inspected if r.get("volume_field"))),
                      all_ohlc_present_rows=sum(1 for r in inspected if r.get("has_all_ohlc")),
                      rows_summary=inspected)
            window_results.append(wr)
            for target in window.get("targets",[]):
                date=target["date"]
                matches=[r for r in inspected if r.get("date")==date]
                symbol_matches=[r for r in matches if r.get("symbol") in (None,symbol)]
                volumes=sorted(set(r["volume"] for r in symbol_matches if r.get("volume") is not None))
                complete=wr["pagination_complete"]
                result={
                    "symbol":symbol,"security_id":sid,"business_date":date,"role":target["role"],
                    "expected_ohlcv_volume":target["expected_volume"],"source_window":[window["start"],window["end"]],
                    "window_pagination_complete":complete,"matching_date_rows":len(matches),
                    "matching_symbol_rows":len(symbol_matches),"observed_volume_values":volumes,
                    "observed_ohlc":[r["ohlc"] for r in symbol_matches],
                    "eod_volume_matches_expected":(len(volumes)==1 and volumes[0]==str(target["expected_volume"])),
                    "status":"row_found" if symbol_matches else "no_record_returned",
                    "evidence_gate_pass":(complete and len(symbol_matches)==1 and
                        symbol_matches[0].get("has_all_ohlc") and len(volumes)==1 and
                        volumes[0]==str(target["expected_volume"])),
                    "limitation":"No record in an EOD query is not proof of NO_TRADE; this is not floorsheet or contract-level evidence."
                }
                target_results.append(result)
    report={
        "task":"P4.36","source":"NEPSE official API domain","retrieved_at_utc":stamp,
        "upstream_authentication_client":{"repo":"basic-bgnr/NepseUnofficialApi",
          "commit":"180a550c60f1959983b854659e650a4c189a3c0f","wasm_git_blob_sha":wasm_sha},
        "authentication_status":"authenticated" if id_map else "authenticated_but_security_list_unavailable",
        "records":records,"windows":window_results,"target_results":target_results,
        "interpretation":"Authenticated official EOD endpoint was tested with month-wide historical windows and a current-month control. EOD responses can cross-check published daily price/volume only. They are not floorsheets, do not prove contract identity or broker flow, and cannot alone establish a first-trade boundary. Empty dates remain UNKNOWN; tokens and salts were never persisted."
    }
    (out/"capture_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return report

if __name__=="__main__":
    result=capture("reference/p436_official_eod_history")
    for row in result["windows"]:
        print(row["symbol"],row["start_date"],row["end_date"],row["status"],"rows=",row.get("rows"),"complete=",row.get("pagination_complete"))
    for row in result["target_results"]:
        print(row["symbol"],row["business_date"],row["status"],"volume_match=",row["eod_volume_matches_expected"])
