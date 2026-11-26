"""Bulk date-grouped positive floorsheet reconciliation; never promote or infer absence."""
import argparse,csv,json
from collections import Counter,defaultdict
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from pathlib import Path
from p443_classify_repeated_candles import source_rows
from validate_historical_floorsheets import download_one,validate_file

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",required=True)
    p.add_argument("--max-dates",type=int,default=20)
    a=p.parse_args()
    root=Path(a.directory)
    raw=root.parent/"bulk-floor-cache"
    raw.mkdir(exist_ok=True)
    with (root/"equity_security_date_recovery_queue.csv").open(newline="") as f:
        queue=[r for r in csv.DictReader(f) if r["priority"]=="P2_SESSION_AND_EXECUTION"]
    keys={(r["symbol"],r["date"]) for r in queue}
    if len(queue)!=68773 or len(keys)!=len(queue):raise ValueError("queue coverage or uniqueness")
    refs=defaultdict(set)
    with (root/"equity_security_date_source_lineage.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            k=(r["symbol"],r["date"])
            if k in keys:refs[k].add((r["path"],r["blob_sha"],r["row"]))
    if set(refs)!=keys:raise ValueError("lineage coverage")
    expected=defaultdict(set)
    for k,links in sorted(refs.items(),key=lambda item:sorted(item[1])[0]):
        for path,sha,row in sorted(links):
            day,values=source_rows(path,sha)[row]
            if day!=k[1]:raise ValueError("lineage date mismatch")
            expected[k].add(values)
    bydate=defaultdict(set)
    for s,d in keys:bydate[d].add(s)
    inventory={}
    with open("reference/p419_observed_date_floorsheet_archive_inventory_2026-11-26.csv",newline="") as f:
        for r in csv.DictReader(f):
            if r["inventory_status"]!="FILE_PRESENT_IN_PINNED_GIT_TREE":continue
            d=r["date"]
            if d in inventory and inventory[d]!=r:raise ValueError("ambiguous inventory")
            inventory[d]=r
    available=sorted(set(bydate)&set(inventory),key=lambda d:(-len(bydate[d]),d))
    selected=available[:a.max_dates]
    results={}
    def process(day):
        item=inventory[day]
        d=download_one(item,raw)
        summary,_=validate_file(item,d,bydate[day],{}, {})
        status=summary["content_status"]
        agg=defaultdict(list)
        if status=="PASS":
            with open(d["path"],newline="",encoding="utf-8-sig") as f:
                for r in csv.DictReader(f):
                    s=r["symbol"].strip().upper()
                    if s in bydate[day]:
                        agg[s].append((Decimal(r["rate"].replace(",","")),Decimal(r["quantity"].replace(",","")),r["transaction"]))
        return day,(status,agg,summary)
    with ThreadPoolExecutor(max_workers=4) as pool:
        for day,v in pool.map(process,selected):results[day]=v
    counts=Counter()
    with (root/"bulk_equity_floorsheet_disposition.csv").open("w",newline="") as f:
        w=csv.writer(f)
        w.writerow(["symbol","date","status","source_blob","contracts","observed_high","observed_low","observed_volume","source_tuple_count","promotion_allowed"])
        for s,d in sorted(keys):
            tuples=expected[s,d]
            obs=[]
            if len(tuples)!=1:status="SOURCE_TUPLE_CONFLICT"
            elif d not in inventory:status="NO_PINNED_PARTITION"
            elif d not in results:status="AVAILABLE_NOT_FETCHED"
            elif results[d][0]!="PASS":status="PARTITION_VALIDATION_FAILED"
            else:
                obs=results[d][1].get(s,[])
                if not obs:status="NO_OBSERVED_CONTRACT_UNKNOWN"
                else:
                    _,h,l,_,v=next(iter(tuples))
                    status="HIGHL_VOLUME_MATCH_OPEN_CLOSE_UNVERIFIED" if (max(x[0] for x in obs),min(x[0] for x in obs),sum(x[1] for x in obs))==(h,l,v) else "HIGHL_VOLUME_CONFLICT"
            counts[status]+=1
            w.writerow([s,d,status,inventory.get(d,{}).get("git_blob_sha",""),len(obs),max((x[0] for x in obs),default=""),min((x[0] for x in obs),default=""),sum(x[1] for x in obs) if obs else "",len(tuples),"false"])
    report={"requests":len(keys),"unique_dates":len(bydate),"available_dates":len(available),"available_requests":sum(len(bydate[d]) for d in available),"selected_dates":selected,"status_counts":dict(counts),"session_validation":[results[d][2] for d in selected],"promoted":0,"limitations":"First batch capped by date; H/L/volume only, not open/close or independent completeness. Absence is unknown."}
    (root/"bulk_equity_floorsheet_summary.json").write_text(json.dumps(report,indent=2,default=str))
    print(json.dumps({k:v for k,v in report.items() if k!="session_validation"}))
if __name__=="__main__":main()
