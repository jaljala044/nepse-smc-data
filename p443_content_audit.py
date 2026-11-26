"""Read-only pinned inventory content audit. Findings are review flags, not repairs."""
import argparse
import csv
import gzip
import hashlib
import io
import json
import subprocess
from collections import Counter
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

PIN = "56362fb4f65b91fdcca8f50b50e53ad80e703649"
INVENTORY = "reference/NEPSE_GLOBAL_DUPLICATE_AUDIT_INVENTORY.csv"

def norm(s):
    return ''.join(c for c in str(s).lower() if c.isalnum())

def records(raw, fmt):
    if fmt == "csv.gz":
        raw = gzip.decompress(raw)
    if fmt in ("csv", "csv.gz"):
        reader = csv.reader(io.StringIO(raw.decode("utf-8-sig")), strict=True)
        header = next(reader)
        keys = [norm(x) for x in header]
        if not all(keys) or len(set(keys)) != len(keys):
            raise ValueError("empty or duplicate normalized headers")
        for row in reader:
            if len(row) != len(keys):
                raise ValueError(f"row width mismatch at line {reader.line_num}")
            yield str(reader.line_num), dict(zip(keys, row))
    elif fmt == "json":
        if not raw.strip():
            return
        def walk(obj, pointer):
            if isinstance(obj, list):
                for i, item in enumerate(obj):
                    yield from walk(item, pointer + "/" + str(i))
            elif isinstance(obj, dict):
                scalar = {norm(k): str(v) for k,v in obj.items()
                          if v is not None and not isinstance(v,(dict,list))}
                if scalar:
                    yield pointer or "/", scalar
                for k,v in obj.items():
                    if isinstance(v,(dict,list)):
                        yield from walk(v, pointer + "/" + k.replace("~","~0").replace("/","~1"))
        yield from walk(json.loads(raw), "")
    else:
        raise ValueError("unsupported format")

def first(row, *keys):
    return next((str(row[k]).strip() for k in keys if row.get(k) not in (None,"")), "")

def non_json_capture(raw):
    text = raw.lstrip()
    return text.startswith(b"<html") or text.startswith(b"<!DOCTYPE html") or raw.strip().startswith(b"Searched Date is not valid.")

def scan(raw, entry):
    path = entry["path"]
    seen, business, previous = {}, {}, {}
    findings, schemas = [], Counter()
    count = 0
    def flag(kind, loc, key, other="", evidence=""):
        findings.append(dict(path=path, blob_sha=entry["git_blob_sha"], row=loc,
                             key=key, classification=kind, previous_row=other,
                             evidence=evidence, action="REVIEW_NO_MUTATION"))
    for loc, row in records(raw, entry["format"]):
        count += 1
        # JSON arrays are independent record scopes, not one global table.
        scope = loc.rsplit("/",1)[0] if entry["format"]=="json" else ""
        signature = json.dumps(row, sort_keys=True, ensure_ascii=False)
        sig = (scope, signature)
        if sig in seen:
            flag("exact_record_repeat",loc,"",seen[sig])
        else:
            seen[sig]=loc
        d = first(row,"date","tradedate","businessdate","holidaydate","sessiondate")
        symbol = first(row,"symbol","stocksymbol","scrip","securitysymbol")
        contract = first(row,"contractno","contractnumber","contractid","transactionid")
        fields=("open","high","low","close","volume")
        key = None
        if all(k in row for k in fields) and d:
            schemas["ohlcv"] += 1
            if not symbol and entry["category"]=="ohlcv_symbol_archive":
                symbol=Path(path).name.split("_OHLCV")[0]
            if symbol:
                key=("ohlcv",scope,symbol,d)
            try:
                dt=date.fromisoformat(d)
                values=tuple(Decimal(row[k]) for k in fields)
                o,h,l,c,v=values
                if not all(x.is_finite() for x in values) or min(o,h,l,c)<=0 or v<0 or h<max(o,l,c) or l>min(o,h,c):
                    flag("invalid_ohlcv",loc,str(key),evidence=str(values))
                if symbol:
                    prev=previous.get((scope,symbol))
                    if prev and prev[0]!=dt and prev[1]==values:
                        flag("repeated_adjacent_tuple_unresolved",loc,str(key),prev[2])
                    previous[(scope,symbol)]=(dt,values,loc)
            except (ValueError,InvalidOperation):
                flag("invalid_ohlcv_or_date",loc,str(key))
        elif contract:
            schemas["contract"] += 1
            if d:
                key=("contract",scope,d,contract)
            else:
                flag("contract_session_missing",loc,contract)
        elif d and entry["category"]=="session_calendar":
            schemas["calendar_candidate"] += 1
            key=("calendar",scope,d)
        else:
            schemas["unclassified"] += 1
        if key:
            if key in business:
                prior, old=business[key]
                flag("duplicate_business_key" if old==signature else "conflicting_business_key",
                     loc,str(key),prior)
            else:
                business[key]=(loc,signature)
    return count, dict(schemas), findings

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    args=p.parse_args()
    out=Path(args.output)
    out.mkdir(parents=True,exist_ok=True)
    coverage=[]; totals=Counter()
    with open(INVENTORY,newline="",encoding="utf-8") as f, (out/"findings.jsonl").open("w",encoding="utf-8") as sink:
        for entry in csv.DictReader(f):
            result=dict(path=entry["path"],blob_sha=entry["git_blob_sha"],records=0)
            try:
                if entry["commit_sha"]!=PIN:
                    raise ValueError("unexpected inventory commit")
                raw=subprocess.check_output(["git","show",PIN+":"+entry["path"]])
                sha=hashlib.sha1(("blob %d\0"%len(raw)).encode()+raw).hexdigest()
                if sha!=entry["git_blob_sha"] or len(raw)!=int(entry["bytes"]):
                    raise ValueError("pinned bytes mismatch")
                if entry["format"] not in ("csv","csv.gz","json"):
                    result["status"]="inventory_only"
                elif entry["format"]=="json" and not raw.strip():
                    result.update(status="empty_capture",records=0)
                elif entry["format"]=="json" and non_json_capture(raw):
                    result.update(status="non_json_response",records=0,error=raw[:160].decode("utf-8","replace"))
                else:
                    count,schemas,findings=scan(raw,entry)
                    result.update(status="parsed",records=count,schemas=schemas)
                    for finding in findings:
                        sink.write(json.dumps(finding,ensure_ascii=False)+"\n")
                        totals[finding["classification"]]+=1
            except (ValueError, OSError, subprocess.CalledProcessError, csv.Error, StopIteration, EOFError) as exc:
                result.update(status="failed",error=str(exc))
            coverage.append(result)
    summary=dict(pinned_commit=PIN,files=len(coverage),statuses=dict(Counter(x["status"] for x in coverage)),
                 parsed_records=sum(x["records"] for x in coverage),findings=dict(totals),
                 limitations=["Within-file checks only; no independent date or source adjudication.",
                              "Unclassified records are parsed but not business-key validated.",
                              "Non-JSON provider error bodies are recorded as non_json_response, not counted as parsed records.",
                              "Finding classes overlap; counts are not unique affected records.",
                              "No corrections or canonical promotion."])
    (out/"coverage.json").write_text(json.dumps(coverage,indent=2))
    (out/"summary.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))
    return int(any(x["status"]=="failed" for x in coverage))

if __name__=="__main__":
    raise SystemExit(main())
