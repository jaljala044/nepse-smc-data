#!/usr/bin/env python3
"""Small stdlib validator for the P4.44 identity interval contract."""
from __future__ import annotations
import argparse, json, re
from datetime import date
from pathlib import Path

HEX64=re.compile(r"^[a-fA-F0-9]{64}$")
HEX40=re.compile(r"^[a-fA-F0-9]{40}$")
FIELDS={"record_type","security_id","symbol","instrument_type","status","effective_from","effective_to","source_url","retrieved_at_utc","raw_sha256","source_git_blob_sha","authorization_status","evidence_tier","effective_date_confidence","canonical_promotion_allowed"}
def validate(record: dict) -> list[str]:
    errors=[]
    if set(record)!=FIELDS: errors.append("field_set_mismatch")
    if record.get("record_type") not in {"snapshot_identity","lifecycle_interval"}: errors.append("invalid_record_type")
    if not str(record.get("security_id","")).strip(): errors.append("missing_security_id")
    if not re.fullmatch(r"[A-Z0-9._-]+",str(record.get("symbol",""))): errors.append("invalid_symbol")
    if record.get("instrument_type") not in {"EQUITY","PROMOTER","MUTUAL_FUND","DEBENTURE","BOND","OTHER","UNKNOWN"}: errors.append("invalid_instrument_type")
    if record.get("status") not in {"ACTIVE","SUSPENDED","MERGED","DELISTED","CANCELLED","UNKNOWN"}: errors.append("invalid_status")
    for key in ("effective_from","effective_to"):
        value=record.get(key)
        if value is not None:
            try: date.fromisoformat(value)
            except (TypeError,ValueError): errors.append("invalid_"+key)
    start,end=record.get("effective_from"),record.get("effective_to")
    if start and end and end<start: errors.append("reversed_interval")
    if record.get("raw_sha256") is not None and not HEX64.fullmatch(str(record["raw_sha256"])): errors.append("invalid_raw_sha256")
    if record.get("source_git_blob_sha") is not None and not HEX40.fullmatch(str(record["source_git_blob_sha"])): errors.append("invalid_source_git_blob_sha")
    if record.get("canonical_promotion_allowed") is not False: errors.append("promotion_must_remain_false")
    if record.get("record_type")=="lifecycle_interval":
        if not start: errors.append("lifecycle_requires_effective_from")
        if not str(record.get("source_url","")).strip(): errors.append("lifecycle_requires_source_url")
        if not str(record.get("retrieved_at_utc","")).strip(): errors.append("lifecycle_requires_retrieval_time")
        if not HEX64.fullmatch(str(record.get("raw_sha256",""))): errors.append("lifecycle_requires_raw_sha256")
        if record.get("authorization_status") not in {"authorized","rights_cleared"}: errors.append("lifecycle_requires_rights_clearance")
        if record.get("evidence_tier") not in {"primary","approved"}: errors.append("lifecycle_requires_primary_or_approved_tier")
        if record.get("effective_date_confidence")!="verified": errors.append("lifecycle_requires_verified_date")
    if record.get("record_type")=="snapshot_identity":
        if record.get("evidence_tier")!="current_snapshot_only": errors.append("snapshot_tier_mismatch")
        if record.get("effective_date_confidence")!="unknown": errors.append("snapshot_date_confidence_must_be_unknown")
    return errors

def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("input"); args=ap.parse_args()
    data=json.loads(Path(args.input).read_text(encoding="utf-8"))
    records=data if isinstance(data,list) else [data]
    failures=[{"index":i,"errors":validate(r)} for i,r in enumerate(records) if validate(r)]
    print(json.dumps({"records":len(records),"invalid":len(failures),"failures":failures},indent=2))
    raise SystemExit(bool(failures))
if __name__=="__main__": main()
