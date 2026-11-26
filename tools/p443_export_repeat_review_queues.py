"""Export disjoint review queues from verified repeat-pair triage; no raw mutation."""
import csv, json, argparse
from pathlib import Path
from collections import Counter

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",required=True)
    a=p.parse_args()
    root=Path(a.directory)
    counts=Counter()
    seen=set()
    with (root/"repeat_calendar_triage.csv").open(newline="") as src, (root/"repeat_quarantine_candidates.csv").open("w",newline="") as q, (root/"repeat_evidence_review.csv").open("w",newline="") as v:
        reader=csv.DictReader(src)
        fields=reader.fieldnames+["review_action","promotion_allowed"]
        qw=csv.DictWriter(q,fieldnames=fields)
        vw=csv.DictWriter(v,fieldnames=fields)
        qw.writeheader()
        vw.writeheader()
        for r in reader:
            key=(r["path"],r["blob_sha"],r["row"],r["previous_row"])
            if key in seen: raise ValueError("duplicate pair finding")
            seen.add(key)
            kind=r["pair_classification"]
            if kind in {"PAIR_CONTAINS_RECORDED_CLOSURE","PAIR_CONTAINS_HISTORICAL_LISTED_HOLIDAY","CONFLICTING_EVIDENCE"}:
                target=qw
                action="REVIEW_PAIR_FOR_QUARANTINE"
            elif kind in {"BOTH_OPEN_TUPLE_UNVERIFIED","INSUFFICIENT_SESSION_EVIDENCE"}:
                target=vw
                action="REQUIRE_INDEPENDENT_SECURITY_DATE_EVIDENCE"
            else: raise ValueError("unknown classification: "+kind)
            target.writerow(dict(r,review_action=action,promotion_allowed="false"))
            counts[action]+=1
    if len(seen)!=94543: raise ValueError("incomplete pair register")
    summary={"total_pairs":len(seen),"queues":dict(counts),"corrected_rows":0,"promoted_rows":0,"note":"Pair-level review queues, not row-level deletions or verified corrections. Candidate closure may concern either date."}
    (root/"repeat_review_queue_summary.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary))
if __name__=="__main__":main()
