import csv, json, math, sys, tempfile
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from validate_historical_floorsheets import download_one, validate_file
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/"reference/P443_391_PRIORITY_ARCHIVE_INVENTORY_2026-11-27.json").read_text())
def check(row):
    day=row["date"]
    with tempfile.TemporaryDirectory() as tmp:
        out=Path(tmp)
        def fetch(entry):
            return download_one(dict(date=day,source_commit=manifest["source_commit"],source_repository="socrateai-official/nepse-open-data",path=entry["path"],size_bytes=entry["bytes"],git_blob_sha=entry["blob"]),out)
        f=fetch(row["floor"])
        try:
            summary,_=validate_file(dict(date=day,path=row["floor"]["path"]),f,[],{}, {})
        except Exception as exc:
            summary={"content_status":"FAIL","error":str(exc)}
        idx={"status":"MISSING"}
        if row["index"]:
            i=fetch(row["index"])
            idx={"status":"DOWNLOAD_FAIL","sha256":i.get("actual_sha256")}
            if i["download_status"]=="PASS":
                errors=Counter();seen=set();main=None
                with Path(i["path"]).open(newline="",encoding="utf-8-sig") as h:
                    for r in csv.DictReader(h):
                        try:
                            symbol=r["symbol"]
                            if symbol in seen:errors["duplicate_symbol"]+=1
                            seen.add(symbol)
                            if r["date"]!=day:errors["date_mismatch"]+=1
                            o,hi,lo,c,v=(float(r[k]) for k in ("open","high","low","close","volume"))
                            if not all(math.isfinite(x) for x in (o,hi,lo,c,v)) or min(o,hi,lo,c)<=0 or v<0 or hi<max(o,lo,c) or lo>min(o,hi,c):errors["invalid_ohlcv"]+=1
                            if symbol=="NEPSE_index":main=dict(open=o,high=hi,low=lo,close=c,volume=v)
                        except (KeyError,ValueError,TypeError):errors["malformed"]+=1
                if main is None:errors["missing_nepse"]+=1
                idx.update(status="PASS" if not errors else "FAIL",errors=dict(errors),symbols=len(seen),nepse=main)
        return dict(date=day,floor_download=f["download_status"],floor=summary,index=idx,promotion_allowed=False)
if __name__=="__main__":
    batch=sys.argv[1]
    rows=[r for r in manifest["rows"] if r["date"].startswith(batch)]
    assert rows
    with ThreadPoolExecutor(max_workers=4) as pool: results=list(pool.map(check,rows))
    report=dict(batch=batch,dates=len(rows),floor_status=dict(Counter(r["floor"].get("content_status") for r in results)),index_status=dict(Counter(r["index"]["status"] for r in results)),results=results,promotion_allowed=False)
    Path("priority-validation-"+batch+".json").write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!="results"}))
    if len(rows)==1: print(json.dumps(results))
