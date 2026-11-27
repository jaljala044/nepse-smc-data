"""Validate P4.44 effective-dated lifecycle evidence without promoting weak records."""
import argparse,csv,hashlib,json
from collections import defaultdict
from datetime import date
from pathlib import Path

REQUIRED=("symbol","event_type","effective_date","source_url","retrieved_at_utc","raw_payload_path","raw_sha256","git_blob_sha","source_tier","effective_date_confidence","disposition")
VALID_EVENTS={"listing","trading_release","suspension","resumption","merger_successor","delisting","maturity","redemption","liquidation"}
ACCEPTED_TIERS={"exchange_primary","issuer_primary","regulator_primary"}
ACCEPTED_CONFIDENCE={"verified","corroborated","unverified","none"}

def validate(path,known_symbols=None,verify_files=False):
    rows=list(csv.DictReader(Path(path).open(encoding="utf-8-sig",newline="")))
    issues=[]; by_symbol=defaultdict(list); seen=set()
    for n,r in enumerate(rows,2):
        sym=(r.get("symbol") or "").strip()
        if not sym: issues.append({"row":n,"code":"MISSING_SYMBOL"}); continue
        if known_symbols is not None and sym not in known_symbols: issues.append({"row":n,"code":"SYMBOL_OUTSIDE_SCOPE","symbol":sym})
        by_symbol[sym].append((n,r))
        event=(r.get("event_type") or "").strip()
        if event and event not in VALID_EVENTS: issues.append({"row":n,"code":"INVALID_EVENT_TYPE","symbol":sym,"value":event})
        if r.get("effective_date") and r.get("effective_date") not in ("",):
            try: date.fromisoformat(r["effective_date"])
            except ValueError: issues.append({"row":n,"code":"INVALID_EFFECTIVE_DATE","symbol":sym,"value":r["effective_date"]})
        confidence=r.get("effective_date_confidence","none")
        if confidence not in ACCEPTED_CONFIDENCE: issues.append({"row":n,"code":"INVALID_CONFIDENCE","symbol":sym})
        evidence_fields=[r.get(k,"").strip() for k in ("source_url","retrieved_at_utc","raw_payload_path","raw_sha256","git_blob_sha")]
        complete=all(evidence_fields) and r.get("source_tier") in ACCEPTED_TIERS and confidence=="verified"
        if any(evidence_fields) and not complete: issues.append({"row":n,"code":"INCOMPLETE_PROVENANCE","symbol":sym})
        if complete:
            key=(sym,event,r.get("effective_date"),r.get("source_url"))
            if key in seen: issues.append({"row":n,"code":"DUPLICATE_EVENT_RECORD","symbol":sym})
            seen.add(key)
            if verify_files:
                p=Path(r["raw_payload_path"])
                if not p.is_file(): issues.append({"row":n,"code":"RAW_FILE_MISSING","symbol":sym,"path":str(p)})
                else:
                    digest=hashlib.sha256(p.read_bytes()).hexdigest()
                    if digest.lower()!=r["raw_sha256"].lower(): issues.append({"row":n,"code":"RAW_SHA256_MISMATCH","symbol":sym})
    # Contradictory overlapping lifecycle states: duplicate event type/date rows are surfaced,
    # and event dates are never auto-corrected or reordered.
    for sym,items in by_symbol.items():
        for i,(n,a) in enumerate(items):
            for m,b in items[i+1:]:
                if a.get("event_type") and a.get("event_type")==b.get("event_type") and a.get("effective_date") and a.get("effective_date")==b.get("effective_date") and a.get("source_url")!=b.get("source_url"):
                    issues.append({"row":m,"code":"CONFLICTING_SAME_DATE_EVENT","symbol":sym,"event_type":a["event_type"],"date":a["effective_date"]})
    summary={"rows":len(rows),"symbols":len(by_symbol),"provenance_complete_rows":sum(1 for r in rows if all((r.get(k) or "").strip() for k in ("source_url","retrieved_at_utc","raw_payload_path","raw_sha256","git_blob_sha")) and r.get("source_tier") in ACCEPTED_TIERS and r.get("effective_date_confidence")=="verified"),"hold_unknown_rows":sum(1 for r in rows if r.get("disposition","").startswith("HOLD")),"issues":issues,"valid":not issues}
    return summary

def main():
    p=argparse.ArgumentParser();p.add_argument("ledger");p.add_argument("--verify-files",action="store_true");a=p.parse_args()
    print(json.dumps(validate(a.ledger,verify_files=a.verify_files),indent=2))
    raise SystemExit(0 if validate(a.ledger,verify_files=a.verify_files)["valid"] else 1)
if __name__=="__main__":main()
