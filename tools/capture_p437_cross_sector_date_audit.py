#!/usr/bin/env python3
"""Stratified official NEPSE EOD parity audit across 12 equity sectors."""
import base64
import csv
import json
import tempfile
from decimal import Decimal, InvalidOperation
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
SOURCE_PROVENANCE={
    "canonical_import_repository":"jaljala044/nepse-history-starter",
    "canonical_import_commit":"12002cdc679061192c1ea3cbd5300257286e66af",
    "canonical_import_manifest":"historical_imports/sharesansar_2026-11-20.json",
    "canonical_import_manifest_metrics":{
        "archived_sessions":937,"source_symbols":525,"imported_symbols":525,
        "source_rows":303438,"imported_rows":301632,"flagged_rows":1806
    },
    "upstream_data_repository":"OmitNomis/ShareSansarScraper",
    "upstream_data_commit":"d5949bd628d6b5ca9ebb2b4a15e001a434c6732c",
    "upstream_workbook":"docs/Data/combined_excel.xlsx",
    "upstream_workbook_git_blob_sha":"e200c06f47a0d529baae61680bb40a55d1114fa1",
    "upstream_workbook_size_bytes":41946267,
    "upstream_workbook_sha256":"dc9534bd1e38a467452196548f82a20b14a1fedc9a2e64983484d9137386c38c",
    "upstream_source_type":"ShareSansar scraped daily-price page; secondary source, not NEPSE primary",
    "scraper_date_assignment":"datetime.now().strftime('%Y_%m_%d')",
    "scraper_duplicate_guard":"exact full table row comparison excluding serial number; does not validate official businessDate",
    "downstream_import_date_validation":"Gregorian ISO date and date bounds; no authoritative NEPSE session-calendar check",
    "downstream_history_date_key":"source CSV filename date"
}
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
    zero_trade_rows=0;positive_trade_rows=0
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
        try:
            trades=int(row.get("totalTrades",0))
            quantity=Decimal(str(row.get("totalTradedQuantity",0)))
            turnover=Decimal(str(row.get("totalTradedValue",0)))
            if trades==0 and quantity==0 and turnover==0:
                zero_trade_rows+=1
            elif trades>0 and quantity>0:
                positive_trade_rows+=1
        except (ValueError,TypeError,InvalidOperation):
            pass
        kind=weekday_class(day)
        if kind!="trading_weekday":
            weekly_closures.append({"date":day,"weekday":kind})
    counts=Counter(dates)
    return {
        "row_count":len(rows),"unique_date_count":len(counts),
        "duplicate_dates":sorted(d for d,n in counts.items() if n>1),
        "missing_date_rows":missing_date,"out_of_window_dates":sorted(set(wrong_date)),
        "missing_hlc_rows":missing_hlc,"missing_volume_rows":missing_volume,
        "zero_trade_rows":zero_trade_rows,"positive_trade_rows":positive_trade_rows,
        "weekly_closure_records":weekly_closures,"observed_dates":sorted(counts),
    }

def build_quarantine_rows(symbol,sector,official_rows,start_date,end_date,canonical_dir="03_stock_charts_ohlcv"):
    canonical_path=Path(canonical_dir)/f"{symbol}_OHLCV.csv"
    if not canonical_path.exists():
        canonical_path=Path("..")/canonical_path
    if not canonical_path.exists():
        return []
    with canonical_path.open(newline="",encoding="utf-8-sig") as handle:
        canonical=[row for row in csv.DictReader(handle)
                   if start_date<=row.get("Date","")<=end_date]
    def key(row,official):
        fields=("highPrice","lowPrice","closePrice","totalTradedQuantity") if official else ("High","Low","Close","Volume")
        try:
            return tuple(Decimal(str(row[name])) for name in fields)
        except (KeyError,TypeError,InvalidOperation,ValueError):
            return None
    def value(row,name):
        item=row.get(name)
        return "" if item is None else str(item)
    def weekday(day):
        return date.fromisoformat(day).strftime("%A")
    official_by_date={str(r.get("businessDate",""))[:10]:r for r in official_rows
                      if isinstance(r,dict) and r.get("businessDate")}
    canonical_by_date={r.get("Date",""):r for r in canonical}
    official_by_tuple={}
    canonical_by_tuple={}
    for day,row in official_by_date.items():
        item=key(row,True)
        if item is not None:official_by_tuple.setdefault(item,[]).append(day)
    for day,row in canonical_by_date.items():
        item=key(row,False)
        if item is not None:canonical_by_tuple.setdefault(item,[]).append(day)
    result=[]
    for day,row in canonical_by_date.items():
        official=official_by_date.get(day)
        if official:
            left,right=key(official,True),key(row,False)
            if left!=right:
                result.append({"sector":sector,"symbol":symbol,"disposition":"EXACT_DATE_HLCV_MISMATCH",
                    "canonical_date":day,"official_date":day,"calendar_day_offset":0,
                    "canonical_open":value(row,"Open"),"canonical_high":value(row,"High"),
                    "canonical_low":value(row,"Low"),"canonical_close":value(row,"Close"),
                    "canonical_volume":value(row,"Volume"),"official_high":value(official,"highPrice"),
                    "official_low":value(official,"lowPrice"),"official_close":value(official,"closePrice"),
                    "official_volume":value(official,"totalTradedQuantity"),
                    "official_total_trades":value(official,"totalTrades"),
                    "official_total_traded_value":value(official,"totalTradedValue"),
                    "canonical_weekday":weekday(day),"official_weekday":weekday(day)})
            continue
        matches=official_by_tuple.get(key(row,False),[]) if key(row,False) is not None else []
        if matches:
            from datetime import date as date_type
            chosen=sorted(matches,key=lambda d:(abs((date_type.fromisoformat(day)-date_type.fromisoformat(d)).days),
                                                 (date_type.fromisoformat(day)-date_type.fromisoformat(d)).days))[0]
            delta=(date_type.fromisoformat(day)-date_type.fromisoformat(chosen)).days
            official=official_by_date[chosen]
            disposition="CANONICAL_ONLY_TUPLE_MATCHES_OTHER_OFFICIAL_DATE"
        else:
            chosen="";delta="";official={}
            disposition="CANONICAL_ONLY_NO_OFFICIAL_TUPLE_MATCH"
        result.append({"sector":sector,"symbol":symbol,"disposition":disposition,
            "canonical_date":day,"official_date":chosen,"calendar_day_offset":delta,
            "canonical_open":value(row,"Open"),"canonical_high":value(row,"High"),
            "canonical_low":value(row,"Low"),"canonical_close":value(row,"Close"),
            "canonical_volume":value(row,"Volume"),"official_high":value(official,"highPrice"),
            "official_low":value(official,"lowPrice"),"official_close":value(official,"closePrice"),
            "official_volume":value(official,"totalTradedQuantity"),
            "official_total_trades":value(official,"totalTrades"),
            "official_total_traded_value":value(official,"totalTradedValue"),
            "canonical_weekday":weekday(day),"official_weekday":weekday(chosen) if chosen else ""})
    for day,row in official_by_date.items():
        if day in canonical_by_date:continue
        matches=canonical_by_tuple.get(key(row,True),[]) if key(row,True) is not None else []
        if matches:
            from datetime import date as date_type
            chosen=sorted(matches,key=lambda d:(abs((date_type.fromisoformat(d)-date_type.fromisoformat(day)).days),
                                                 (date_type.fromisoformat(d)-date_type.fromisoformat(day)).days))[0]
            delta=(date_type.fromisoformat(chosen)-date_type.fromisoformat(day)).days
            disposition="OFFICIAL_ONLY_TUPLE_MATCHES_OTHER_CANONICAL_DATE"
        else:
            chosen="";delta="";disposition="OFFICIAL_ONLY_NO_CANONICAL_TUPLE_MATCH"
        result.append({"sector":sector,"symbol":symbol,"disposition":disposition,
            "canonical_date":chosen,"official_date":day,"calendar_day_offset":delta,
            "canonical_open":value(canonical_by_date.get(chosen,{}),"Open"),
            "canonical_high":value(canonical_by_date.get(chosen,{}),"High"),
            "canonical_low":value(canonical_by_date.get(chosen,{}),"Low"),
            "canonical_close":value(canonical_by_date.get(chosen,{}),"Close"),
            "canonical_volume":value(canonical_by_date.get(chosen,{}),"Volume"),
            "official_high":value(row,"highPrice"),"official_low":value(row,"lowPrice"),
            "official_close":value(row,"closePrice"),"official_volume":value(row,"totalTradedQuantity"),
            "official_total_trades":value(row,"totalTrades"),
            "official_total_traded_value":value(row,"totalTradedValue"),
            "canonical_weekday":weekday(chosen) if chosen else "","official_weekday":weekday(day)})
    return result

def write_quarantine_matrix(path,rows):
    fields=["sector","symbol","disposition","canonical_date","official_date","calendar_day_offset",
            "canonical_weekday","official_weekday","canonical_open","canonical_high","canonical_low",
            "canonical_close","canonical_volume","official_high","official_low","official_close",
            "official_volume","official_total_trades","official_total_traded_value"]
    with Path(path).open("w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=fields,extrasaction="ignore")
        writer.writeheader();writer.writerows(rows)

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
    records=[];symbol_results=[];quarantine_rows=[]
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
            quarantine_rows.extend(build_quarantine_rows(symbol,sector,rows_all,WINDOW_START,WINDOW_END))
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
            aggregate["zero_trade_rows"]+=row_summary["zero_trade_rows"]
            aggregate["positive_trade_rows"]+=row_summary["positive_trade_rows"]
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
    (out/"quarantine_matrix.csv").parent.mkdir(parents=True,exist_ok=True)
    write_quarantine_matrix(out/"quarantine_matrix.csv",quarantine_rows)
    disposition_counts=dict(Counter(row["disposition"] for row in quarantine_rows))
    date_sets={tuple(x.get("observed_dates",[])) for x in symbol_results if x.get("status")=="captured"}
    date_set_consistency={"unique_date_sets":len(date_sets),
        "all_captured_symbols_share_same_date_set":len(date_sets)==1,
        "shared_date_count":len(next(iter(date_sets))) if len(date_sets)==1 else None}
    report={
        "task":"P4.37","source":"NEPSE official API domain",
        "retrieved_at_utc":stamp,
        "window":{"start":WINDOW_START,"end":WINDOW_END,"page_size":500},
        "upstream_authentication_client":{"repo":"basic-bgnr/NepseUnofficialApi",
          "commit":"180a550c60f1959983b854659e650a4c189a3c0f","wasm_git_blob_sha":wasm_sha},
        "authentication_status":"authenticated" if security_map else "authenticated_but_security_master_unavailable",
        "canonical_data_provenance":SOURCE_PROVENANCE,
        "quarantine_matrix":{"rows":len(quarantine_rows),"disposition_counts":disposition_counts,
                             "path":"reference/p437_cross_sector_date_audit/quarantine_matrix.csv"},
        "sample_design":{"method":"stratified purposive sample","symbols":len(SAMPLE),
          "sectors":12,"per_sector":2,"sector_source":"scanner_inputs/sectors.csv",
          "security_ids_cross_checked_against_official_security_master":True,
          "sector_counts":sample_check["sector_counts"]},
        "records":records,"aggregate":dict(aggregate),"sector_rollup":sector_rollup,
        "date_set_consistency":date_set_consistency,
        "results":symbol_results,
        "weekday_regime":{"through_2026-04-05":"Sunday-Thursday regular sessions; Friday/Saturday weekly closures","from_2026-04-06":"Monday-Friday regular sessions; Saturday/Sunday weekly closures","limitation":"Weekday compatibility does not establish an actual open session; holidays and exceptional closures require the evidence-backed calendar."},
        "interpretation":"Exploratory stratified sample only; not a full-universe finding. Canonical source is ShareSansar-derived, not NEPSE primary. The importer does not enforce an authoritative session calendar; date-stamped duplicate rows remain quarantined. Official EOD HLCV comparisons do not prove contract-level execution or broker flow. Canonical rows are not modified."
    }
    (out/"capture_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return report

if __name__=="__main__":
    result=capture("reference/p437_cross_sector_date_audit")
    print("P4.37",result["sample_design"]["symbols"],"symbols across",result["sample_design"]["sectors"],"sectors")
    print("Aggregate:",result.get("aggregate"))
    for sector,summary in result.get("sector_rollup",{}).items():
        print(sector,summary)
