#!/usr/bin/env python3
"""Validate imported secondary lifecycle context against current official security IDs."""
import argparse,csv,json
from collections import Counter
from pathlib import Path

def rows(path):
    with Path(path).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def audit(lifecycle_path,events_path,official_path):
    lifecycle=rows(lifecycle_path);events=rows(events_path)
    official=json.loads(Path(official_path).read_text(encoding="utf-8"))
    by_symbol={x["symbol"]:str(x["id"]) for x in official}
    if len(lifecycle)!=281:raise ValueError("expected 281 equity lifecycle rows")
    seen=set();statuses=Counter();dated=0;matches=0
    for r in lifecycle:
        s=r["symbol"]
        if s in seen:raise ValueError("duplicate lifecycle symbol "+s)
        seen.add(s)
        if r["instrument_type"]!="equity" or r["target_in_scope"].lower()!="true":raise ValueError("non-equity/out-of-scope lifecycle row "+s)
        if r["valid_from_evidence_status"] not in {"unverified","verified_secondary_first_trade_archive_match","verified_secondary_notice"}:raise ValueError("unsupported lifecycle evidence status")
        statuses[r["valid_from_evidence_status"]]+=1
        if r["valid_from"]:
            dated+=1
            if r["valid_from_evidence_status"]=="unverified" or not r["valid_from_evidence_uri"] or not r["valid_from_evidence_note"]:raise ValueError("dated lifecycle start lacks evidence URI/status/note")
        elif r["valid_from_evidence_status"]!="unverified" or r["valid_from_evidence_uri"]:raise ValueError("blank lifecycle start must remain unverified")
        if by_symbol.get(s)==r["security_id"]:matches+=1
    if matches!=281:raise ValueError("current official security ID/symbol crosswalk mismatch")
    if statuses["verified_primary_notice"]!=0:raise ValueError("source register unexpectedly asserts primary first-trade evidence")
    if dated!=44 or statuses["unverified"]!=237:raise ValueError("lifecycle evidence counts changed")
    if len(events)!=6:raise ValueError("expected six typed lifecycle events")
    event_ids=set()
    for e in events:
        if e["event_id"] in event_ids:raise ValueError("duplicate lifecycle event ID")
        event_ids.add(e["event_id"])
        if e["event_type"] in {"first_trade","first_executed_trade"} and e["review_status"]=="primary_notice_verified":raise ValueError("listing evidence must not be promoted to first-trade proof")
    return {"lifecycle_rows":len(lifecycle),"typed_events":len(events),"dated_secondary_starts":dated,
      "blank_unverified_starts":statuses["unverified"],"status_counts":dict(statuses),
      "current_official_id_symbol_matches":matches,"primary_first_trade_proofs":0,"promotion_allowed":False}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--lifecycle",required=True);p.add_argument("--events",required=True);p.add_argument("--official",required=True)
    a=p.parse_args();print(json.dumps(audit(a.lifecycle,a.events,a.official),indent=2))
if __name__=="__main__":main()
