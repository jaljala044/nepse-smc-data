"""Evidence-only comparison of historical index exceptions; no promotion."""
import csv,json,io,hashlib,urllib.request
from decimal import Decimal, InvalidOperation
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from p443_index_discrepancy_audit import inspect,manifest
from p443_index_correction_overlay import classify,valid
REPO="menaceXnadin/nepse-historical-market-data-csv"
REV="7e95d749f267a7d32a8d7e0a160eb708c01fbf8c"
PINS=json.loads('''{"Finance_index":{"path":"data/subindices/unadjusted/FINANCE_unadjusted.csv","blob":"19bc5d5addcacf7caba7d81ef822a7df7112aea1","size":229465},"Others_index":{"path":"data/subindices/unadjusted/OTHERS_unadjusted.csv","blob":"889e8397786a31cdf82f9f588edf21df0798d69c","size":223448},"Trading_index":{"path":"data/subindices/unadjusted/TRADING_unadjusted.csv","blob":"2372eda1dec364ff156b35d592f301d55e40eba9","size":148303},"Investment_index":{"path":"data/subindices/unadjusted/INVESTMENT_unadjusted.csv","blob":"1c6a11bcd8e0091b69ea6700c7bacaf20c8cea3c","size":87723},"Banking_index":{"path":"data/subindices/unadjusted/BANKING_unadjusted.csv","blob":"b129bf8b423827b9cf8d103d856d2480cb4ad607","size":235718},"HydroPower_index":{"path":"data/subindices/unadjusted/HYDROPOWER_unadjusted.csv","blob":"9b172504d885b5395e115c75db6387293250404f","size":247861},"Microfinance_index":{"path":"data/subindices/unadjusted/MICROFINANCE_unadjusted.csv","blob":"4f1962ac41f6812982c5f74b64b45d837b983d35","size":154247},"Float_index":{"path":"data/index/unadjusted/FLOAT_unadjusted.csv","blob":"cd10790e30f81b0631d223bbf2bd652dc6ffc634","size":197618},"Hotels%20and%20Tourism_index":{"path":"data/subindices/unadjusted/HOTELS_unadjusted.csv","blob":"1979ad85827b57c0f04502a743f675e8f906fc03","size":219392},"Non%20Life%20Insurance_index":{"path":"data/subindices/unadjusted/NONLIFEINSU_unadjusted.csv","blob":"58b23a9e456968d228637b031a1387feadebd8ce","size":144041},"Life%20Insurance_index":{"path":"data/subindices/unadjusted/LIFEINSU_unadjusted.csv","blob":"90004e69c26f555cecd024f631b9bf814ada6fe9","size":138944},"Development%20Bank_index":{"path":"data/subindices/unadjusted/DEVBANK_unadjusted.csv","blob":"a835229c89dc3239020df913a2225f179c8b973f","size":224834},"Mutual%20Fund_index":{"path":"data/subindices/unadjusted/MUTUAL_unadjusted.csv","blob":"b4852cb5e60e06b4e0bdd757e13852b4ceb531ab","size":99892},"Sensitive_index":{"path":"data/index/unadjusted/SENSITIVE_unadjusted.csv","blob":"15d8c12822163de9e62060903e05787896d11d6c","size":217529},"Sen.%20Float_index":{"path":"data/index/unadjusted/SENFLOAT_unadjusted.csv","blob":"d497e52aad15180dec45f9a80cf2a805352127c3","size":206834}}''')
def acquire(item):
    symbol,pin=item
    url=f"https://raw.githubusercontent.com/{REPO}/{REV}/{pin['path']}"
    try:
        with urllib.request.urlopen(url,timeout=60) as response: raw=response.read()
        blob=hashlib.sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest()
        if blob!=pin["blob"] or len(raw)!=pin["size"]: raise ValueError("pin mismatch")
        rows={}
        for r in csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))):
            rows.setdefault(r["time"],[]).append(r)
        return symbol,dict(**pin,url=url,sha256=hashlib.sha256(raw).hexdigest(),rows=rows,status="PASS")
    except Exception as e:return symbol,dict(**pin,error=str(e),rows={},status="FAIL")
if __name__=="__main__":
    with ThreadPoolExecutor(max_workers=8) as pool:
        sources=dict(pool.map(acquire,PINS.items()))
        results=list(pool.map(inspect,manifest["rows"]))
    out=[]
    for r in results:
        for v in r["violations"]:
            if v["symbol"]=="NEPSE_index" or classify(v)["rounding_candidate"]:continue
            source=sources.get(v["symbol"],{"rows":{},"status":"UNMAPPED"})
            matches=source["rows"].get(r["date"],[])
            candidate=None
            status="SOURCE_MISSING_OR_UNAVAILABLE"
            if len(matches)>1:status="DUPLICATE_SOURCE_DATE"
            elif len(matches)==1:
                x=matches[0];candidate={k:x[k] for k in ("open","high","low","close","volume")}
                try:
                    o,h,l,c,z=(Decimal(candidate[k]) for k in ("open","high","low","close","volume"))
                    status="SECONDARY_VALID_OHLC_CANDIDATE" if valid(o,h,l,c) and z.is_finite() and z>=0 else "SECONDARY_INVALID_OHLC"
                    if all(Decimal(candidate[k])==Decimal(v[k]) for k in ("open","high","low","close")):status="SAME_INVALID_OHLC"
                except (InvalidOperation,ValueError):status="SECONDARY_INVALID_OHLC"
            out.append(dict(date=r["date"],symbol=v["symbol"],original=v,source_sha256=r["index_sha256"],alternate=candidate,alternate_path=source.get("path"),alternate_blob=source.get("blob"),status=status,promotion_allowed=False))
    assert len(out)==169 and len({(r["date"],r["symbol"]) for r in out})==169
    report=dict(source_repository=REPO,source_revision=REV,counts=dict(Counter(r["status"] for r in out)),by_symbol={s:dict(Counter(r["status"] for r in out if r["symbol"]==s)) for s in sorted({r["symbol"] for r in out})},sources={k:{a:b for a,b in v.items() if a!="rows"} for k,v in sources.items()},records=out,promotion_allowed=False)
    Path("sector-external-recovery.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(dict(counts=report["counts"],by_symbol=report["by_symbol"],source_status={k:v["status"] for k,v in sources.items()})))
