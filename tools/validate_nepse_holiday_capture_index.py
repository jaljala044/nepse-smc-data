#!/usr/bin/env python3
"""Validate the immutable NEPSE holiday-capture evidence index."""
import argparse, json, re
from pathlib import Path
EXPECTED = {"SHA256SUMS","capture-report.json","parsed-response.json","response-body.bin","response-headers.json","source-url.txt"}
SHA = re.compile(r"^[0-9a-f]{40}$")
def validate(d):
    e=[]
    pin="39747bd2ade2bdb59ef7665f454bcbc04b3060df"
    if d.get("immutable_source_commit") != pin: e.append("source commit is not pinned")
    years=d.get("annual_captures",[])
    if [x.get("year") for x in years] != list(range(2015,2027)): e.append("expected annual captures for 2015-2026")
    urls=[]
    for y in years:
        files=y.get("files",[])
        names=[f.get("name") for f in files]
        if set(names)!=EXPECTED or len(names)!=6: e.append(f"{y.get('year')}: expected six capture files")
        for f in files:
            if not SHA.fullmatch(f.get("git_blob_sha","")): e.append(f"{y.get('year')}/{f.get('name')}: invalid blob SHA")
            u=f.get("url","")
            if pin not in u or f"/{y.get('year')}-11-25/" not in u: e.append(f"{y.get('year')}/{f.get('name')}: URL not immutable/pinned")
            urls.append(u)
    if len(urls)!=72 or len(set(urls))!=72: e.append("expected 72 unique immutable URLs")
    a=d.get("audit_summary",{})
    if (a.get("http_200_years"),a.get("total_records"),a.get("unique_dates"),a.get("duplicate_date"),a.get("capture_integrity_failures")) != (12,499,498,"2020-04-13",0): e.append("archive audit totals differ")
    c=d.get("calendar_616_recovery",{})
    if c.get("exact_date_list_recovered") is not False or c.get("independently_reproduced") is not False or c.get("confirmed_sessions_promoted") != 0: e.append("must preserve unrecovered 616-session status")
    return e
def main():
    p=argparse.ArgumentParser(); p.add_argument("manifest",type=Path); a=p.parse_args()
    errors=validate(json.loads(a.manifest.read_text(encoding="utf-8")))
    if errors: raise SystemExit("\n".join(errors))
    print("PASS: 12 annual captures, 72 pinned evidence references, archive controls and 616 UNKNOWN status")
if __name__=="__main__": main()
