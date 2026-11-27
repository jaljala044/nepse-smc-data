"""Read-back audit for the P4.44 23,377-pair evidence artifact."""
import argparse,csv,json,re
from collections import Counter
from datetime import date
from pathlib import Path

BLOB_RE=re.compile(r"^[0-9a-f]{40}$")
SCOPES={"historical_effective_dated_id","current_snapshot_only","unresolved"}

def audit(path,expected_pairs=23377,expected_symbols=209):
    with Path(path).open(encoding="utf-8-sig",newline="") as f:
        rows=list(csv.DictReader(f))
    issues=[]; symbols=set(); pair_ids=set(); counts=Counter(); dates=[]
    required={"pair_id","symbol","previous_date","current_date","source_path","source_blob_sha","previous_source_row","current_source_row","source_pair_tuple_equal","identity_scope","historical_stable_id","current_snapshot_security_id","disposition","promotion_allowed"}
    if rows and not required.issubset(rows[0]): issues.append({"code":"MISSING_COLUMNS","columns":sorted(required-set(rows[0]))})
    for n,r in enumerate(rows,2):
        sym=r.get("symbol","").strip(); pid=r.get("pair_id","").strip()
        if not sym: issues.append({"row":n,"code":"MISSING_SYMBOL"})
        symbols.add(sym)
        if not pid: issues.append({"row":n,"code":"MISSING_PAIR_ID"})
        elif pid in pair_ids: issues.append({"row":n,"code":"DUPLICATE_PAIR_ID","pair_id":pid})
        pair_ids.add(pid)
        if not BLOB_RE.fullmatch(r.get("source_blob_sha","")): issues.append({"row":n,"code":"INVALID_SOURCE_BLOB_SHA"})
        try:
            prev=date.fromisoformat(r["previous_date"]); cur=date.fromisoformat(r["current_date"])
            dates.extend((prev.isoformat(),cur.isoformat()))
            if prev==cur: issues.append({"row":n,"code":"SAME_DATE_PAIR"})
        except (ValueError,KeyError): issues.append({"row":n,"code":"INVALID_PAIR_DATE"})
        if r.get("source_pair_tuple_equal")!="true": issues.append({"row":n,"code":"SOURCE_TUPLE_NOT_VERIFIED"})
        scope=r.get("identity_scope","")
        if scope not in SCOPES: issues.append({"row":n,"code":"INVALID_IDENTITY_SCOPE","value":scope})
        if scope=="historical_effective_dated_id" and not r.get("historical_stable_id","").strip():
            issues.append({"row":n,"code":"HISTORICAL_ID_MISSING"})
        if scope!="historical_effective_dated_id" and r.get("historical_stable_id","").strip():
            issues.append({"row":n,"code":"UNVERIFIED_HISTORICAL_ID_PRESENT"})
        if r.get("disposition")!="HOLD_UNKNOWN_NO_INFERENCE": issues.append({"row":n,"code":"NON_HOLD_DISPOSITION"})
        if r.get("promotion_allowed")!="false": issues.append({"row":n,"code":"PROMOTION_NOT_FALSE"})
        counts["identity_"+scope]+=1
        counts["previous_session_"+r.get("previous_session_status","missing")]+=1
        counts["current_session_"+r.get("current_session_status","missing")]+=1
    if len(rows)!=expected_pairs: issues.append({"code":"PAIR_COUNT_MISMATCH","actual":len(rows),"expected":expected_pairs})
    if len(symbols)!=expected_symbols: issues.append({"code":"SYMBOL_COUNT_MISMATCH","actual":len(symbols),"expected":expected_symbols})
    summary={"rows":len(rows),"symbols":len(symbols),"unique_pair_ids":len(pair_ids),"date_min":min(dates) if dates else None,"date_max":max(dates) if dates else None,"counts":dict(sorted(counts.items())),"issues":issues,"valid":not issues}
    return summary

def main():
    p=argparse.ArgumentParser();p.add_argument("matrix");p.add_argument("--expected-pairs",type=int,default=23377);p.add_argument("--expected-symbols",type=int,default=209);p.add_argument("--summary-output")
    a=p.parse_args(); result=audit(a.matrix,a.expected_pairs,a.expected_symbols)
    if a.summary_output: Path(a.summary_output).write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2)); raise SystemExit(0 if result["valid"] else 1)
if __name__=="__main__": main()
