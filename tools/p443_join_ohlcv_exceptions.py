import csv,json,zipfile,ast,re
from decimal import Decimal
from pathlib import Path
from collections import Counter
import argparse
p=argparse.ArgumentParser()
p.add_argument("artifact")
p.add_argument("--output",default="p443_exception_join.csv")
a=p.parse_args()
root=Path("reference")
names=["AHPC","API","CHL","HIDCL","MERO","SKBBL","SPDL","remaining_six_equity"]
index={}
for name in names:
    with (root/(name+"_ohlc_exception_register_2026-11-26.csv")).open(newline="") as f:
        for r in csv.DictReader(f):
            key=(r["symbol"],r["date"],r["source_blob_sha"],tuple(Decimal(r[k]) for k in ("open","high","low","close","volume")))
            index.setdefault(key,[]).append(name)
counts=Counter()
matched=set()
with zipfile.ZipFile(a.artifact) as z,open(a.output,"w",newline="") as out:
    w=csv.writer(out)
    w.writerow(["symbol","date","blob_sha","row","open","high","low","close","volume","disposition","registers"])
    for line in z.open("findings.jsonl"):
        r=json.loads(line)
        if r["classification"]!="invalid_ohlcv":continue
        _,_,symbol,day=ast.literal_eval(r["key"])
        values=tuple(Decimal(v) for v in re.findall(r"Decimal\('([^']+)'\)",r["evidence"]))
        if len(values)!=5:raise ValueError("unexpected tuple")
        key=(symbol,day,r["blob_sha"],values)
        status="EXACT_REGISTER_MATCH" if key in index else "UNMATCHED_REVIEW"
        if key in index:matched.add(key)
        counts[status]+=1
        w.writerow([symbol,day,r["blob_sha"],r["row"],*values,status,";".join(index.get(key,[]))])
print(json.dumps({"findings":dict(counts),"register_unique_keys":len(index),"register_keys_not_matched":len(set(index)-matched)}))
