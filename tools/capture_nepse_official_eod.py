#!/usr/bin/env python3
"""Capture the official NEPSE EOD board while preserving exact response bytes.

Uses the public NEPSE API client only to obtain its short-lived Salter token and
POST payload ID. Every HTTP response body is written byte-for-byte before JSON
parsing. No raw market archive is modified.
"""
import argparse
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode

from p437_official_eod_helpers import summarize_pages

import httpx
from nepse import Nepse

NPT = timezone(timedelta(hours=5, minutes=45))
BASE_URL = "https://www.nepalstock.com"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="NEPSE business date YYYY-MM-DD")
    parser.add_argument("--symbol", default="RHGCL")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--allow-missing", action="store_true", help="Save a complete capture manifest even when the target symbol/date row is absent or non-unique")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    client = Nepse()
    client.base_url = BASE_URL
    client.setTLSVerification(True)
    client.load_json_header()

    endpoint = client.api_end_points["todays_price"]
    page_size = 500
    captures = []
    page_payloads = []
    total_pages = None
    total_elements = None

    with httpx.Client(timeout=60, verify=True, follow_redirects=False) as http:
        page = 0
        while total_pages is None or page < total_pages:
            params = urlencode({
                "size": page_size,
                "page": page,
                "businessDate": args.date,
            })
            url = f"{client.get_full_url(endpoint)}?{params}"
            # Refresh token first; the POST ID is derived from its current salts.
            headers = dict(client.getAuthorizationHeaders())
            headers["Content-Type"] = "application/json"
            body = {"id": client.getPOSTPayloadIDForFloorSheet()}
            response = http.post(url, headers=headers, json=body)
            retrieved_at = datetime.now(NPT).isoformat()
            raw = response.content
            file_path = args.output_dir / f"nepse_eod_{args.date}_page_{page}.json"
            file_path.write_bytes(raw)
            content_type = response.headers.get("content-type", "")
            if response.status_code != 200 or "json" not in content_type.lower():
                error = {
                    "status": "HTTP_OR_CONTENT_TYPE_ERROR",
                    "source": "NEPSE official EOD API",
                    "symbol": args.symbol.strip().upper(),
                    "business_date": args.date,
                    "url": str(response.request.url),
                    "retrieved_at": retrieved_at,
                    "http_status": response.status_code,
                    "content_type": content_type,
                    "bytes": len(raw),
                    "sha256": hashlib.sha256(raw).hexdigest(),
                    "error_body_preview": raw.decode("utf-8", "replace")[:300],
                    "raw_payload_file": str(file_path),
                }
                (args.output_dir / "capture_error.json").write_text(json.dumps(error, indent=2) + "\n", encoding="utf-8")
                raise RuntimeError(f"NEPSE EOD request failed; see capture_error.json")
            try:
                payload = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                error = {
                    "status": "INVALID_JSON",
                    "url": str(response.request.url),
                    "retrieved_at": retrieved_at,
                    "http_status": response.status_code,
                    "content_type": content_type,
                    "bytes": len(raw),
                    "sha256": hashlib.sha256(raw).hexdigest(),
                    "error": str(exc),
                    "raw_payload_file": str(file_path),
                }
                (args.output_dir / "capture_error.json").write_text(json.dumps(error, indent=2) + "\n", encoding="utf-8")
                raise RuntimeError("NEPSE EOD response was not valid JSON; see capture_error.json")
            if not isinstance(payload, dict) or not isinstance(payload.get("content"), list):
                raise RuntimeError("NEPSE EOD response missing content array")
            if total_pages is None:
                total_pages = int(payload.get("totalPages", 1))
                total_elements = int(payload.get("totalElements", len(payload["content"])))
            else:
                if int(payload.get("totalPages", total_pages)) != total_pages:
                    raise RuntimeError("NEPSE totalPages changed during paginated capture")
                if int(payload.get("totalElements", total_elements)) != total_elements:
                    raise RuntimeError("NEPSE totalElements changed during paginated capture")

            page_payloads.append(payload)
            captures.append({
                "page": page,
                "file": str(file_path),
                "url": str(response.request.url),
                "retrieved_at": retrieved_at,
                "http_status": response.status_code,
                "content_type": content_type,
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "rows": len(payload["content"]),
            })
            page += 1

    symbol = args.symbol.strip().upper()
    summary = summarize_pages(page_payloads, symbol, args.date, total_elements)
    target_page_indices = [
        i for i, payload in enumerate(page_payloads)
        if any(
            isinstance(row, dict)
            and str(row.get("symbol", "")).strip().upper() == symbol
            and str(row.get("businessDate", ""))[:10] == args.date
            for row in payload["content"]
        )
    ]
    target_page = captures[target_page_indices[0]] if len(target_page_indices) == 1 else None
    manifest = {
        **summary,
        "source": "NEPSE official EOD API",
        "base_url": BASE_URL,
        "total_pages": total_pages,
        "upstream_total_elements": total_elements,
        "captured_pages": captures,
        "target_page_file": target_page["file"] if target_page else None,
        "target_page_url": target_page["url"] if target_page else None,
        "target_page_retrieved_at": target_page["retrieved_at"] if target_page else None,
        "target_page_index": target_page["page"] if target_page else None,
    }
    manifest_path = args.output_dir / "capture_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    if summary["target_row_count"] != 1 and not args.allow_missing:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
