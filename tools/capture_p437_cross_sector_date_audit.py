#!/usr/bin/env python3
"""Stratified official NEPSE EOD parity audit across 12 equity sectors."""
import base64
import json
import tempfile
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from capture_p435_authenticated_historical_floorsheets import (
    BASE, WASM_B64, WASM_GIT_BLOB_SHA, git_blob_sha, token_parser, request,
    parse_json, metadata,
)
from capture_p436_official_eod_history import find_rows, find_total, compare_canonical

WINDOW_START="2025-11-26"
WINDOW_END="2026-11-26"
SAMPLE=[
    ("Microfinance","ACLBSL",2790),("Microfinance","NUBL",163),
    ("Commercial Banks","NABIL",131),("Commercial Banks","NMB",238),
    ("Hydro Power","AHPC",360),("Hydro Power","API",697),
    ("Life Insurance","NLIC",187),("Life Insurance","LICN",188),
    ("Hotels And Tourism","SHL",147),("Hotels And Tourism","CGH",2917),
    ("Tradings","STC",155),("Tradings","BBC",156),
    ("Finance","CFCL",245),("Finance","ICFC",273),
    ("Manufacturing And Processing","HDL",235),("Manufacturing And Processing","NLO",198),
    ("Investment","HIDCL",2742),("Investment","NIFRA",2919),
    ("Development Banks","GBBL",417),("Development Banks","CORBL",450),
    ("Non Life Insurance","NLG",559),("Non Life Insurance","NICL",176),
    ("Others","NTC",307),("Others","HRL",9234),
]

def weekday_class(iso_date):
    day=date.fromisoformat(iso_date)
    weekday=day.weekday()
    if day <= date(2026,4,5):
        # Historical NEPSE week: Sunday-Thursday, with Friday/Saturday closed.
        if weekday==4:return "friday"
        if weekday==5:return "saturday"
    else:
        # Current NEPSE week, effective 2026-04-06: Monday-Friday.
        if weekday==5:return "saturday"
        if weekday==6:return "sunday"
    return "trading_weekday"

def validate_sample(sectors_csv):
    import csv
    sector_path=Path(sectors_csv)
    if not sector_path.exists():
        sector_path=Path("..")/sector_path
    with sector_path.open(newline="",encoding="utf-8-sig") as handle:
        mapping={row["symbol"]:row["sector"] for row in csv.DictReader(handle)}
    counts=Counter(sector for sector,_,_ in SAMPLE)
    errors=[]
    for sector,symbol,expected_id in SAMPLE:
        if mapping.get(symbol)!=sector:
            errors.append(f"{symbol}: sample sector {sector!r} != sectors.csv {mapping.get(symbol)!r}")
    if len(SAMPLE)!=24 or len({symbol for _,symbol,_ in SAMPLE})!=24:
        errors.append("sample must contain 24 unique symbols")
    if len(counts)!=12 or any(n!=2 for n in counts.values()):
        errors.append("sample must contain exactly two symbols in each of 12 sectors")
    return {"sector_counts":dict(sorted(counts.items())),"errors":errors}

def summarize_rows(rows):
    dates=[];missing_date=0;wrong_date=[];missing_hlc=0;missing_volume=0;weekly_closures=[]
    for row in rows:
        if not isinstance(row,dict):
            missing_date+=1;continue
        raw_date=row.get("businessDate")
        if not raw_date:
            missing_date+=1;continue
        day=str(raw_date)[:10];dates.append(day)
        if not (WINDOW_START<=day<=WINDOW_END):
            wrong_date.append(day)
        if any(row.get(k) is None for k in ("highPrice","lowPrice","closePrice")):
            missing_hlc+=1
        if row.get("totalTradedQuantity") is None:
            missing_volume+=1
        kind=weekday_class(day)
        if kind!="trading_weekday":
            weekly_closures.append({"date":day,"weekday":kind})
    counts=Counter(dates)
    return {
        "row_count":len(rows),"unique_date_count":len(counts),
        "duplicate_dates":sorted(d for d,n in counts.items() if n>1),
        "missing_date_rows":missing_date,"out_of_window_dates":sorted(set(wrong_date)),
        "missing_hlc_rows":missing_hlc,"missing_volume_rows":missing_volume,
        "weekly_closure_records":weekly_closures,"observed_dates":sorted(counts),
    }

def capture(output_dir,requester=request,parser=token_parser,retrieved_at=None):
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    stamp=retrieved_at or datetime.now(ZoneInfo("UTC")).isoformat()
    sample_check=validate_sample("scanner_inputs/sectors.csv")
    if sample_check["errors"]:
        raise ValueError("; ".join(sample_check["errors"]))
    wasm=base64.b64decode(WASM_B64)
    wasm_sha=git_blob_sha(wasm)
    if wasm_sha!=WASM_GIT_BLOB_SHA:
        raise ValueError("pinned upstream WASM Git blob SHA mismatch")
    records=[];symbol_results=[]
    with tempfile.TemporaryDirectory() as td:
        wasm_path=Path(td)/"css.wasm";wasm_path.write_bytes(wasm)
        token_url=BASE+"/api/authenticate/prove"
        st,sh,sb=requester("GET",token_url,None,{})
        token=parse_json(sb)
        token_record={"name":"token_prove","url":token_url,**metadata(st,sh,sb)}
        if st!=200 or not isinstance(token,dict):
            token_record["body_saved"]=False
            report={"task":"P4.37","retrieved_at_utc":stamp,"authentication_status":"token_prove_failed",
                    "records":[token_record],"sample":SAMPLE,"results":[]}
            (out/"capture_report.json").write_text(json.dumps(report,indent=2)+"\n")
            return report
        token_record["token_fields_present"]={k:bool(token.get(k)) for k in ("accessToken","refreshToken","salt1","salt2","salt3","salt4","salt5","serverTime")}
        token_record["body_saved"]=False;records.append(token_record)
        access,_refresh=parser(token,wasm_path)
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
        security_map={str(x.get("symbol","")).upper():x for x in securities if isinstance(x,dict)}
        aggregate=Counter()
        sector_summary={}
        for sector,symbol,expected_id in SAMPLE:
            sec=security_map.get(symbol)
            sid=sec.get("id") if sec else None
            item={"sector":sector,"symbol":symbol,"security_id":sid,
                  "expected_security_id":expected_id,"active_status":sec.get("activeStatus") if sec else None,
                  "window":[WINDOW_START,WINDOW_END]}
            if sid is None or sid!=expected_id or item["active_status"]!="A":
                item["status"]="security_master_mismatch_or_inactive"
                symbol_results.append(item);sector_summary.setdefault(sector,[]).append(item);continue
            rows_all=[];pages=[];total_elements=None;total_pages=None;failed=False
            for page in range(0,100):
                url=BASE+f"/api/nots/market/history/security/{sid}?size=500&startDate={WINDOW_START}&endDate={WINDOW_END}&page={page}"
                status,headers,raw=requester("GET",url,None,auth)
                obj=parse_json(raw);page_record={"page":page,"url":url,**metadata(status,headers,raw)}
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
                if page==0:total_elements,total_pages=te,tp
                page_record.update(status="captured",rows_path=rows_path,row_count=len(rows),
                                   total_elements=te,total_pages=tp,total_metadata_path=total_path)
                filename=f"{symbol}_page_{page}.json";(out/filename).write_bytes(raw)
                page_record["filename"]=filename;pages.append(page_record);rows_all.extend(rows)
                if tp is None or tp==0 or page+1>=tp:break
            row_summary=summarize_rows(rows_all)
            pagination_complete=(not failed and isinstance(total_elements,int) and isinstance(total_pages,int)
                                 and len(rows_all)==total_elements and len(pages)==max(1,total_pages))
            canonical=compare_canonical(symbol,rows_all,WINDOW_START,WINDOW_END)
            item.update(status="captured" if not failed else "request_or_schema_failure",
                        pages=pages,total_elements=total_elements,total_pages=total_pages,
                        pagination_complete=pagination_complete,**row_summary,
                        canonical_comparison=canonical,
                        evidence_gate_pass=(pagination_complete and row_summary["missing_date_rows"]==0
                          and row_summary["missing_hlc_rows"]==0 and row_summary["missing_volume_rows"]==0
                          and not row_summary["duplicate_dates"] and not row_summary["out_of_window_dates"]))
            symbol_results.append(item);sector_summary.setdefault(sector,[]).append(item)
            aggregate["symbols"]+=1
            aggregate["official_rows"]+=len(rows_all)
            aggregate["canonical_only_dates"]+=canonical.get("canonical_only_dates_count",0)
            aggregate["canonical_only_tuple_matches"]+=canonical.get("canonical_only_exact_hlc_volume_tuple_match_count",0)
            aggregate["exact_date_overlaps"]+=canonical.get("exact_date_overlap_count",0)
            aggregate["exact_date_mismatches"]+=canonical.get("exact_date_hlc_volume_mismatch_count",0)
            aggregate["weekly_closure_rows"]+=len(row_summary["weekly_closure_records"])
        sector_rollup={}
        for sector,items in sector_summary.items():
            valid=[x for x in items if x.get("status")=="captured"]
            sector_rollup[sector]={
                "sample_size":len(items),"captured":len(valid),
                "official_rows":sum(x.get("row_count",0) for x in valid),
                "canonical_only_dates":sum(x.get("canonical_comparison",{}).get("canonical_only_dates_count",0) for x in valid),
                "canonical_only_tuple_matches":sum(x.get("canonical_comparison",{}).get("canonical_only_exact_hlc_volume_tuple_match_count",0) for x in valid),
                "exact_date_mismatches":sum(x.get("canonical_comparison",{}).get("exact_date_hlc_volume_mismatch_count",0) for x in valid),
                "evidence_gates_passed":sum(bool(x.get("evidence_gate_pass")) for x in valid),
            }
    report={
        "task":"P4.37","source":"NEPSE official API domain",
        "retrieved_at_utc":stamp,
        "window":{"start":WINDOW_START,"end":WINDOW_END,"page_size":500},
        "upstream_authentication_client":{"repo":"basic-bgnr/NepseUnofficialApi",
          "commit":"180a550c60f1959983b854659e650a4c189a3c0f","wasm_git_blob_sha":wasm_sha},
        "authentication_status":"authenticated" if security_map else "authenticated_but_security_master_unavailable",
        "sample_design":{"method":"stratified purposive sample","symbols":len(SAMPLE),
          "sectors":12,"per_sector":2,"sector_source":"scanner_inputs/sectors.csv",
          "security_ids_cross_checked_against_official_security_master":True,
          "sector_counts":sample_check["sector_counts"]},
        "records":records,"aggregate":dict(aggregate),"sector_rollup":sector_rollup,
        "results":symbol_results,
        "weekday_regime":{"through_2026-04-05":"Sunday-Thursday regular sessions; Friday/Saturday weekly closures","from_2026-04-06":"Monday-Friday regular sessions; Saturday/Sunday weekly closures","limitation":"Weekday compatibility does not establish an actual open session; holidays and exceptional closures require the evidence-backed calendar."},
        "interpretation":"Exploratory stratified sample only; not a full-universe finding. Official EOD HLCV comparisons do not prove contract-level execution or broker flow. Canonical rows are not modified. Suspected date-shift patterns remain quarantined pending provenance investigation."
    }
    (out/"capture_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return report

if __name__=="__main__":
    result=capture("reference/p437_cross_sector_date_audit")
    print("P4.37",result["sample_design"]["symbols"],"symbols across",result["sample_design"]["sectors"],"sectors")
    print("Aggregate:",result.get("aggregate"))
    for sector,summary in result.get("sector_rollup",{}).items():
        print(sector,summary)
