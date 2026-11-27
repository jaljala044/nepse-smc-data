"""Extract pinned secondary corporate-action candidates without adjustment approval."""
import csv
import hashlib
import io
import json
import re
import subprocess
from collections import Counter
from datetime import date
from decimal import Decimal
from pathlib import Path

SOURCE = "c9c7ae42cf10e4b110ec6ea32d0cf480bdc81b54"

def read(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))

def run(source, output):
    universe = read("reference/nepse_target_universe_candidates_2026-11-26.csv")
    target = {r["symbol"] for r in universe if r["instrument_class_from_rendered_list"] == "Equity"}
    target.update({"NESDO","ULBSL","YMHL"})
    inventory = read("reference/P443_CORPORATE_ACTION_SECONDARY_INVENTORY.csv")
    if len(target) != 281 or len(inventory) != 323 or len({r["path"] for r in inventory}) != 323:
        raise ValueError("Unexpected universe or inventory")
    events, files, seen = [], [], set()
    covered = set()
    for item in inventory:
        symbol, kind = item["symbol"], item["event_source"]
        path = item["path"]
        expected = f"data/company-wise/{symbol}/" + {"dividend":"dividend.csv","rights":"right-share.csv"}[kind]
        if path != expected or item["adjustment_allowed"] != "false":
            raise ValueError("Invalid inventory item")
        raw = subprocess.check_output(["git","-C",str(source),"show",SOURCE+":"+path])
        if len(raw) != int(item["bytes"]) or hashlib.sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest() != item["git_blob_sha"]:
            raise ValueError("Source integrity mismatch: "+path)
        reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
        required = {"fiscal_year","bonus_share","cash_dividend","total_dividend","book_closure_date"} if kind == "dividend" else {"ratio","total_units","issue_price","opening_date","closing_date","status","issue_manager"}
        if not required.issubset(reader.fieldnames or []) or len(set(reader.fieldnames or [])) != len(reader.fieldnames or []):
            raise ValueError("Unexpected schema: "+path)
        count = duplicates = 0
        for line,row in enumerate(reader,2):
            if None in row or any(v is None for v in row.values()):
                raise ValueError("Malformed row: "+path)
            payload = json.dumps(row,sort_keys=True,ensure_ascii=False)
            key = (symbol,kind,payload)
            if key in seen:
                duplicates += 1
                continue
            seen.add(key)
            count += 1
            flags = []
            try:
                if kind == "dividend":
                    for name in ("bonus_share","cash_dividend","total_dividend"):
                        value = Decimal(row[name].replace(",",""))
                        if not value.is_finite() or value < 0:
                            raise ValueError("Invalid percentage")
                    date.fromisoformat(row["book_closure_date"].split(" ")[0])
                else:
                    parts = row["ratio"].split(":")
                    if len(parts) != 2 or any(not Decimal(p.strip()).is_finite() or Decimal(p.strip()) <= 0 for p in parts):
                        raise ValueError("Invalid ratio")
                    if date.fromisoformat(row["opening_date"]) > date.fromisoformat(row["closing_date"]):
                        raise ValueError("Reversed subscription dates")
            except (ValueError, ArithmeticError, IndexError):
                flags.append("SOURCE_FIELD_REVIEW")
                print(json.dumps({"symbol":symbol,"kind":kind,"path":path,"line":line,"raw":row},ensure_ascii=False))
            if symbol in target:
                covered.add(symbol)
            events.append(dict(symbol=symbol,event_source=kind,target_equity=str(symbol in target).lower(),source_path=path,source_blob=item["git_blob_sha"],source_line=line,raw_event=payload,review_status=";".join(flags) or "UNVERIFIED_SECONDARY",effective_date="",adjustment_factor="",adjustment_allowed="false"))
        files.append(dict(symbol=symbol,path=path,rows=count,exact_duplicates=duplicates,target_equity=str(symbol in target).lower()))
    output.mkdir(parents=True,exist_ok=True)
    for name,records in [("corporate_action_candidates.csv",events),("file_audit.csv",files),("equity_coverage.csv",[dict(symbol=s,source_rows_present=str(s in covered).lower(),official_coverage="UNKNOWN") for s in sorted(target)])]:
        with (output/name).open("x",encoding="utf-8",newline="") as stream:
            w=csv.DictWriter(stream,fieldnames=list(records[0]))
            w.writeheader()
            w.writerows(records)
    summary=dict(files=len(files),candidate_rows=len(events),target_equities=len(target),target_symbols_with_candidates=len(covered),target_symbols_without_candidates=len(target-covered),target_candidate_rows=sum(r["target_equity"]=="true" for r in events),exact_duplicate_rows=sum(r["exact_duplicates"] for r in files),review_counts=dict(Counter(r["review_status"] for r in events)),approved_adjustments=0)
    (output/"summary.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))

if __name__ == "__main__":
    import sys
    run(Path(sys.argv[1]),Path(sys.argv[2]))
