#!/usr/bin/env python3
"""Audit a dated official NEPSE security-list response against an equity crosswalk."""
import argparse, csv, hashlib, json
from collections import Counter
from pathlib import Path

EXPECTED_SHA256 = "5495d99a73aeb44e573936f59fc6a6d8dbf9ffc45c5a8ba62e672f0b0c6fa2f7"
EXPECTED_PARSED_BLOB = "eed3bbb3152e83d4abcb0ee8d03d720c33c63cef"

def audit(raw_path, crosswalk_path):
    raw_bytes=Path(raw_path).read_bytes()
    digest=hashlib.sha256(raw_bytes).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError("official security-list raw SHA-256 mismatch")
    records=json.loads(raw_bytes.decode("utf-8"))
    if not isinstance(records,list) or len(records)!=573:
        raise ValueError("expected 573 official security-list records")
    required={"id","symbol","securityName","name","activeStatus"}
    ids=[]; symbols=[]; status=Counter(); by_symbol={}
    for i,row in enumerate(records):
        if not isinstance(row,dict) or not required.issubset(row):
            raise ValueError(f"record {i}: missing required official fields")
        if not isinstance(row["id"],int) or not str(row["symbol"]).strip() or row["symbol"]!=row["symbol"].upper():
            raise ValueError(f"record {i}: invalid ID or symbol")
        if row["activeStatus"] not in {"A","S"}:
            raise ValueError(f"record {i}: unknown raw activeStatus code")
        ids.append(row["id"]); symbols.append(row["symbol"]); status[row["activeStatus"]]+=1
        if row["symbol"] in by_symbol: raise ValueError(f"duplicate official symbol {row['symbol']}")
        by_symbol[row["symbol"]]=row
    if len(set(ids))!=573: raise ValueError("duplicate official security IDs")
    with Path(crosswalk_path).open(encoding="utf-8-sig",newline="") as f:
        cross=list(csv.DictReader(f))
    if len(cross)!=281: raise ValueError("expected 281 current equity crosswalk rows")
    seen=set(); mismatches=[]
    for row in cross:
        symbol=row["symbol"]
        if symbol in seen: raise ValueError(f"duplicate crosswalk symbol {symbol}")
        seen.add(symbol)
        official=by_symbol.get(symbol)
        if official is None or str(official["id"])!=row["security_id"]:
            mismatches.append(symbol)
        if row.get("source_snapshot_blob_sha")!=EXPECTED_PARSED_BLOB:
            raise ValueError(f"{symbol}: crosswalk does not pin the reviewed official snapshot blob")
    if mismatches: raise ValueError("official security ID/symbol mismatch: "+", ".join(mismatches))
    return {
        "official_record_count":len(records),"unique_security_ids":len(set(ids)),
        "unique_symbols":len(set(symbols)),"raw_active_status_counts":dict(sorted(status.items())),
        "equity_crosswalk_rows":len(cross),"equity_crosswalk_matches":len(cross),
        "equity_crosswalk_mismatches":0,"raw_sha256":digest,
        "instrument_type":"UNKNOWN_NOT_RETURNED_BY_ENDPOINT",
        "lifecycle_dates":"UNKNOWN_NOT_RETURNED_BY_ENDPOINT",
        "historical_security_identity_verified":False,
        "promotion_allowed":False,
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--raw",required=True);p.add_argument("--crosswalk",required=True);a=p.parse_args()
    print(json.dumps(audit(a.raw,a.crosswalk),indent=2))
if __name__=="__main__":main()
