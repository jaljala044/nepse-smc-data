#!/usr/bin/env python3
"""Read-only P4.43 duplicate and integrity scan over the pinned inventory."""
import argparse
import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "reference" / "NEPSE_GLOBAL_DUPLICATE_AUDIT_INVENTORY.csv"
FINDINGS = ROOT / "reference" / "NEPSE_GLOBAL_DUPLICATE_AUDIT_FINDINGS.csv"
SUMMARY = ROOT / "reference" / "NEPSE_GLOBAL_DUPLICATE_AUDIT_SCAN_SUMMARY.csv"
REPORT = ROOT / "reference" / "NEPSE_GLOBAL_DUPLICATE_AUDIT_REPORT.md"


def norm(value):
    return "".join(ch.lower() for ch in str(value or "") if ch.isalnum())


def choose(headers, aliases):
    lookup = {norm(h): h for h in headers}
    for alias in aliases:
        if norm(alias) in lookup:
            return lookup[norm(alias)]
    return None


def emit(findings, row):
    findings.append({k: str(v) for k, v in row.items()})


def read_rows(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", newline="", encoding="utf-8-sig") as stream:
        yield from csv.DictReader(stream)


def scan_csv(path, category, findings, stats):
    rows = list(read_rows(path))
    stats["records"] += len(rows)
    if not rows:
        return
    headers = list(rows[0])
    if category == "ohlcv_symbol_archive":
        date_col = choose(headers, ["Date", "Trading_Date", "TradingDate"])
        cols = {name: choose(headers, [name]) for name in ["Open", "High", "Low", "Close", "Volume"]}
        if not date_col or not all(cols.values()):
            stats["unsupported"] += 1
            return
        seen_keys, seen_rows, seen_exact_rows, prior = {}, {}, {}, None
        for line, row in enumerate(rows, 2):
            date = row.get(date_col, "").strip()
            symbol = path.stem.replace("_OHLCV", "").upper()
            key = (symbol, date)
            payload = tuple((row.get(cols[k]) or "").strip() for k in ["Open", "High", "Low", "Close", "Volume"])
            if key in seen_keys:
                emit(findings, {"finding_type":"duplicate_symbol_date_key","category":category,"path":path.relative_to(ROOT),"line":line,"related_line":seen_keys[key],"key": "|".join(key),"detail":"Multiple rows share one symbol/date key; preserve all rows pending provenance review"})
            else:
                seen_keys[key] = line
            exact_key = (date, payload)
            if exact_key in seen_exact_rows:
                emit(findings, {"finding_type":"exact_duplicate_ohlcv_row","category":category,"path":path.relative_to(ROOT),"line":line,"related_line":seen_exact_rows[exact_key],"key":"|".join(key),"detail":"Same date and complete OHLCV tuple repeated within this symbol file"})
            else:
                seen_exact_rows[exact_key] = line
            if payload in seen_rows:
                emit(findings, {"finding_type":"repeated_ohlcv_tuple","category":category,"path":path.relative_to(ROOT),"line":line,"related_line":seen_rows[payload],"key":"|".join(key),"detail":"OHLCV tuple repeats across rows; not assumed erroneous"})
            else:
                seen_rows[payload] = line
            if prior and payload == prior[1] and date != prior[0]:
                emit(findings, {"finding_type":"consecutive_identical_ohlcv_tuple","category":category,"path":path.relative_to(ROOT),"line":line,"related_line":prior[2],"key":f"{symbol}|{prior[0]}|{date}","detail":"Same OHLCV tuple on consecutive file rows; repeated values alone do not establish duplication"})
            prior = (date, payload, line)
    elif category == "floorsheet_or_reconciliation":
        txn = choose(headers, ["Contract_No", "ContractNo", "Contract Number", "contract_id", "contractId", "Transaction ID", "TransactionId"])
        if not txn and choose(headers, ["Transaction"]) and all(choose(headers, [name]) for name in ["Symbol", "Buyer", "Seller", "Quantity", "Rate"]):
            txn = choose(headers, ["Transaction"])
        date_col = choose(headers, ["Trading_Date", "TradingDate", "Date", "business_date"])
        seen, exact = {}, {}
        for line, row in enumerate(rows, 2):
            date = (row.get(date_col) or "").strip() if date_col else ""
            fingerprint = tuple((row.get(h) or "").strip() for h in headers)
            if fingerprint in exact:
                emit(findings, {"finding_type":"exact_duplicate_floorsheet_row","category":category,"path":path.relative_to(ROOT),"line":line,"related_line":exact[fingerprint],"key":date,"detail":"Exact row repeated within this file"})
            else:
                exact[fingerprint] = line
            if txn:
                tid = (row.get(txn) or "").strip()
                if not tid:
                    continue
                key = (date, tid)
                if key in seen:
                    emit(findings, {"finding_type":"duplicate_floorsheet_contract_key","category":category,"path":path.relative_to(ROOT),"line":line,"related_line":seen[key],"key":"|".join(key),"detail":"Contract identity repeats within this source file/session; inspect source pagination and provenance"})
                else:
                    seen[key] = line
        if not txn:
            stats["unsupported"] += 1
    elif category == "session_calendar":
        date_col = choose(headers, ["date", "session_date", "Trading_Date"])
        if date_col:
            seen = {}
            for line, row in enumerate(rows, 2):
                date = (row.get(date_col) or "").strip()
                if not date:
                    continue
                if date in seen:
                    emit(findings, {"finding_type":"duplicate_calendar_date","category":category,"path":path.relative_to(ROOT),"line":line,"related_line":seen[date],"key":date,"detail":"Date appears more than once in this calendar file; independent calendar sources are not combined"})
                else:
                    seen[date] = line


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write deterministic findings, summary and report")
    args = parser.parse_args()
    with INVENTORY.open(newline="", encoding="utf-8") as stream:
        inventory = list(csv.DictReader(stream))
    findings, summaries = [], []
    totals = Counter()
    for item in inventory:
        path = ROOT / item["path"]
        stats = Counter()
        status, error = "inventory_only", ""
        fmt = item["format"].lower()
        totals["files"] += 1
        try:
            if fmt in {"csv", "csv.gz", "gz"} and (fmt != "gz" or path.name.endswith(".csv.gz")):
                scan_csv(path, item["category"], findings, stats)
                status = "parsed_csv"
            elif fmt == "json":
                opener = gzip.open if path.suffix == ".gz" else open
                with opener(path, "rt", encoding="utf-8") as stream:
                    raw = stream.read()
                if not raw.strip():
                    status = "empty_capture"
                    error = "Empty provider capture; no market data verified"
                elif raw.lstrip().startswith("<html") or raw.strip().startswith("Searched Date is not valid."):
                    status = "non_json_response"
                    error = "Non-JSON provider capture; no market data verified"
                else:
                    json.loads(raw)
                    stats["records"] = 1
                    status = "parsed_json_document"
            else:
                stats["unsupported"] += 1
            totals["records"] += stats["records"]
            totals["unsupported"] += stats["unsupported"]
            totals[status] += 1
        except Exception as exc:
            status, error = "parse_error", f"{type(exc).__name__}: {exc}"
            totals["parse_errors"] += 1
            totals["parse_error"] += 1
        summaries.append({"path":item["path"],"category":item["category"],"format":fmt,"status":status,"records":stats["records"],"unsupported_checks":stats["unsupported"],"error":error})
    totals["findings"] = len(findings)
    totals["ohlcv_key_duplicates"] = sum(x["finding_type"]=="duplicate_symbol_date_key" for x in findings)
    totals["ohlcv_exact_rows"] = sum(x["finding_type"]=="exact_duplicate_ohlcv_row" for x in findings)
    totals["ohlcv_repeated_tuples"] = sum(x["finding_type"]=="repeated_ohlcv_tuple" for x in findings)
    totals["ohlcv_consecutive_tuples"] = sum(x["finding_type"]=="consecutive_identical_ohlcv_tuple" for x in findings)
    totals["floorsheet_contract_duplicates"] = sum(x["finding_type"]=="duplicate_floorsheet_contract_key" for x in findings)
    totals["floorsheet_exact_rows"] = sum(x["finding_type"]=="exact_duplicate_floorsheet_row" for x in findings)
    totals["calendar_duplicate_dates"] = sum(x["finding_type"]=="duplicate_calendar_date" for x in findings)
    if args.write:
        with FINDINGS.open("w", newline="", encoding="utf-8") as stream:
            fields = ["finding_type","category","path","line","related_line","key","detail"]
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(findings)
        with SUMMARY.open("w", newline="", encoding="utf-8") as stream:
            fields = ["path","category","format","status","records","unsupported_checks","error"]
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(summaries)
        lines = [
            "# P4.43 global duplicate and data-integrity audit",
            "",
            "**Pinned input:** `main` at `56362fb4f65b91fdcca8f50b50e53ad80e703649`.",
            "**Method:** deterministic, read-only scan of the pinned inventory. Findings are leads for review, not automatic corrections.",
            "",
            "## Scan totals",
            "",
            f"- Inventory files visited: {totals['files']}",
            f"- Parseable CSV data rows plus parsed JSON documents: {totals['records']}",
            f"- Parsed CSV files: {totals['parsed_csv']}",
            f"- Parsed JSON documents: {totals['parsed_json_document']}",
            f"- Empty/whitespace-only captures: {totals['empty_capture']}",
            f"- Non-JSON provider responses: {totals['non_json_response']}",
            f"- Unsupported file/check combinations: {totals['unsupported']}",
            f"- Parse errors: {totals['parse_errors']}",
            f"- Findings: {totals['findings']}",
            "",
            "## Finding classes",
            "",
        ]
        for key, label in [
            ("ohlcv_key_duplicates","OHLCV duplicate symbol/date keys"),
            ("ohlcv_exact_rows","OHLCV exact duplicate rows (same symbol/date/tuple)"),
            ("ohlcv_repeated_tuples","OHLCV repeated tuples across rows (not assumed erroneous)"),
            ("ohlcv_consecutive_tuples","consecutive identical OHLCV tuples"),
            ("floorsheet_contract_duplicates","floorsheet duplicate contract keys"),
            ("floorsheet_exact_rows","floorsheet exact repeated rows"),
            ("calendar_duplicate_dates","duplicate dates within a calendar file"),
        ]:
            lines.append(f"- {label}: {totals[key]}")
        lines += [
            "",
            "## Interpretation and safeguards",
            "",
            "- Repeated OHLCV values across different dates are flagged as repeated tuples, not declared invalid; consecutive repeated values may reflect source carry-forward or date-stamping defects.",
            "- Floorsheet contract identifiers are scoped to the same source file/session, never treated as globally unique across dates.",
            "- Calendar dates are checked within each calendar file; independent calendars are not merged into duplicate counts.",
            "- Existing P4 audit outputs are inventoried as artifacts and are not added to raw-source finding totals, preventing simple double counting.",
            "- Unsupported formats/checks and parse errors are enumerated in the scan summary; a zero finding count is not proof of clean data.",
            "- No source OHLCV, floorsheet, calendar or scanner input rows are modified, deleted, corrected or promoted.",
            "",
            "Machine-readable outputs: `NEPSE_GLOBAL_DUPLICATE_AUDIT_FINDINGS.csv` and `NEPSE_GLOBAL_DUPLICATE_AUDIT_SCAN_SUMMARY.csv`.",
        ]
        REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(dict(totals), sort_keys=True))


if __name__ == "__main__":
    main()
