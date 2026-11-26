"""Separate recorded-closure rows from neighbouring repeat-pair rows, read only."""
import argparse,csv,json
from pathlib import Path
from collections import Counter

def adjudicate(rows):
    affected={}
    pairs=0
    for r in rows:
        if r["pair_classification"]!="PAIR_CONTAINS_RECORDED_CLOSURE":continue
        pairs+=1
        for side,day,loc,evidence in (
            ("current",r["date"],r["row"],r["calendar_evidence"]),
            ("previous",r["previous_date"],r["previous_row"],r["previous_calendar_evidence"])):
            if evidence!="closed":continue
            key=(r["path"],r["blob_sha"],loc)
            value={"path":r["path"],"blob_sha":r["blob_sha"],"row":loc,"symbol":r["symbol"],"date":day,"action":"EXCLUDE_RECORDED_CLOSURE_PENDING_INDEPENDENT_ADJUDICATION","replacement_allowed":"false"}
            if key in affected and affected[key]!=value:raise ValueError("inconsistent row identity")
            affected[key]=value
    return pairs,affected

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",required=True)
    a=p.parse_args()
    root=Path(a.directory)
    with (root/"repeat_calendar_triage.csv").open(newline="") as src:
        pairs,affected=adjudicate(csv.DictReader(src))
    if pairs!=9027:raise ValueError("unexpected recorded-closure pair count")
    fields=["path","blob_sha","row","symbol","date","action","replacement_allowed"]
    with (root/"recorded_closure_row_hold.csv").open("w",newline="") as dst:
        w=csv.DictWriter(dst,fieldnames=fields)
        w.writeheader()
        w.writerows(affected[k] for k in sorted(affected))
    summary={"pairs":pairs,"unique_source_rows_on_recorded_closure":len(affected),"unique_dates":len({r["date"] for r in affected.values()}),"symbols":len({r["symbol"] for r in affected.values()}),"by_date":dict(sorted(Counter(r["date"] for r in affected.values()).items())),"replacements":0,"limitations":"Recorded calendar closure only; independent adjudication still required. Neighbouring rows are not excluded solely because they form a pair. No canonical application."}
    (root/"recorded_closure_row_hold_summary.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary))
if __name__=="__main__":main()
