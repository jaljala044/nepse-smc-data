"""Compare secondary archived trades without repairing contract identifiers."""
import csv,gzip,hashlib,io,json,re
from collections import Counter
from decimal import Decimal
from pathlib import Path
from capture_p433_first_trade_floorsheets import fetch,BASE,tree_metadata,pick

DATES={"2026-06-29","2026-07-01","2026-08-24","2026-08-25","2026-08-26"}
def broker(row,side):
    for k in (side,side+"_broker",side+"_broker_id",side+"_broker_no",side+"_broker_number",side+"_broker_name"):
        if row.get(k):return row[k]
    return ""
def norm(s):
    return Decimal(str(s).replace(",",""))
def main():
    out=Path("secondary-evidence")
    out.mkdir(exist_ok=True)
    with open("reference/P443_PRIORITY_CONTRACT_OBSERVATIONS_2026-11-27.csv",newline="") as f:
        primary=[r for r in csv.DictReader(f) if r["date"] in DATES]
    assert len(primary)==5 and {r["date"] for r in primary}==DATES
    meta=tree_metadata()
    report=[]
    for p in primary:
        day=p["date"]
        path=f"floorsheet/{day}.csv.gz"
        result={"date":day,"symbol":p["symbol"],"primary_contract":p["contract"],"source_url":BASE+path,"promotion_allowed":False}
        try:
            m=meta[path]
            status,_,data=fetch(BASE+path)
            digest=hashlib.sha256(data).hexdigest()
            result.update(sha256=digest,expected_sha256=m["lfs"]["oid"],bytes=len(data))
            if status!=200 or digest!=m["lfs"]["oid"] or len(data)!=m["size"]:raise ValueError("source integrity mismatch")
            reader=csv.DictReader(io.StringIO(gzip.decompress(data).decode("utf-8-sig")))
            ids=Counter()
            target=[]
            invalid=0
            total=0
            for r in reader:
                total+=1
                r={str(k).strip().lower():str(v or "").strip() for k,v in r.items()}
                cid=pick(r,"contract_no")
                ids[cid]+=1
                try:
                    q,rate,amt=(norm(pick(r,k)) for k in ("quantity","rate","amount"))
                    if not cid or pick(r,"date")[:10]!=day or q<=0 or q!=q.to_integral_value() or rate<=0 or abs(q*rate-amt)>Decimal("0.01"):invalid+=1
                except Exception:invalid+=1
                if pick(r,"symbol").upper()==p["symbol"]:target.append(r)
            matches=[]
            for r in target:
                try:
                    numeric=all(norm(pick(r,k))==norm(p[k]) for k in ("quantity","rate","amount"))
                except Exception:numeric=False
                b,s=broker(r,"buyer"),broker(r,"seller")
                cid=pick(r,"contract_no")
                matches.append({"raw":r,"numeric_match":numeric,"contract_match":cid==p["contract"],"broker_match":b==p["buyer"] and s==p["seller"],"contract_occurrences":ids[cid]})
            duplicate=sum(n-1 for n in ids.values() if n>1)
            result.update(total_rows=total,duplicate_contract_occurrences=duplicate,invalid_rows=invalid,headers=reader.fieldnames,target_rows=len(target),observations=matches)
            if len(matches)==1 and all(matches[0][k] for k in ("numeric_match","contract_match","broker_match")) and matches[0]["contract_occurrences"]==1 and not invalid and not duplicate:result["status"]="EXACT_SECONDARY_MATCH"
            elif any(x["numeric_match"] for x in matches):result["status"]="NUMERIC_MATCH_IDENTITY_OR_FILE_REVIEW"
            else:result["status"]="NO_MATCH_OR_CONFLICT"
        except Exception as e:result.update(status="UNAVAILABLE_OR_INTEGRITY_FAILED",error=str(e))
        report.append(result)
    summary={"records":report,"counts":dict(Counter(x["status"] for x in report)),"limitations":"Independent publication does not establish independent upstream lineage. No canonical promotion, no inference of no trade from absence."}
    (out/"secondary_comparison.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary))
if __name__=="__main__":main()
