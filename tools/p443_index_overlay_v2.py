"""Build research-only V2 from pinned source comparisons; never promote."""
import json
from collections import Counter
from pathlib import Path
from decimal import Decimal
from p443_index_correction_overlay import valid
ROOT=Path(__file__).resolve().parents[1]
def key(r):return (r["symbol"],r["date"])
def main():
    v1=json.loads(Path("index-correction-overlay-v1.json").read_text())
    sector=json.loads(Path("sector-external-recovery.json").read_text())
    bench=json.loads((ROOT/"reference/P443_BENCHMARK_BATCH_AD_RECOVERY_2026-11-27.json").read_text())
    s={key(r):r for r in sector["records"]}
    b={key(r):r for r in bench["records"]}
    assert len(s)==169 and len(b)==6
    out=[]
    for r in v1["records"]:
        k=key(r)
        candidate=None; evidence=None; status="UNRESOLVED"
        if r["rounding_candidate"]:
            candidate=r["rounding_candidate"];status="ROUNDING_CANDIDATE"
        elif k in s:
            evidence=s[k]
            if evidence["status"]=="SECONDARY_VALID_OHLC_CANDIDATE":
                candidate=evidence["alternate"];status="SECTOR_SOURCE_CANDIDATE"
        elif k in b:
            evidence=b[k]
            if evidence["status"]=="SECONDARY_SOURCE_CANDIDATE":
                candidate=dict(zip(("open","high","low","close"),evidence["ohlc"]));status="BENCHMARK_SOURCE_CANDIDATE"
        else:raise ValueError(k)
        out.append(dict(symbol=k[0],date=k[1],original=r["raw"],source_sha256=r["source_sha256"],candidate=candidate,evidence=evidence,status=status,promotion_allowed=False))
    missing=b[("NEPSE_index","2025-04-03")]
    out.append(dict(symbol=missing["symbol"],date=missing["date"],original=None,source_sha256=None,candidate=dict(zip(("open","high","low","close"),missing["ohlc"])),evidence=missing,status="BENCHMARK_SOURCE_CANDIDATE",promotion_allowed=False))
    assert len(out)==len(set(map(key,out)))==221
    counts=Counter(r["status"] for r in out)
    assert counts=={"ROUNDING_CANDIDATE":46,"SECTOR_SOURCE_CANDIDATE":162,"BENCHMARK_SOURCE_CANDIDATE":4,"UNRESOLVED":9},counts
    for r in out:
        if r["candidate"]:
            assert valid(*(Decimal(r["candidate"][k]) for k in ("open","high","low","close")))
    out.sort(key=key)
    Path("index-overlay-v2.json").write_text(json.dumps(dict(schema_version=2,counts=counts,records=out,promotion_allowed=False),indent=2))
    keys=[dict(symbol=r["symbol"],date=r["date"]) for r in out]
    Path("index-quarantine-v2.json").write_text(json.dumps(dict(schema_version=1,records=keys,promotion_allowed=False),indent=2))
    print(json.dumps(dict(counts=counts,keys=keys)))
if __name__=="__main__":main()
