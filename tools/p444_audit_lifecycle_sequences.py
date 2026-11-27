"""Audit P4.44 lifecycle event sequences without changing evidence or dispositions.

Findings are review flags only. This tool never infers missing dates, releases holds,
or promotes an identity/event.
"""
import argparse
import csv
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

REQUIRED = {"symbol", "event_type", "effective_date", "successor_symbol",
            "effective_date_confidence", "disposition"}
DATE_ORDER = {
    "listing": 0, "trading_release": 1, "suspension": 2,
    "resumption": 3, "merger_successor": 4, "delisting": 5,
    "maturity": 6, "redemption": 7, "liquidation": 8,
}


def audit(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames or []
        if len(fields) != len(set(fields)) or not REQUIRED.issubset(fields):
            raise ValueError("Invalid P4.44 lifecycle ledger schema")
        rows = list(reader)

    findings = []
    by_symbol = defaultdict(list)
    for line, row in enumerate(rows, 2):
        symbol = (row.get("symbol") or "").strip().upper()
        event = (row.get("event_type") or "").strip()
        raw_date = (row.get("effective_date") or "").strip()
        if not symbol:
            findings.append({"line": line, "code": "MISSING_SYMBOL", "severity": "ERROR"})
            continue
        if not event:
            continue
        if event not in DATE_ORDER:
            findings.append({"line": line, "symbol": symbol, "code": "UNKNOWN_EVENT_TYPE", "severity": "ERROR"})
            continue
        if not raw_date:
            findings.append({"line": line, "symbol": symbol, "event_type": event,
                             "code": "EVENT_DATE_MISSING", "severity": "REVIEW"})
            continue
        try:
            parsed = date.fromisoformat(raw_date)
        except ValueError:
            findings.append({"line": line, "symbol": symbol, "event_type": event,
                             "code": "EVENT_DATE_INVALID", "severity": "ERROR"})
            continue
        by_symbol[symbol].append((line, event, parsed, row))

        if event == "merger_successor" and not (row.get("successor_symbol") or "").strip():
            findings.append({"line": line, "symbol": symbol,
                             "code": "MERGER_SUCCESSOR_MISSING", "severity": "REVIEW"})

    for symbol, events in by_symbol.items():
        ordered = sorted(events, key=lambda item: (item[2], item[0]))
        for i, (line, event, day, row) in enumerate(ordered):
            for other_line, other_event, other_day, other_row in ordered[i + 1:]:
                if event == other_event and day == other_day:
                    findings.append({"line": other_line, "symbol": symbol,
                                     "code": "DUPLICATE_EVENT_DATE", "severity": "REVIEW",
                                     "event_type": event, "date": day.isoformat()})
            if event in {"delisting", "maturity", "redemption", "liquidation"}:
                earlier = [e for e in ordered if e[2] > day and e[1] in {"listing", "trading_release", "resumption"}]
                if earlier:
                    findings.append({"line": line, "symbol": symbol,
                                     "code": "TERMINAL_EVENT_PRECEDES_LATER_TRading",
                                     "severity": "REVIEW", "terminal_event": event,
                                     "later_event_lines": [e[0] for e in earlier]})
            if event == "resumption":
                suspensions = [e for e in ordered if e[1] == "suspension" and e[2] < day]
                if not suspensions:
                    findings.append({"line": line, "symbol": symbol,
                                     "code": "RESUMPTION_WITHOUT_PRIOR_SUSPENSION",
                                     "severity": "REVIEW", "date": day.isoformat()})

    findings.sort(key=lambda x: (x.get("line", 0), x["code"]))
    return {
        "rows": len(rows),
        "symbols": len({(r.get("symbol") or "").strip().upper() for r in rows if (r.get("symbol") or "").strip()}),
        "findings": len(findings),
        "review_findings": sum(f["severity"] == "REVIEW" for f in findings),
        "error_findings": sum(f["severity"] == "ERROR" for f in findings),
        "findings_detail": findings,
        "mutations": 0,
        "promotions": 0,
        "dispositions_changed": 0,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger")
    args = parser.parse_args()
    print(json.dumps(audit(args.ledger), indent=2))
    # Review findings are expected for an incomplete evidence ledger; schema/errors fail CI.
    raise SystemExit(1 if audit(args.ledger)["error_findings"] else 0)


if __name__ == "__main__":
    main()
