"""Read-only P4.44 row-level evidence matrix for 209 uncovered repeat symbols."""
import argparse, ast, csv, hashlib, json, subprocess, io
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

PIN="56362fb4f65b91fdcca8f50b50e53ad80e703649"
TRIAGE="reference/P443_UNCOVERED_REPEAT_SYMBOL_IDENTITY_TRIAGE_2026-11-27.csv"
CALENDAR="reference/nepse_canonical_session_calendar_2025-2026.csv"
POSITIVE="reference/nepse_positive_open_sessions_2025-11-26_2026-11-25.csv"

def git_bytes(path,pin=PIN):
    return subprocess.check_output(["git","show",f"{pin}:{path}"])

def csv_rows(raw):
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"),newline="")))

def identity_fields(r):
    hid=r.get("historical_stable_id","").strip()
    verified=r.get("historical_effective_date_verified","").lower()=="true"
    cid=r.get("current_snapshot_security_id","").strip()
    scope="historical_effective_dated_id" if hid and verified else ("current_snapshot_only" if cid else "unresolved")
    return {
      "identity_scope":scope,"historical_stable_id":hid if scope=="historical_effective_dated_id" else "",
      "current_snapshot_security_id":cid,"current_snapshot_status":r.get("current_snapshot_status",""),
      "current_snapshot_name":r.get("current_snapshot_name",""),
      "historical_instrument_class_candidate":r.get("historical_instrument_class",""),
      "target_registry_instrument_class_candidate":r.get("target_registry_instrument_class",""),
      "triage_disposition":r.get("review_disposition",""),"triage_class":r.get("triage_class","")
    }

def load_evidence():
    closed=defaultdict(list)
    for r in csv_rows(git_bytes(CALENDAR)):
        if r.get("status")=="verified_closed" and r.get("scope")=="all_securities":
            closed[r["date"]].append(r)
    execution=defaultdict(list)
    for r in csv_rows(git_bytes(POSITIVE)):
        if r.get("status")=="verified_open":
            execution[(r.get("source_symbol",""),r.get("date",""))].append(r)
    return closed,execution

def session_fields(symbol,day,closed,execution):
    c=closed.get(day,[]); e=execution.get((symbol,day),[])
    status=("CONFLICTING_MARKET_CLOSED_AND_SECURITY_TRADE" if c and e else
            "SECURITY_POSITIVE_TRADE" if e else
            "MARKET_CLOSED_ALL_SECURITIES" if c else
            "UNKNOWN_NO_PINNED_SESSION_EVIDENCE")
    return {
      "status":status,
      "market_sources":";".join(x.get("source_id","")+"|"+x.get("evidence_uri","") for x in c),
      "execution_sources":";".join(x.get("source_id","")+"|"+x.get("source_capture_file","")+"|"+x.get("raw_evidence_sha256","") for x in e),
      "execution_security_ids":";".join(sorted({x.get("security_id","") for x in e if x.get("security_id")})),
      "execution_trade_counts":";".join(sorted({x.get("total_trades","") for x in e if x.get("total_trades")})),
      "execution_quantities":";".join(sorted({x.get("total_traded_quantity","") for x in e if x.get("total_traded_quantity")})),
      "execution_values":";".join(sorted({x.get("total_traded_value","") for x in e if x.get("total_traded_value")})),
      "execution_retrieved_at":";".join(sorted({x.get("retrieved_at_utc","") for x in e if x.get("retrieved_at_utc")}))
    }

@lru_cache(maxsize=64)
def source_rows(path,expected_blob):
    raw=git_bytes(path)
    actual=hashlib.sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest()
    if actual!=expected_blob: raise ValueError(f"source blob mismatch: {path}")
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig"),newline=""))
    out={}
    for r in reader:
        n={k.lower().replace("_","").replace(" ",""):v for k,v in r.items()}
        day=next((n[k] for k in ("date","tradingdate","tradedate") if k in n),None)
        if day is None: raise ValueError(f"date column missing: {path}")
        vals=tuple(n.get(k,"") for k in ("open","high","low","close","volume"))
        out[str(reader.line_num)]=(day.strip(),vals)
    return out

def build(findings,output,expected_pairs=23377,expected_symbols=209):
    triage=csv_rows(git_bytes(TRIAGE)); by_symbol={r["symbol"].strip():r for r in triage}
    if len(by_symbol)!=expected_symbols: raise ValueError(f"triage symbols {len(by_symbol)} != {expected_symbols}")
    closed,execution=load_evidence(); counts=Counter(); symbols=set(); dates=[]; total=0
    out=Path(output); out.mkdir(parents=True,exist_ok=True)
    fields=["pair_id","symbol","previous_date","current_date","source_path","source_blob_sha","previous_source_row","current_source_row","source_pair_tuple_equal","identity_scope","historical_stable_id","current_snapshot_security_id","current_snapshot_status","current_snapshot_name","historical_instrument_class_candidate","target_registry_instrument_class_candidate","triage_disposition","triage_class","previous_session_status","previous_market_sources","previous_execution_sources","previous_execution_security_ids","previous_execution_trade_counts","previous_execution_quantities","previous_execution_values","previous_execution_retrieved_at","current_session_status","current_market_sources","current_execution_sources","current_execution_security_ids","current_execution_trade_counts","current_execution_quantities","current_execution_values","current_execution_retrieved_at","disposition","promotion_allowed"]
    with open(findings,encoding="utf-8") as src,(out/"P444_UNCOVERED_REPEAT_PAIR_EVIDENCE_2026-11-27.csv").open("w",newline="",encoding="utf-8") as dst:
      w=csv.DictWriter(dst,fieldnames=fields); w.writeheader()
      for line in src:
        f=json.loads(line)
        if f.get("classification")!="repeated_adjacent_tuple_unresolved": continue
        _,_,sym,day=ast.literal_eval(f["key"])
        if sym not in by_symbol: continue
        rows=source_rows(f["path"],f["blob_sha"])
        cur=rows.get(str(f["row"])); prev=rows.get(str(f["previous_row"]))
        if not cur or not prev: raise ValueError(f"source row absent: {f['path']}:{f['row']}")
        pd,pv=prev; cd,cv=cur
        if cd!=day or pd==cd or cv!=pv: raise ValueError(f"repeat source lineage mismatch: {f['path']}:{f['row']}")
        ident=identity_fields(by_symbol[sym]); ps=session_fields(sym,pd,closed,execution); cs=session_fields(sym,cd,closed,execution)
        row={"pair_id":f"{f['path']}#{f['previous_row']}->{f['row']}","symbol":sym,"previous_date":pd,"current_date":cd,"source_path":f["path"],"source_blob_sha":f["blob_sha"],"previous_source_row":f["previous_row"],"current_source_row":f["row"],"source_pair_tuple_equal":"true",**ident}
        for prefix,x in (("previous",ps),("current",cs)):
          for k,v in x.items(): row[f"{prefix}_{'session_status' if k=='status' else k}"]=v
          counts[prefix+"_session_"+x["status"]]+=1
          if x["execution_sources"]: counts[prefix+"_security_execution_present"]+=1
        row.update(disposition="HOLD_UNKNOWN_NO_INFERENCE",promotion_allowed="false")
        w.writerow(row); total+=1; symbols.add(sym); dates.extend((pd,cd))
        counts["identity_"+ident["identity_scope"]]+=1
    if total!=expected_pairs or len(symbols)!=expected_symbols: raise ValueError(f"coverage mismatch: {total} pairs/{len(symbols)} symbols")
    summary={"task":"P4.44 uncovered repeat pair evidence matrix","pinned_source_commit":PIN,"pairs":total,"symbols":len(symbols),"date_min":min(dates),"date_max":max(dates),"counts":dict(sorted(counts.items())),"disposition":"HOLD_UNKNOWN_NO_INFERENCE","promotion_allowed":False,"canonical_data_modified":False,"limitations":["Current snapshot IDs do not prove historical continuity.","Market-open evidence does not prove a specific security traded.","Missing execution evidence is not evidence of no trade.","Repeated tuples do not prove duplicate executions."]}
    (out/"P444_UNCOVERED_REPEAT_PAIR_EVIDENCE_SUMMARY_2026-11-27.json").write_text(json.dumps(summary,indent=2)+"\n")
    report=["# P4.44 — uncovered repeated-pair row-level evidence matrix","",f"Pinned source: {PIN}",f"Rows: {total:,} across {len(symbols)} symbols; date range {summary['date_min']} to {summary['date_max']}.","","Every row includes exact source path/blob/row identity, both dates, identity scope, and available session/execution evidence. Current snapshot IDs are separated from historical stable IDs.","","All rows remain HOLD/UNKNOWN. No canonical data changed; no pair was promoted or deduplicated.","","## Counts",""]+[f"- {k}: {v:,}" for k,v in sorted(counts.items())]+["","## Limitations",""]+[f"- {x}" for x in summary["limitations"]]+[""]
    (out/"P444_UNCOVERED_REPEAT_PAIR_EVIDENCE_2026-11-27.md").write_text("\n".join(report))
    return summary

def main():
    p=argparse.ArgumentParser(); p.add_argument("--findings",required=True); p.add_argument("--output-dir",required=True); p.add_argument("--expected-pairs",type=int,default=23377); p.add_argument("--expected-symbols",type=int,default=209); a=p.parse_args()
    print(json.dumps(build(a.findings,a.output_dir,a.expected_pairs,a.expected_symbols),indent=2))

if __name__=="__main__": main()
