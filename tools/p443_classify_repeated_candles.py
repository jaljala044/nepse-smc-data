"""Classify repeat flags against pinned calendar evidence; never alter inputs."""
import argparse, ast, csv, json, subprocess, io, hashlib
from decimal import Decimal
from datetime import date
from functools import lru_cache
from collections import Counter, defaultdict
from pathlib import Path
PIN="56362fb4f65b91fdcca8f50b50e53ad80e703649"
def rows(path):
    return csv.DictReader(subprocess.check_output(["git","show",PIN+":reference/"+path],text=True).splitlines())
@lru_cache(maxsize=4)
def source_rows(path, sha):
    raw=subprocess.check_output(["git","show",PIN+":"+path])
    if hashlib.sha1(("blob %d\0"%len(raw)).encode()+raw).hexdigest()!=sha:
        raise ValueError("source blob mismatch: "+path)
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig"),newline=""))
    result={}
    for row in reader:
        normalized={k.lower().replace("_","").replace(" ",""):v for k,v in row.items()}
        day=next((normalized[k] for k in ("date","tradingdate","tradedate") if k in normalized),None)
        if day is None: raise ValueError("missing date column: "+path)
        result[str(reader.line_num)]=(day.strip(),tuple(Decimal(normalized[k]) for k in ("open","high","low","close","volume")))
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    evidence=defaultdict(set)
    for r in rows("nepse_canonical_session_calendar_2025-2026.csv"):
        if r["status"]=="verified_closed" and r["scope"]=="all_securities":
            evidence[r["date"]].add("closed")
        elif r["status"]=="verified_open_observed":
            evidence[r["date"]].add("open")
    for r in rows("nepse_session_calendar_2026.csv"):
        if r["status"]=="verified_closed" and r["scope"]=="all_securities":
            evidence[r["date"]].add("closed")
    for r in rows("nepse_positive_open_sessions_2025-11-26_2026-11-25.csv"):
        if r["status"]=="verified_open":
            evidence[r["date"]].add("open")
    for r in rows("nepse_primary_observed_open_sessions_2025-2026.csv"):
        if r["classification"]=="primary_positive_trade_observation":
            evidence[r["date"]].add("open")
    listed={r["holiday_date"] for r in rows("nepse_holiday_listing_entries_2014-2025.csv") if r["year_capture_status"]=="all_pages_captured_for_year"}
    shifts={(r["symbol"],r["raw_date"]) for r in rows("p427_490_date_shift_audit_2026-11-26.csv")}
    counts=Counter()
    pair_counts=Counter()
    holiday_counts=Counter()
    out=Path(a.output)
    out.mkdir(parents=True,exist_ok=True)
    with open(a.input) as src, (out/"repeat_calendar_triage.csv").open("w",newline="") as dst:
        w=csv.writer(dst)
        w.writerow(["path","blob_sha","symbol","date","row","previous_row","calendar_evidence","prior_date_shift_candidate","disposition","previous_date","previous_calendar_evidence","current_listed_holiday","previous_listed_holiday","pair_classification","volume"] )
        for line in src:
            r=json.loads(line)
            if r["classification"]!="repeated_adjacent_tuple_unresolved":continue
            _,_,symbol,day=ast.literal_eval(r["key"])
            e=evidence[day]
            status=("CONFLICTING_SESSION_EVIDENCE" if e=={"open","closed"} else
                    "CLOSED_SESSION_CANDIDATE" if e=={"closed"} else
                    "OPEN_SESSION_TUPLE_UNVERIFIED" if e=={"open"} else
                    "SESSION_UNKNOWN")
            counts[status]+=1
            source=source_rows(r["path"],r["blob_sha"])
            current,values=source[str(r["row"])]
            prior,previous=source[str(r["previous_row"])]
            if current!=day or prior==day or values!=previous:
                raise ValueError("repeat lineage mismatch: "+r["path"]+":"+str(r["row"]))
            pe=evidence[prior]
            current_listed=day in listed
            prior_listed=prior in listed
            if current_listed: holiday_counts["current_listed_holiday"]+=1
            if prior_listed: holiday_counts["previous_listed_holiday"]+=1
            if e=={"open","closed"} or pe=={"open","closed"} or (current_listed and "open" in e) or (prior_listed and "open" in pe):
                pair="CONFLICTING_EVIDENCE"
            elif "closed" in e or "closed" in pe:
                pair="PAIR_CONTAINS_RECORDED_CLOSURE"
            elif current_listed or prior_listed:
                pair="PAIR_CONTAINS_HISTORICAL_LISTED_HOLIDAY"
            elif e=={"open"} and pe=={"open"}:
                pair="BOTH_OPEN_TUPLE_UNVERIFIED"
            else:
                pair="INSUFFICIENT_SESSION_EVIDENCE"
            pair_counts[pair]+=1
            w.writerow([r["path"],r["blob_sha"],symbol,day,r["row"],r["previous_row"],";".join(sorted(e)),(symbol,day) in shifts,status,prior,";".join(sorted(pe)),current_listed,prior_listed,pair,str(values[-1])])
    summary={"pinned_commit":PIN,"counts":dict(counts),"total":sum(counts.values()),"pair_counts":dict(pair_counts),"listed_holiday_counts":dict(holiday_counts),"limitations":"Both pinned source rows and exact tuple equality checked. Historical listed holidays are candidates, not proven universal closures. Open session does not establish security-specific execution. No automatic corrections."}
    (out/"repeat_calendar_summary.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary))
    if summary["total"]!=94543:raise ValueError("unexpected repeat count for pinned audit")
if __name__=="__main__":main()
