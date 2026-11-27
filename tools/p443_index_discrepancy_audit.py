import csv,json,sys,tempfile
from decimal import Decimal,InvalidOperation
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from validate_historical_floorsheets import download_one
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/"reference/P443_391_PRIORITY_ARCHIVE_INVENTORY_2026-11-27.json").read_text())
def inspect(row):
    day=row["date"]
    out={"date":day,"index_status":"MISSING","violations":[],"rejected_contracts":[],"promotion_allowed":False}
    with tempfile.TemporaryDirectory() as tmp:
        def fetch(item):
            return download_one(dict(date=day,source_commit=manifest["source_commit"],source_repository="socrateai-official/nepse-open-data",path=item["path"],size_bytes=item["bytes"],git_blob_sha=item["blob"]),Path(tmp))
        if row["index"]:
            d=fetch(row["index"])
            out["index_status"]=d["download_status"]
            out["index_sha256"]=d.get("actual_sha256")
            if d["download_status"]=="PASS":
                with open(d["path"],newline="",encoding="utf-8-sig") as h:
                    for r in csv.DictReader(h):
                        try:
                            o,hi,lo,c,v=(Decimal(r[k]) for k in ("open","high","low","close","volume"))
                            if not all(x.is_finite() for x in (o,hi,lo,c,v)) or min(o,hi,lo,c)<=0 or v<0:
                                kind="NONFINITE_OR_NONPOSITIVE";gap=None
                            else:
                                gap=max(Decimal(0),max(o,c,lo)-hi,lo-min(o,c,hi))
                                if not gap:continue
                                kind="WITHIN_0_005_ROUNDING_CANDIDATE" if gap<=Decimal("0.005") else "WITHIN_0_01_ROUNDING_CANDIDATE" if gap<=Decimal("0.01") else "MATERIAL_BOUNDS_VIOLATION"
                            out["violations"].append(dict(symbol=r["symbol"],open=r["open"],high=r["high"],low=r["low"],close=r["close"],volume=r["volume"],gap=str(gap) if gap is not None else None,classification=kind))
                        except (InvalidOperation,KeyError,ValueError):out["violations"].append(dict(classification="MALFORMED"))
        if day in ("2024-12-01","2026-11-26"):
            d=fetch(row["floor"]);out["floor_download"]=d["download_status"];out["floor_sha256"]=d.get("actual_sha256")
            if d["download_status"]=="PASS":
                totals={}
                with open(d["path"],newline="",encoding="utf-8-sig") as h:
                    for r in csv.DictReader(h):
                        rate,amount=Decimal(r["rate"]),Decimal(r["amount"])
                        if rate<=0 or amount<=0:
                            out["rejected_contracts"].append({k:r.get(k) for k in ("transaction","symbol","quantity","rate","amount","date")})
                        symbol=r["symbol"];totals[symbol]=totals.get(symbol,Decimal(0))+amount
                if day=="2026-11-26":
                    target=Decimal("881363.60")
                    out["turnover_exact_single_symbol_matches"]=[s for s,v in totals.items() if v==target]
                    out["turnover_by_symbol"]={s:str(v) for s,v in sorted(totals.items())}
    return out
if __name__=="__main__":
    with ThreadPoolExecutor(max_workers=8) as pool: results=list(pool.map(inspect,manifest["rows"]))
    counts=Counter(v["classification"] for r in results for v in r["violations"])
    report=dict(dates=len(results),counts=dict(counts),failed_downloads=[r["date"] for r in results if r["index_status"]=="FAIL"],results=results,promotion_allowed=False)
    Path("index-discrepancy-audit.json").write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!="results"}))
    print(json.dumps([r for r in results if r["rejected_contracts"]]))
