"""Audit secondary-only partitions in bounded date batches; no canonical changes."""
import argparse,csv,gzip,hashlib,io,json
from collections import Counter,defaultdict
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from pathlib import Path
from capture_p433_first_trade_floorsheets import fetch,BASE,pick
from p443_classify_repeated_candles import source_rows
from p443_full_session_parity import signature

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",required=True)
    p.add_argument("--offset",type=int,default=0)
    p.add_argument("--limit",type=int,default=20)
    a=p.parse_args()
    root=Path(a.directory)
    with (root/"secondary_bulk_coverage.csv").open(newline="") as f:
        candidates=[r for r in csv.DictReader(f) if r["secondary_status"]=="SECONDARY_ONLY_CANDIDATE"]
    keys={(r["symbol"],r["date"]) for r in candidates}
    if len(keys)!=len(candidates):raise ValueError("duplicate recovery keys")
    bydate=defaultdict(dict)
    for r in candidates:bydate[r["date"]][r["symbol"]]=r
    dates=sorted(bydate,key=lambda d:(-len(bydate[d]),d))
    selected=dates[a.offset:a.offset+a.limit]
    selected_keys={(s,d) for d in selected for s in bydate[d]}
    refs=defaultdict(set)
    with (root/"equity_security_date_source_lineage.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            k=(r["symbol"],r["date"])
            if k in selected_keys:refs[k].add((r["path"],r["blob_sha"],r["row"]))
    if set(refs)!=selected_keys:raise ValueError("lineage coverage mismatch")
    expected=defaultdict(set)
    for k,links in sorted(refs.items(),key=lambda x:sorted(x[1])[0]):
        for path,sha,row in sorted(links):
            date,values=source_rows(path,sha)[row]
            if date!=k[1]:raise ValueError("lineage date mismatch")
            expected[k].add(values)
    def process(day):
        targets=bydate[day]
        item=next(iter(targets.values()))
        result={"date":day,"requests":len(targets),"promotion_allowed":False}
        agg=defaultdict(list)
        try:
            status,_,data=fetch(BASE+item["secondary_path"])
            digest=hashlib.sha256(data).hexdigest()
            result["sha256"]=digest
            if status!=200 or digest!=item["secondary_sha256"] or len(data)!=int(item["secondary_size"]):raise ValueError("hash or size mismatch")
            reader=csv.DictReader(io.StringIO(gzip.decompress(data).decode("utf-8-sig")))
            ids=Counter()
            invalid=0
            total=0
            for r in reader:
                total+=1
                cid=pick(r,"contract_no")
                ids[cid]+=1
                try:key=signature(r,True,day)
                except Exception:
                    invalid+=1
                    continue
                if key[2] in targets:agg[key[2]].append((key[5],key[6],key[7],cid))
            duplicates=sum(n-1 for n in ids.values() if n>1)
            result.update(rows=total,invalid_rows=invalid,duplicate_contract_occurrences=duplicates,status="PASS" if total and not invalid and not duplicates else "PARTITION_QUARANTINE_CANDIDATE")
        except Exception as e:result.update(status="UNAVAILABLE_OR_INTEGRITY_FAILED",error=str(e))
        return day,result,agg
    results={}
    with ThreadPoolExecutor(max_workers=4) as pool:
        for day,result,agg in pool.map(process,selected):results[day]=(result,agg)
    counts=Counter()
    name=f"secondary_bulk_batch_{a.offset:03d}"
    with (root/(name+".csv")).open("w",newline="") as f:
        w=csv.writer(f)
        w.writerow(["symbol","date","status","source_sha256","contracts","observed_high","observed_low","observed_volume","promotion_allowed"])
        for s,d in sorted(selected_keys):
            result,agg=results[d]
            obs=agg.get(s,[]) if result["status"]=="PASS" else []
            h=max((x[1] for x in obs),default="")
            l=min((x[1] for x in obs),default="")
            v=sum(x[0] for x in obs) if obs else ""
            if result["status"]!="PASS":status=result["status"]
            elif len(expected[s,d])!=1:status="SOURCE_TUPLE_CONFLICT"
            elif not obs:status="NO_OBSERVED_CONTRACT_UNKNOWN"
            else:
                _,eh,el,_,ev=next(iter(expected[s,d]))
                status="HLV_MATCH_OPEN_CLOSE_UNVERIFIED" if (h,l,v)==(eh,el,ev) else "HLV_CONFLICT"
            counts[status]+=1
            w.writerow([s,d,status,result.get("sha256",""),len(obs),h,l,v,"false"])
    report={"candidate_dates":len(dates),"candidate_requests":len(keys),"offset":a.offset,"selected_dates":selected,"processed_requests":len(selected_keys),"status_counts":dict(counts),"sessions":[results[d][0] for d in selected],"promoted":0,"limitations":"Reject entire partition on any invalid or duplicate contract. No official completeness, no reliable opening/closing ordering, no inference of no trade."}
    (root/(name+".json")).write_text(json.dumps(report,indent=2))
    print(json.dumps(report))
if __name__=="__main__":main()
