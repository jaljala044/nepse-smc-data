"""Classify repeat flags against pinned calendar evidence; never alter inputs."""
import argparse, ast, csv, json, subprocess
from collections import Counter, defaultdict
from pathlib import Path
PIN="56362fb4f65b91fdcca8f50b50e53ad80e703649"
def rows(path):
    return csv.DictReader(subprocess.check_output(["git","show",PIN+":reference/"+path],text=True).splitlines())
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
    shifts={(r["symbol"],r["raw_date"]) for r in rows("p427_490_date_shift_audit_2026-11-26.csv")}
    counts=Counter()
    out=Path(a.output)
    out.mkdir(parents=True,exist_ok=True)
    with open(a.input) as src, (out/"repeat_calendar_triage.csv").open("w",newline="") as dst:
        w=csv.writer(dst)
        w.writerow(["path","blob_sha","symbol","date","row","previous_row","calendar_evidence","prior_date_shift_candidate","disposition"])
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
            w.writerow([r["path"],r["blob_sha"],symbol,day,r["row"],r["previous_row"],";".join(sorted(e)),(symbol,day) in shifts,status])
    summary={"pinned_commit":PIN,"counts":dict(counts),"total":sum(counts.values()),"limitations":"Calendar evidence only; current row date checked, not prior row date. No tuple independently verified; no automatic corrections."}
    (out/"repeat_calendar_summary.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary))
    if summary["total"]!=94543:raise ValueError("unexpected repeat count for pinned audit")
if __name__=="__main__":main()
