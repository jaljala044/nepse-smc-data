"""Research overlay only: preserve original values, never invent extrema."""
import csv,json
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from p443_index_discrepancy_audit import inspect,manifest,ROOT

def valid(o,h,l,c):
    return all(x.is_finite() and x>0 for x in (o,h,l,c)) and h>=max(o,l,c) and l<=min(o,h,c)

def classify(v):
    raw={k:v[k] for k in ("open","high","low","close","volume")}
    o,h,l,c=(Decimal(raw[k]) for k in ("open","high","low","close"))
    rounded=[x.quantize(Decimal(".01"),rounding=ROUND_HALF_UP) for x in (o,h,l,c)]
    candidate=valid(*rounded) and Decimal(v["gap"])<=Decimal(".01")
    return dict(raw=raw,rounding_candidate={**dict(zip(("open","high","low","close"),map(str,rounded))),"volume":raw["volume"]} if candidate else None,
                status="ROUNDING_REPRESENTATION_VALID_REVIEW_REQUIRED" if candidate else "HOLD_SOURCE_RECOVERY",
                promotion_allowed=False)

if __name__=="__main__":
    with ThreadPoolExecutor(max_workers=8) as pool: results=list(pool.map(inspect,manifest["rows"]))
    out=[]
    for r in results:
        for v in r["violations"]:
            out.append(dict(date=r["date"],symbol=v.get("symbol"),source_sha256=r["index_sha256"],gap=v.get("gap"),classification=v["classification"],**classify(v)))
    assert len(out)==220 and len({(r["date"],r["symbol"]) for r in out})==220
    assert not any(r["index_status"]=="FAIL" for r in results)
    evidence=json.loads((ROOT/"reference/P443_BENCHMARK_EXTERNAL_RECOVERY_2026-11-27.json").read_text())
    report=dict(schema_version=1,counts=dict(Counter(r["status"] for r in out)),records=out,external_recovery=evidence,promotion_allowed=False,
                policy="Uniform rounding is a display representation, not proof of original trade extrema. No raw or canonical overwrite.")
    Path("index-correction-overlay-v1.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(dict(counts=report["counts"],total=len(out),benchmark=[r for r in out if r["symbol"]=="NEPSE_index"])))
