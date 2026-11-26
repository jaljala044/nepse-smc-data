"""Retrieve ten pinned floorsheet partitions and validate priority equity executions."""
import csv,json,argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from pathlib import Path
from validate_historical_floorsheets import download_one,validate_file

TARGETS={
"2026-11-13":("BNL","14000"),"2026-11-17":("BNL","14000"),
"2026-06-29":("BNT","11600"),"2026-07-01":("BNT","11600"),
"2026-08-25":("ENL","833.90"),"2026-08-26":("ENL","833.90"),
"2026-08-24":("UNL","47200"),"2026-08-27":("UNL","47200"),
"2026-09-28":("UNL","48000"),"2026-09-29":("UNL","48000")}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    root=Path(p.parse_args().output)
    root.mkdir(parents=True,exist_ok=True)
    raw=root/"raw"
    raw.mkdir(exist_ok=True)
    with open("reference/p419_observed_date_floorsheet_archive_inventory_2026-11-26.csv",newline="") as f:
        items=[r for r in csv.DictReader(f) if r["date"] in TARGETS and r["inventory_status"]=="FILE_PRESENT_IN_PINNED_GIT_TREE"]
    if len(items)!=10 or {r["date"] for r in items}!=set(TARGETS):raise ValueError("inventory coverage mismatch")
    with ThreadPoolExecutor(max_workers=4) as pool:
        downloads=list(pool.map(lambda x:download_one(x,raw),items))
    results=[]
    contracts=[]
    for item,d in zip(items,downloads):
        day=item["date"]
        symbol,price=TARGETS[day]
        price=Decimal(price)
        summary,_=validate_file(item,d,{symbol},{(symbol,day):10},{})
        result=dict(date=day,symbol=symbol,expected_volume=10,expected_price=str(price),download_status=d["download_status"],file_validation=summary,source_url=d.get("url"),source_blob=item["git_blob_sha"],promotion_allowed=False)
        if d["download_status"]!="PASS":
            result["status"]="DOWNLOAD_FAILED"
        elif summary["content_status"]!="PASS":
            result["status"]="FILE_INTEGRITY_REVIEW"
        else:
            with open(d["path"],newline="",encoding="utf-8-sig") as f:
                rows=[r for r in csv.DictReader(f) if r["symbol"].strip().upper()==symbol]
            qty=sum((Decimal(r["quantity"].replace(",","")) for r in rows),Decimal(0))
            amount=sum((Decimal(r["amount"].replace(",","")) for r in rows),Decimal(0))
            rates=[Decimal(r["rate"].replace(",","")) for r in rows]
            match=bool(rows and qty==10 and all(v==price for v in rates) and amount==qty*price)
            result.update(contracts=len(rows),volume=str(qty),turnover=str(amount),status="THIRD_PARTY_CONTRACT_MATCH" if match else "NO_OBSERVED_CONTRACT" if not rows else "OHLCV_CONFLICT")
            for r in rows:
                contracts.append(dict(date=day,symbol=symbol,contract=r["transaction"],buyer=r["buyer"],seller=r["seller"],quantity=r["quantity"],rate=r["rate"],amount=r["amount"],source_blob=item["git_blob_sha"],status=result["status"],promotion_allowed="false"))
        results.append(result)
    with (root/"priority_contract_observations.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["date","symbol","contract","buyer","seller","quantity","rate","amount","source_blob","status","promotion_allowed"])
        w.writeheader()
        w.writerows(contracts)
    report=dict(requests=10,status_counts=dict(Counter(r["status"] for r in results)),results=results,downloads=downloads,limitations="Single third-party archive. No independent completeness proof; absence is unknown. No canonical promotion. Raw downloads are retained only in runner workspace.")
    (root/"priority_floorsheet_summary.json").write_text(json.dumps(report,indent=2,default=str))
    print(json.dumps(report,default=str))
if __name__=="__main__":main()
