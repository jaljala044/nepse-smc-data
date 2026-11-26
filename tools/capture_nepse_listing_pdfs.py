#!/usr/bin/env python3
"""Capture official NEPSE merger-share listing PDFs with byte-level provenance."""
import argparse
import hashlib
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

DOCUMENTS = [
    {
        "symbol": "NMLBBL",
        "event_date": "2024-05-17",
        "document_type": "post_merger_share_listing_and_trading_release",
        "url": "https://www.nepalstock.com/api/nots/security/fetchFiles?fileLocation=rita_listing%2F2024-05-17%2FNMLBBL_1715925622934.pdf",
        "scope_limit": "Confirms merger shares were listed and trading released; does not establish the first executed contract date."
    },
    {
        "symbol": "SMPDA",
        "event_date": "2024-08-15",
        "document_type": "post_merger_share_listing",
        "url": "https://www.nepalstock.com/api/nots/security/fetchFiles?fileLocation=rita_listing%2F2024-08-15%2FSMPDA_1723716902880.pdf",
        "scope_limit": "Confirms merger shares were listed and an opening range was set; does not establish the first executed contract date."
    }
]

def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "NEPSE-Data-Evidence-Audit/1.0",
        "Accept": "application/pdf,application/octet-stream;q=0.9,*/*;q=0.8"
    })
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.status, dict(response.headers.items()), response.read()

def capture(output_dir, fetcher=fetch, retrieved_at=None):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    retrieved_at = retrieved_at or datetime.now(timezone.utc).isoformat()
    records = []
    for item in DOCUMENTS:
        row = dict(item)
        row["retrieved_at_utc"] = retrieved_at
        try:
            status, headers, body = fetcher(item["url"])
            row["http_status"] = status
            row["content_type"] = headers.get("Content-Type") or headers.get("content-type")
            row["response_bytes"] = len(body)
            if status != 200:
                row["capture_status"] = "http_error"
            elif not body.startswith(b"%PDF-"):
                row["capture_status"] = "non_pdf_response"
                row["response_sha256"] = hashlib.sha256(body).hexdigest()
            else:
                filename = f"{item['symbol']}_{item['event_date']}_NEPSE_official.pdf"
                path = output_dir / filename
                path.write_bytes(body)
                row["capture_status"] = "captured"
                row["filename"] = filename
                row["response_sha256"] = hashlib.sha256(body).hexdigest()
        except Exception as exc:
            row["capture_status"] = "unavailable"
            row["error"] = f"{type(exc).__name__}: {exc}"
        records.append(row)
    report = {
        "task": "P4.32",
        "source_authority": "Nepal Stock Exchange (NEPSE) official fetchFiles endpoint",
        "retrieved_at_utc": retrieved_at,
        "documents": records,
        "interpretation": "These are post-merger listing/trading-release documents. They do not prove first executed trade dates; contract-level first-trade and complete prior-session evidence remain separately required.",
        "first_trade_disposition": {
            "NMLBBL": {"candidate_date": "2024-05-19", "prior_session_to_check": "2024-05-16", "status": "UNKNOWN"},
            "SMPDA": {"candidate_date": "2024-08-18", "prior_session_to_check": "2024-08-14", "status": "UNKNOWN"}
        }
    }
    (output_dir / "capture_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="reference/p432_official_listing_documents")
    args = parser.parse_args()
    report = capture(args.output_dir)
    for doc in report["documents"]:
        print(f"{doc['symbol']}: {doc['capture_status']} {doc.get('response_sha256', doc.get('error', ''))}")
    if any(doc["capture_status"] != "captured" for doc in report["documents"]):
        print("WARNING: one or more official PDFs were not captured; UNKNOWN lifecycle status is preserved.")

if __name__ == "__main__":
    main()
