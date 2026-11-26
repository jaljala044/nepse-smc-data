#!/usr/bin/env python3
"""Build/check exact-match reconciliation between official NEPSE IDs and OHLCV files."""
import argparse, csv, hashlib, json
from collections import Counter
from pathlib import Path

RAW_SHA="5495d99a73aeb44e573936f59fc6a6d8dbf9ffc45c5a8ba62e672f0b0c6fa2f7"
FIELDS=["record_type","symbol","ohlcv_file_stem","security_id","security_name","active_status_raw","has_ohlcv_file","ohlcv_path","instrument_type","valid_from","valid_to","disposition"]

def build(raw_path, ohlcv_dir, inventory_commit):
    raw=Path(raw_path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=RAW_SHA: raise ValueError("official security-list SHA-256 mismatch")
    official=json.loads(raw.decode("utf-8"))
    if not isinstance(official,list) or len(official)!=573: raise ValueError("expected 573 official security records")
    paths=sorted(Path(ohlcv_dir).glob("*_OHLCV.csv"))
    files={p.stem[:-6]:p.as_posix() for p in paths}
    if len(paths)!=525 or len(files)!=525: raise ValueError("expected 525 unique OHLCV file stems")
    by_symbol={}
    ids=set()
    for r in official:
        if not isinstance(r.get("id"),int) or not r.get("symbol") or r["symbol"] in by_symbol or r["id"] in ids:
            raise ValueError("invalid or duplicate official ID/symbol")
        if r.get("activeStatus") not in {"A","S"}: raise ValueError("unknown raw activeStatus code")
        by_symbol[r["symbol"]]=r; ids.add(r["id"])
    rows=[]
    for r in official:
        symbol=r["symbol"]; path=files.get(symbol)
        rows.append({"record_type":"official_security","symbol":symbol,"ohlcv_file_stem":symbol if path else "",
            "security_id":str(r["id"]),"security_name":r["securityName"],"active_status_raw":r["activeStatus"],
            "has_ohlcv_file":"true" if path else "false","ohlcv_path":path or "",
            "instrument_type":"UNKNOWN","valid_from":"UNKNOWN","valid_to":"UNKNOWN",
            "disposition":"OFFICIAL_MATCH_WITH_OHLCV" if path else "OFFICIAL_NO_OHLCV_FILE"})
    for stem,path in sorted(files.items()):
        if stem not in by_symbol:
            rows.append({"record_type":"ohlcv_file_only","symbol":"","ohlcv_file_stem":stem,"security_id":"UNKNOWN",
                "security_name":"UNKNOWN","active_status_raw":"UNKNOWN","has_ohlcv_file":"true","ohlcv_path":path,
                "instrument_type":"UNKNOWN","valid_from":"UNKNOWN","valid_to":"UNKNOWN",
                "disposition":"OHLCV_FILE_NO_OFFICIAL_MATCH"})
    counts=Counter(r["disposition"] for r in rows)
    missing=[r for r in official if r["symbol"] not in files]
    matched=[r for r in official if r["symbol"] in files]
    report={"audit":"P4.29 current official security-list vs OHLCV filename inventory",
      "source_security_list_commit":inventory_commit,
      "security_list_raw_sha256":RAW_SHA,"ohlcv_inventory_commit":inventory_commit,
      "ohlcv_directory":"03_stock_charts_ohlcv/","official_security_rows":len(official),
      "unique_official_symbols":len(by_symbol),"ohlcv_files":len(paths),"unique_ohlcv_file_stems":len(files),
      "disposition_counts":dict(counts),"official_matches_with_ohlcv":counts["OFFICIAL_MATCH_WITH_OHLCV"],
      "official_symbols_without_ohlcv_file":counts["OFFICIAL_NO_OHLCV_FILE"],
      "ohlcv_file_stems_without_official_symbol":counts["OHLCV_FILE_NO_OFFICIAL_MATCH"],
      "official_missing_ohlcv_by_status":{k:sum(r["activeStatus"]==k for r in missing) for k in ("A","S")},
      "official_matched_ohlcv_by_status":{k:sum(r["activeStatus"]==k for r in matched) for k in ("A","S")},
      "limitations":["Filename matching is exact only; escaped or transformed filenames are not normalized.",
       "The 37 OHLCV-only file stems are not mapped to official securities; aliases, delisted securities, funds and debentures remain unresolved.",
       "Instrument type and effective lifecycle dates are UNKNOWN because the official security-list endpoint did not return them.",
       "Raw activeStatus A/S codes are preserved without undocumented interpretation.",
       "This is a coverage inventory, not a canonical instrument-master promotion."]}
    return rows,report

def write_csv(rows):
    import io
    s=io.StringIO(newline="")
    w=csv.writer(s,lineterminator="\n",quoting=csv.QUOTE_ALL)
    w.writerows([[row.get(field,"") for field in FIELDS] for row in rows])
    return ",".join(FIELDS)+"\n"+s.getvalue()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--raw",required=True);p.add_argument("--ohlcv-dir",required=True)
    p.add_argument("--inventory-commit",required=True);p.add_argument("--csv",required=True)
    p.add_argument("--report",required=True);p.add_argument("--check",action="store_true")
    a=p.parse_args();rows,report=build(a.raw,a.ohlcv_dir,a.inventory_commit)
    csv_text=write_csv(rows);json_text=json.dumps(report,indent=2)+"\n"
    if a.check:
        if Path(a.csv).read_text(encoding="utf-8")!=csv_text:
            actual=Path(a.csv).read_text(encoding="utf-8").splitlines()
            expected=csv_text.splitlines()
            for i,(left,right) in enumerate(zip(actual,expected),1):
                if left!=right:
                    raise SystemExit("reconciliation CSV stale at line %s: committed=%r generated=%r" % (i,left[:220],right[:220]))
            raise SystemExit("reconciliation CSV line-count differs: committed=%s generated=%s" % (len(actual),len(expected)))
        if Path(a.report).read_text(encoding="utf-8")!=json_text: raise SystemExit("reconciliation report is stale")
        print("PASS: 573 official records, 525 files, 488 exact matches, 85 missing, 37 unmatched file stems")
    else:
        Path(a.csv).write_text(csv_text,encoding="utf-8")
        Path(a.report).write_text(json_text,encoding="utf-8")
if __name__=="__main__":main()
