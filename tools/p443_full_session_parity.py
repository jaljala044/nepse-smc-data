"""Compare complete contract multisets across five hash-pinned published archives."""
import csv,gzip,hashlib,io,json
from collections import Counter
from decimal import Decimal
from pathlib import Path
from capture_p433_first_trade_floorsheets import fetch,BASE,tree_metadata,pick
from validate_historical_floorsheets import download_one
from p443_secondary_priority_comparison import DATES

def signature(r,secondary,day):
    get=lambda k:pick(r,k) if secondary else r[k if k!="contract_no" else "transaction"]
    cid=get("contract_no").strip()
    date=get("date")[:10]
    symbol=get("symbol").strip().upper()
    buyer,seller=(r[k].strip() for k in ("buyer","seller"))
    q,rate,amt=(Decimal(get(k).replace(",","")) for k in ("quantity","rate","amount"))
    if not cid.isdigit() or date!=day or not symbol or not buyer.isdigit() or not seller.isdigit() or not all(x.is_finite() for x in (q,rate,amt)) or q<=0 or q!=q.to_integral_value() or rate<=0 or amt<=0 or abs(q*rate-amt)>Decimal("0.01"):
        raise ValueError("invalid contract "+cid)
    return (date,cid,symbol,buyer,seller,q,rate,amt)

def parse(reader,secondary,day):
    counts=Counter()
    ids=Counter()
    for r in reader:
        key=signature(r,secondary,day)
        counts[key]+=1
        ids[key[1]]+=1
    if not counts or any(n!=1 for n in ids.values()):raise ValueError("empty file or duplicate contract")
    return counts

def main():
    out=Path("full-session-parity")
    out.mkdir(exist_ok=True)
    raw=out/"raw"
    raw.mkdir(exist_ok=True)
    with open("reference/p419_observed_date_floorsheet_archive_inventory_2026-11-26.csv",newline="") as f:
        items=[r for r in csv.DictReader(f) if r["date"] in DATES and r["inventory_status"]=="FILE_PRESENT_IN_PINNED_GIT_TREE"]
    if len(items)!=5 or {r["date"] for r in items}!=DATES:raise ValueError("inventory scope mismatch")
    meta=tree_metadata()
    results=[]
    for item in items:
        day=item["date"]
        result={"date":day,"promotion_allowed":False}
        try:
            d=download_one(item,raw)
            if d["download_status"]!="PASS":raise ValueError("primary download failed")
            path=f"floorsheet/{day}.csv.gz"
            status,_,data=fetch(BASE+path)
            digest=hashlib.sha256(data).hexdigest()
            m=meta[path]
            if status!=200 or digest!=m["lfs"]["oid"] or len(data)!=m["size"]:raise ValueError("secondary hash or size mismatch")
            with open(d["path"],newline="",encoding="utf-8-sig") as f:
                a=parse(csv.DictReader(f),False,day)
            b=parse(csv.DictReader(io.StringIO(gzip.decompress(data).decode("utf-8-sig"))),True,day)
            left,right=a-b,b-a
            result.update(primary_rows=a.total(),secondary_rows=b.total(),matched_rows=(a&b).total(),primary_only=left.total(),secondary_only=right.total(),primary_blob=item["git_blob_sha"],primary_sha256=d["actual_sha256"],secondary_sha256=digest,status="EXACT_PARITY" if a==b else "ROW_CONFLICT")
            with (out/f"differences_{day}.csv").open("w",newline="") as f:
                w=csv.writer(f)
                w.writerow(["source","date","contract","symbol","buyer","seller","quantity","rate","amount","count"])
                for side,c in (("primary",left),("secondary",right)):
                    for key,n in sorted(c.items()):w.writerow([side,*key,n])
        except Exception as e:result.update(status="UNAVAILABLE_OR_INVALID",error=str(e))
        results.append(result)
    report={"results":results,"counts":dict(Counter(r["status"] for r in results)),"matched_rows":sum(r.get("matched_rows",0) for r in results),"limitations":"Parity covers shared fields only; no timestamp parity, independent upstream provenance, official completeness or canonical promotion."}
    (out/"full_session_parity.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report))
    if any(r["status"]!="EXACT_PARITY" for r in results):raise SystemExit(1)
if __name__=="__main__":main()
