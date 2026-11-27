"""Test odd-lot hypothesis on pinned April transactions; no promotion."""
import csv,json
from decimal import Decimal
from collections import Counter
from pathlib import Path
from validate_historical_floorsheets import download_one,validate_file
def main():
    out=Path("april-lot-evidence");out.mkdir(exist_ok=True)
    base=json.loads(Path("reference/APRIL_2026_CANDLE_RECONSTRUCTION_ADJUDICATION_2026-11-27.json").read_text())
    with open("reference/p419_observed_date_floorsheet_archive_inventory_2026-11-26.csv",newline="") as f:
        items=[r for r in csv.DictReader(f) if r["date"] in {x["date"] for x in base["rows"]} and r["inventory_status"]=="FILE_PRESENT_IN_PINNED_GIT_TREE"]
    assert len(items)==4
    report=[]
    for item in items:
        day=item["date"]; d=download_one(item,out)
        if d["download_status"]!="PASS":raise RuntimeError(d)
        targets=[x for x in base["rows"] if x["date"]==day]
        with open(d["path"],newline="",encoding="utf-8-sig") as f: rows=list(csv.DictReader(f))
        for target in targets:
            s=target["symbol"]; original=target["original"]
            trades=[r for r in rows if r["symbol"].strip().upper()==s]
            parsed=[(Decimal(r["quantity"]),Decimal(r["rate"]),r["transaction"]) for r in trades]
            assert all(q>0 and q==q.to_integral_value() and p>0 for q,p,_ in parsed)
            assert len({i for _,_,i in parsed})==len(parsed)
            regular=[(q,p,i) for q,p,i in parsed if q>=10]
            odd=[(q,p,i) for q,p,i in parsed if q<10]
            below=[(q,p,i) for q,p,i in parsed if p<Decimal(str(original[2]))]
            ordered=sorted(regular,key=lambda x:int(x[2]))
            r=dict(date=day,symbol=s,source_sha256=d["actual_sha256"],original=original,all_contracts=len(parsed),regular_contracts=len(regular),odd_contracts=len(odd),all_volume=str(sum(q for q,p,i in parsed)),regular_volume=str(sum(q for q,p,i in regular)),odd_volume=str(sum(q for q,p,i in odd)),below_published_low=[dict(quantity=str(q),rate=str(p),contract=i) for q,p,i in below],all_below_low_are_under_10=bool(below) and all(q<10 for q,p,i in below),promotion_allowed=False)
            if regular:
                r.update(regular_high=str(max(p for q,p,i in regular)),regular_low=str(min(p for q,p,i in regular)),regular_open_by_id=str(ordered[0][1]),regular_close_by_id=str(ordered[-1][1]),regular_low_matches_published=min(p for q,p,i in regular)==Decimal(str(original[2])))
            report.append(r)
    assert len(report)==11
    result=dict(rows=report,limitations="Quantity threshold is a proxy, not authenticated trade type; contract ID ordering is unverified, and independent completeness not established.",verified_replacements=0)
    (out/"report.json").write_text(json.dumps(result,indent=2))
    print(json.dumps(result))
if __name__=="__main__":main()
