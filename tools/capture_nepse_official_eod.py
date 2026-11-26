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

import httpx
from nepse import Nepse

NPT = timezone(timedelta(hours=5, minutes=45))
BASE_URL = "https://www.nepalstock.com"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="NEPSE business date YYYY-MM-DD")
    parser.add_argument("--symbol", default="RHGCL")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    client = Nepse()
    client.base_url = BASE_URL
    client.setTLSVerification(True)
    client.load_json_header()

    endpoint = client.api_end_points["todays_price"]
    page_size = 500
    captures = []
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
            if response.status_code != 200:
                raise RuntimeError(
                    f"NEPSE EOD request failed: status={response.status_code}, "
                    f"content_type={response.headers.get('content-type')}, "
                    f"body={response.text[:300]!r}"
                )
            content_type = response.headers.get("content-type", "")
            if "json" not in content_type.lower():
                raise RuntimeError(f"NEPSE returned non-JSON response: {content_type}")
            raw = response.content
            payload = json.loads(raw.decode("utf-8"))
            if not isinstance(payload, dict) or not isinstance(payload.get("content"), list):
                raise RuntimeError("NEPSE EOD response missing content array")
            if total_pages is None:
                total_pages = int(payload.get("totalPages", 1))
                total_elements = int(payload.get("totalElements", len(payload["content"])))
            elif int(payload.get("totalPages", total_pages)) != total_pages:
                raise RuntimeError("NEPSE totalPages changed during paginated capture")

            file_path = args.output_dir / f"nepse_eod_{args.date}_page_{page}.json"
            file_path.write_bytes(raw)
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
    matching = []
    for capture in captures:
        raw = Path(capture["file"]).read_bytes()
        payload = json.loads(raw.decode("utf-8"))
        for row in payload["content"]:
            if str(row.get("symbol", "")).strip().upper() == symbol and str(row.get("businessDate", ""))[:10] == args.date:
                matching.append(capture)

    manifest = {
        "status": "TARGET_ROW_FOUND" if len(matching) == 1 else "TARGET_ROW_NOT_UNIQUE",
        "source": "NEPSE official EOD API",
        "symbol": symbol,
        "business_date": args.date,
        "base_url": BASE_URL,
        "total_pages": total_pages,
        "upstream_total_elements": total_elements,
        "captured_pages": captures,
        "target_page_file": matching[0]["file"] if len(matching) == 1 else None,
        "target_page_url": matching[0]["url"] if len(matching) == 1 else None,
        "target_page_retrieved_at": matching[0]["retrieved_at"] if len(matching) == 1 else None,
    }
    manifest_path = args.output_dir / "capture_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    if len(matching) != 1:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
