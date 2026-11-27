"""Validate P4.44 effective-dated lifecycle evidence without promoting weak records."""
import argparse
import csv
import hashlib
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

REQUIRED = {
    "symbol", "event_type", "effective_date", "calendar_basis", "security_id",
    "successor_symbol", "source_url", "retrieved_at_utc", "raw_payload_path",
    "raw_sha256", "git_blob_sha", "source_tier",
    "effective_date_confidence", "source_statement", "disposition",
}
VALID_EVENTS = {
    "listing", "trading_release", "suspension", "resumption",
    "merger_successor", "delisting", "maturity", "redemption", "liquidation",
}
SOURCE_TIERS = {
    "exchange_primary", "issuer_primary", "regulator_primary",
    "secondary_notice", "secondary_nepse_listing_report",
    "secondary_company_metadata", "unknown",
}
CONFIDENCE = {"verified", "corroborated", "unverified", "none"}
TERMINAL_EVENTS = {"delisting", "maturity", "redemption", "liquidation"}
TRADING_EVENTS = {"listing", "trading_release", "resumption"}
REVIEW_ONLY_CODES = {"EVENT_DATE_MISSING", "MERGER_SUCCESSOR_MISSING"}


def validate(path, known_symbols=None, verify_files=False):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames or []
        issues = []
        if len(fields) != len(set(fields)):
            issues.append({"row": 1, "code": "DUPLICATE_COLUMN_NAME"})
        missing = sorted(REQUIRED - set(fields))
        if missing:
            issues.append({"row": 1, "code": "MISSING_REQUIRED_COLUMNS", "columns": missing})
            return {"rows": 0, "symbols": 0, "provenance_complete_rows": 0,
                    "hold_unknown_rows": 0, "issues": issues, "review_findings": [], "error_findings": issues, "evidence_complete": False, "valid": False}
        rows = list(reader)

    by_symbol = defaultdict(list)
    seen_records = set()
    for number, row in enumerate(rows, 2):
        symbol = (row.get("symbol") or "").strip().upper()
        if not symbol:
            issues.append({"row": number, "code": "MISSING_SYMBOL"})
            continue
        if known_symbols is not None and symbol not in known_symbols:
            issues.append({"row": number, "code": "SYMBOL_OUTSIDE_SCOPE", "symbol": symbol})

        event = (row.get("event_type") or "").strip()
        raw_date = (row.get("effective_date") or "").strip()
        parsed_date = None
        if event and event not in VALID_EVENTS:
            issues.append({"row": number, "code": "INVALID_EVENT_TYPE", "symbol": symbol, "value": event})
        if event and not raw_date:
            issues.append({"row": number, "code": "EVENT_DATE_MISSING", "symbol": symbol, "event_type": event})
        elif raw_date:
            try:
                parsed_date = date.fromisoformat(raw_date)
            except ValueError:
                issues.append({"row": number, "code": "INVALID_EFFECTIVE_DATE", "symbol": symbol, "value": raw_date})

        tier = (row.get("source_tier") or "").strip()
        confidence = (row.get("effective_date_confidence") or "").strip()
        if tier not in SOURCE_TIERS:
            issues.append({"row": number, "code": "INVALID_SOURCE_TIER", "symbol": symbol, "value": tier})
        if confidence not in CONFIDENCE:
            issues.append({"row": number, "code": "INVALID_CONFIDENCE", "symbol": symbol, "value": confidence})
        if event == "merger_successor" and not (row.get("successor_symbol") or "").strip():
            issues.append({"row": number, "code": "MERGER_SUCCESSOR_MISSING", "symbol": symbol})

        evidence = [((row.get(key) or "").strip()) for key in
                    ("source_url", "retrieved_at_utc", "raw_payload_path", "raw_sha256", "git_blob_sha")]
        primary = tier in {"exchange_primary", "issuer_primary", "regulator_primary"}
        if confidence == "verified":
            if not all(evidence) or not primary or not parsed_date:
                issues.append({"row": number, "code": "INCOMPLETE_VERIFIED_PROVENANCE", "symbol": symbol})
            if not (row.get("security_id") or "").strip():
                issues.append({"row": number, "code": "VERIFIED_EVENT_MISSING_SECURITY_ID", "symbol": symbol})
            if not (row.get("source_statement") or "").strip():
                issues.append({"row": number, "code": "VERIFIED_EVENT_MISSING_SOURCE_STATEMENT", "symbol": symbol})

        if row.get("raw_sha256") and not all(ch in "0123456789abcdefABCDEF" for ch in row["raw_sha256"].strip()):
            issues.append({"row": number, "code": "INVALID_RAW_SHA256", "symbol": symbol})
        if row.get("git_blob_sha") and not all(ch in "0123456789abcdefABCDEF" for ch in row["git_blob_sha"].strip()):
            issues.append({"row": number, "code": "INVALID_GIT_BLOB_SHA", "symbol": symbol})

        if event and parsed_date:
            by_symbol[symbol].append((number, event, parsed_date, row))
            key = (symbol, event, parsed_date.isoformat(), (row.get("source_url") or "").strip())
            if key in seen_records:
                issues.append({"row": number, "code": "DUPLICATE_EVENT_RECORD", "symbol": symbol})
            seen_records.add(key)
            if verify_files and all(evidence):
                raw_path = Path(row["raw_payload_path"])
                if not raw_path.is_file():
                    issues.append({"row": number, "code": "RAW_FILE_MISSING", "symbol": symbol, "path": str(raw_path)})
                elif hashlib.sha256(raw_path.read_bytes()).hexdigest().lower() != row["raw_sha256"].strip().lower():
                    issues.append({"row": number, "code": "RAW_SHA256_MISMATCH", "symbol": symbol})

    for symbol, events in by_symbol.items():
        ordered = sorted(events, key=lambda item: (item[2], item[0]))
        for index, (line, event, day, row) in enumerate(ordered):
            for other_line, other_event, other_day, other_row in ordered[index + 1:]:
                if event == other_event and day == other_day and (row.get("source_url") or "") != (other_row.get("source_url") or ""):
                    issues.append({"row": other_line, "code": "CONFLICTING_SAME_DATE_EVENT",
                                   "symbol": symbol, "event_type": event, "date": day.isoformat()})
            if event in TERMINAL_EVENTS:
                later_trading = [item[0] for item in ordered if item[2] > day and item[1] in TRADING_EVENTS]
                if later_trading:
                    issues.append({"row": line, "code": "TERMINAL_EVENT_PRECEDES_LATER_TRADING",
                                   "symbol": symbol, "later_event_rows": later_trading})
            if event == "resumption" and not any(
                item[1] == "suspension" and item[2] < day for item in ordered
            ):
                issues.append({"row": line, "code": "RESUMPTION_WITHOUT_PRIOR_SUSPENSION", "symbol": symbol})

    provenance_complete = sum(
        all((row.get(key) or "").strip() for key in
            ("source_url", "retrieved_at_utc", "raw_payload_path", "raw_sha256", "git_blob_sha"))
        and row.get("source_tier") in {"exchange_primary", "issuer_primary", "regulator_primary"}
        and row.get("effective_date_confidence") == "verified"
        for row in rows
    )
    review_findings = [issue for issue in issues if issue["code"] in REVIEW_ONLY_CODES]
    error_findings = [issue for issue in issues if issue["code"] not in REVIEW_ONLY_CODES]
    return {
        "rows": len(rows),
        "symbols": len({(row.get("symbol") or "").strip().upper() for row in rows if (row.get("symbol") or "").strip()}),
        "provenance_complete_rows": provenance_complete,
        "hold_unknown_rows": sum((row.get("disposition") or "").startswith("HOLD") for row in rows),
        "issues": issues,
        "review_findings": review_findings,
        "error_findings": error_findings,
        "evidence_complete": not issues,
        "valid": not error_findings,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger")
    parser.add_argument("--verify-files", action="store_true")
    args = parser.parse_args()
    result = validate(args.ledger, verify_files=args.verify_files)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
