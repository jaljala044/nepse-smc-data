"""Research-only reconstruction from pinned public CSVs; never promote."""
import csv,json,re
from pathlib import Path
from decimal import Decimal
from collections import Counter,defaultdict
from validate_historical_floorsheets import download_one,validate_file
TARGETS={
"2026-04-24":{"MERO":1671,"UAIL":4553},
"2026-04-27":{"API":206969,"RAWA":3747},
"2026-04-28":{"SPDL":64356},
"2026-04-29":{"RADHI":57510,"RAWA":2840,"UAIL":9360,"UNHPL":46481,"BGWT":1573,"HRL":74867}}
EXPECTED={"2026-04-24":(75229,12174516,"5270399727.64"),"2026-04-27":(81006,10928617,"4748809127.76"),"2026-04-28":(151354,14018920,"6531723226.36"),"2026-04-29":(104004,12133360,"4986294173.38")}
def main():
    out=Path("april-evidence");out.mkdir(exist_ok=True)
    raw=out/"raw";raw.mkdir(exist_ok=True)
    with open("reference/p419_observed_date_floorsheet_archive_inventory_2026-11-26.csv",newline="") as f:
        items=[r for r in csv.DictReader(f) if r["date"] in TARGETS and r["inventory_status"]=="FILE_PRESENT_IN_PINNED_GIT_TREE"]
    assert len(items)==4 and {r["date"] for r in items}==set(TARGETS)
    results=[]
    for item in items:
        day=item["date"]; targets=TARGETS[day]
        d=download_one(item,raw)
        summary,_=validate_file(item,d,set(targets),{(s,day):v for s,v in targets.items()},{})
        result={"date":day,"download":d,"validation":summary,"candidates":[],"promotion_allowed":False}
        results.append(result)
        if d["download_status"]!="PASS":continue
        expected=EXPECTED[day]
        result["saved_archive_totals_match"]=(summary["trades"],summary["shares"],Decimal(summary["turnover_npr"]))==(expected[0],expected[1],Decimal(expected[2]))
        with open(d["path"],newline="",encoding="utf-8-sig") as f:
            reader=csv.DictReader(f)
            result["columns"]=reader.fieldnames
            selected=defaultdict(list); rejected=[]
            for row in reader:
                symbol=row["symbol"].strip().upper()
                if Decimal(row["rate"].replace(",",""))<=0:
                    rejected.append({"symbol":symbol,"contract":row["transaction"],"rate":row["rate"]})
                if symbol in targets:selected[symbol].append(row)
        result["nonpositive_rate_rows"]=rejected
        for s,vol in targets.items():
            rows=selected[s]; c={"symbol":s,"expected_volume":vol,"observed_contracts":len(rows),"promotion_allowed":False,"status":"HOLD"};result["candidates"].append(c)
            if not rows:continue
            try:
                prices=[Decimal(r["rate"].replace(",","")) for r in rows]
                quantities=[Decimal(r["quantity"].replace(",","")) for r in rows]
                if any(not p.is_finite() or p<=0 for p in prices) or any(not q.is_finite() or q<=0 or q!=q.to_integral_value() for q in quantities):continue
                ids=[r["transaction"].strip() for r in rows]
                if len(set(ids))!=len(ids):continue
                c.update(high=str(max(prices)),low=str(min(prices)),volume=str(sum(quantities)),volume_matches=sum(quantities)==vol)
                # Contract ID ordering is a hypothesis, not certified execution chronology.
                if all(re.fullmatch(r"[0-9]+",x) for x in ids) and len(set(map(int,ids)))==len(ids):
                    ordered=sorted(zip(map(int,ids),prices))
                    c.update(first_contract_id=str(ordered[0][0]),last_contract_id=str(ordered[-1][0]),open_by_contract_id=str(ordered[0][1]),close_by_contract_id=str(ordered[-1][1]),order_status="UNVERIFIED_CONTRACT_ID_ORDER")
                c["status"]="OBSERVED_RANGE_ONLY" if summary["content_status"]!="PASS" else "RESEARCH_CANDIDATE"
            except (ValueError,ArithmeticError,KeyError):c["status"]="INVALID_TARGET_ROWS"
    report={"sessions":results,"verified_replacements":0,"promotion_allowed":False,"limitations":"Pinned public CSV alternative; not a byte comparison to recovered Parquet. Independent market totals and execution chronology remain unverified."}
    (out/"report.json").write_text(json.dumps(report,indent=2,default=str))
    print(json.dumps(report,default=str))
    if any(r["download"]["download_status"]!="PASS" for r in results):raise SystemExit(1)
if __name__=="__main__":main()
