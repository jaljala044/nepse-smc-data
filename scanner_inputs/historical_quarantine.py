"""Fail-closed P4.43 historical hold gate. No implicit release or correction."""
import csv
import hashlib
import io
import json
from collections import Counter
from datetime import date
from pathlib import Path

MANIFEST = Path(__file__).resolve().parent.parent / "reference" / "P443_HISTORICAL_QUARANTINE_OVERLAY_MANIFEST_2026-11-27.json"
OVERLAY_SHA256 = "6d76c2a161dc3a65067806b5114a418be6aee0a90ebdc5519e2a718a531f7a2d"
EXPECTED_ROWS = 68773
SESSION_HOLDS = frozenset({"2026-04-10"})
EXPECTED_DISPOSITIONS = {
    "SCHEDULE_CLOSURE_CANDIDATE_HOLD":34345,
    "SECONDARY_CONTENT_PENDING":15439,
    "RECORDED_CLOSURE_HOLD":13312,
    "PARTIAL_HLV_MATCH_HOLD":3155,
    "PRICE_SEMANTICS_HOLD":1837,
    "OPEN_SESSION_SECURITY_EVIDENCE_PENDING":440,
    "SESSION_COMPLETENESS_HOLD":243,
    "UNRESOLVED_HOLD":2,
}

def key(symbol, day):
    symbol = symbol.strip().upper()
    day = day.strip()
    if not symbol or date.fromisoformat(day).isoformat() != day:
        raise ValueError("Invalid security/date")
    return symbol, day

def load_holds(overlay):
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if (manifest["overlay_sha256"] != OVERLAY_SHA256 or
        manifest["rows"] != EXPECTED_ROWS or manifest["unique_keys"] != EXPECTED_ROWS or
        manifest["dispositions"] != EXPECTED_DISPOSITIONS or
        manifest["approved_replacements"] != 0 or manifest["promoted"] != 0):
        raise ValueError("Unrecognized quarantine manifest")
    raw = Path(overlay).read_bytes()
    if len(raw) != manifest["overlay_bytes"] or hashlib.sha256(raw).hexdigest() != OVERLAY_SHA256:
        raise ValueError("Quarantine overlay integrity mismatch")
    holds = {}
    counts = Counter()
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    required = {"symbol","date","overlay_disposition","promotion_allowed","replacement_approved","scanner_admission","canonical_action","original_lineage"}
    if not required.issubset(reader.fieldnames or []) or len(set(reader.fieldnames)) != len(reader.fieldnames):
        raise ValueError("Invalid quarantine schema")
    for row in reader:
        k = key(row["symbol"],row["date"])
        disposition = row["overlay_disposition"]
        if (k in holds or disposition not in EXPECTED_DISPOSITIONS or
            row["promotion_allowed"] != "false" or row["replacement_approved"] != "false" or
            row["scanner_admission"] != "BLOCKED" or row["canonical_action"] != "NO_CHANGE" or
            not json.loads(row["original_lineage"])):
            raise ValueError(f"Invalid quarantine entry: {k}")
        if (k[1] in SESSION_HOLDS) != (disposition == "SESSION_COMPLETENESS_HOLD"):
            raise ValueError(f"Session hold mismatch: {k}")
        holds[k] = disposition
        counts[disposition] += 1
    if len(holds) != EXPECTED_ROWS or counts != EXPECTED_DISPOSITIONS or len({k[1] for k in holds}) != manifest["dates"]:
        raise ValueError("Quarantine coverage mismatch")
    return holds

def reject_held(symbol, day, holds):
    k = key(symbol,day)
    if k[1] in SESSION_HOLDS:
        raise ValueError(f"Quarantined session: {k[1]}")
    if (k[0], "*") in holds:
        raise ValueError(f"Quarantined lifecycle identity: {k[0]}: {holds[(k[0], '*')]}")
    if k in holds:
        raise ValueError(f"Quarantined security/date: {k}: {holds[k]}")

def validate_rows(values, holds):
    for row in values:
        reject_held(row["symbol"],row["date"],holds)
