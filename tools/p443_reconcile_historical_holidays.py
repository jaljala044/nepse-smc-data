"""Join historical holiday pair candidates with authenticated API evidence."""
import argparse,csv,json
from collections import Counter,defaultdict
from pathlib import Path

def reconcile(pairs, holidays):
    dates=defaultdict(list)
    for h in holidays:
        dates[h["date"]].append(h)
    counts=Counter()
    holds={}
    for r in pairs:
        if r["pair_classification"]!="PAIR_CONTAINS_HISTORICAL_LISTED_HOLIDAY":continue
        supported=0
        conflict=False
        for day,loc,ev in ((r["date"],r["row"],r["calendar_evidence"]),(r["previous_date"],r["previous_row"],r["previous_calendar_evidence"])):
            matches=[h for h in dates.get(day,[]) if not h["instrument_type_id"] and h["active_status"].lower() not in {"false","0","inactive"}]
            if not matches:continue
            if "open" in ev.split(";"):
                conflict=True
                continue
            supported+=1
            key=(r["path"],r["blob_sha"],loc)
            record=dict(path=r["path"],blob_sha=r["blob_sha"],row=loc,symbol=r["symbol"],date=day,holiday_source_blobs=";".join(sorted({h["source_blob_sha"] for h in matches})),disposition="API_HOLIDAY_CORROBORATED_HOLD_CANDIDATE",promotion_allowed="false")
            if key in holds and holds[key]!=record:raise ValueError("inconsistent source identity")
            holds[key]=record
        counts["CONFLICTING_OPEN_EVIDENCE" if conflict else "API_HOLIDAY_CORROBORATED_PAIR" if supported else "NO_API_CORROBORATION"]+=1
    return counts,holds

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",required=True)
    a=p.parse_args()
    root=Path(a.directory)
    with (root/"repeat_calendar_triage.csv").open(newline="") as pairs, Path("reference/P443_AUTHENTICATED_HOLIDAY_EVIDENCE_2015_2026.csv").open(newline="") as holidays:
        counts,holds=reconcile(csv.DictReader(pairs),csv.DictReader(holidays))
    if sum(counts.values())!=26544:raise ValueError("historical holiday pair coverage mismatch")
    fields=["path","blob_sha","row","symbol","date","holiday_source_blobs","disposition","promotion_allowed"]
    with (root/"historical_api_holiday_hold_candidates.csv").open("w",newline="") as dst:
        w=csv.DictWriter(dst,fieldnames=fields)
        w.writeheader()
        w.writerows(holds[k] for k in sorted(holds))
    summary={"pairs":sum(counts.values()),"classifications":dict(counts),"unique_candidate_rows":len(holds),"dates":len({h["date"] for h in holds.values()}),"replacements":0,"limitations":"API listing corroboration is not independent confirmation of universal closure or individual stock execution. No raw or canonical data changed."}
    (root/"historical_api_holiday_summary.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary))
if __name__=="__main__":main()
