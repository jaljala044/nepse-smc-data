"""Compare both open-session candles with pinned official security EOD captures."""
import argparse,csv,json,subprocess
from collections import Counter,defaultdict
from decimal import Decimal
from pathlib import Path
from p443_classify_repeated_candles import source_rows,PIN

def load_evidence():
    evidence=defaultdict(list)
    paths=subprocess.check_output(["git","ls-tree","-r","--name-only",PIN,"reference/p437_cross_sector_date_audit","reference/p443_positive_open_sessions_evidence","reference/p436_official_eod_history"],text=True).splitlines()
    for path in paths:
        if not path.endswith("_page_0.json"):continue
        symbol=Path(path).name.split("_")[0]
        raw=subprocess.check_output(["git","show",PIN+":"+path])
        import hashlib
        sha=hashlib.sha1(("blob %d\0"%len(raw)).encode()+raw).hexdigest()
        obj=json.loads(raw,parse_float=Decimal)
        for r in obj.get("content",[]):
            if not all(k in r for k in ("businessDate","highPrice","lowPrice","closePrice","totalTradedQuantity","totalTrades")):continue
            evidence[(symbol,r["businessDate"])].append((path,sha,r))
    return evidence

def compare(values,records):
    if not records:return "NO_SECURITY_DATE_EVIDENCE"
    signatures=set()
    for _,_,r in records:
        signatures.add(tuple(Decimal(str(r[k])) for k in ("highPrice","lowPrice","closePrice","totalTradedQuantity","totalTrades")))
    if len(signatures)!=1:return "CONFLICTING_OFFICIAL_EVIDENCE"
    h,l,c,v,t=next(iter(signatures))
    if t<=0 or v<=0:return "NO_POSITIVE_EXECUTION"
    if (h,l,c,v)!=values[1:]:return "HLCV_MISMATCH"
    return "HLCV_MATCH_OPEN_UNVERIFIED"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",required=True)
    root=Path(p.parse_args().directory)
    evidence=load_evidence()
    counts=Counter()
    symbols=set()
    with (root/"repeat_calendar_triage.csv").open(newline="") as src,(root/"open_pair_security_evidence.csv").open("w",newline="") as dst:
        w=csv.writer(dst)
        w.writerow(["symbol","date","previous_date","path","blob_sha","row","previous_row","open","high","low","close","volume","current_result","previous_result","current_evidence","previous_evidence","promotion_allowed"])
        for r in csv.DictReader(src):
            if r["pair_classification"]!="BOTH_OPEN_TUPLE_UNVERIFIED":continue
            symbol=r["symbol"]
            symbols.add(symbol)
            source=source_rows(r["path"],r["blob_sha"])
            day,values=source[r["row"]]
            prior,old=source[r["previous_row"]]
            if values!=old or day!=r["date"] or prior!=r["previous_date"]:raise ValueError("lineage mismatch")
            current=evidence[(symbol,day)]
            previous=evidence[(symbol,prior)]
            a,b=compare(values,current),compare(old,previous)
            counts[a+" | "+b]+=1
            w.writerow([symbol,day,prior,r["path"],r["blob_sha"],r["row"],r["previous_row"],*values,a,b,";".join(x[0]+":"+x[1] for x in current),";".join(x[0]+":"+x[1] for x in previous),"false"])
    if sum(counts.values())!=73:raise ValueError("pair count mismatch")
    summary={"pairs":73,"symbols":sorted(symbols),"results":dict(counts),"promoted":0,"limitations":"Official history supplies HLCV and execution counts, not opening price. Missing capture is not proof of no trade. No floorsheet validation or canonical correction."}
    (root/"open_pair_security_summary.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary))
if __name__=="__main__":main()
