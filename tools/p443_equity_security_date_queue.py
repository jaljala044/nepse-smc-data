"""Create a unique equity security-date evidence acquisition queue; no data promotion."""
import argparse,csv,json
from collections import Counter,defaultdict
from pathlib import Path

def build(rows):
    requests=defaultdict(set)
    pairs=Counter()
    for r in rows:
        if r["review_priority"]!="EQUITY_RECOVERY_PRIORITY":continue
        pairs[r["pair_classification"]]+=1
        for day,col in ((r["date"],"row"),(r["previous_date"],"previous_row")):
            requests[(r["symbol"],day)].add((r["path"],r["blob_sha"],r[col],r["pair_classification"]))
    return requests,pairs

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",required=True)
    root=Path(p.parse_args().directory)
    with (root/"equity_first_repeat_review.csv").open(newline="") as src:
        requests,pairs=build(csv.DictReader(src))
    if dict(pairs)!={"BOTH_OPEN_TUPLE_UNVERIFIED":5,"INSUFFICIENT_SESSION_EVIDENCE":44283}:
        raise ValueError("equity pair coverage mismatch")
    priorities=Counter()
    with (root/"equity_security_date_recovery_queue.csv").open("w",newline="") as dst,(root/"equity_security_date_source_lineage.csv").open("w",newline="") as lineage:
        w=csv.writer(dst)
        l=csv.writer(lineage)
        w.writerow(["symbol","date","priority","source_row_references","required_evidence","promotion_allowed"])
        l.writerow(["symbol","date","path","blob_sha","row","pair_classification"])
        for (symbol,day),refs in sorted(requests.items()):
            priority="P1_OPEN_PAIR" if any(x[3]=="BOTH_OPEN_TUPLE_UNVERIFIED" for x in refs) else "P2_SESSION_AND_EXECUTION"
            priorities[priority]+=1
            w.writerow([symbol,day,priority,len({x[:3] for x in refs}),"session calendar; security EOD; execution floorsheet; identity","false"])
            for ref in sorted(refs):l.writerow([symbol,day,*ref])
    summary={"equity_pairs":sum(pairs.values()),"unique_security_dates":len(requests),"unique_symbols":len({s for s,d in requests}),"priorities":dict(priorities),"promoted":0,"limitations":"Queue includes both sides of each pair, not proof of invalidity or missing execution. No data fetched or corrected."}
    (root/"equity_security_date_recovery_summary.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary))
if __name__=="__main__":main()
