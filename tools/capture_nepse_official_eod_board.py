#!/usr/bin/env python3
"""Capture complete official NEPSE EOD board pages for a single business date.

The exact response bytes are written before parsing. This script captures the
board, not a selected symbol, so one capture can validate many securities.
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
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--page-size", type=int, default=500)
    args = parser.parse_args()
    if args.page_size < 1 or args.page_size > 500:
        raise SystemExit("page-size must be between 1 and 500")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    client = Nepse()
    client.base_url = BASE_URL
    client.setTLSVerification(True)
    client.load_json_header()
    endpoint = client.api_end_points["todays_price"]
    captures = []
    total_pages = None
    total_elements = None

    with httpx.Client(timeout=60, verify=True, follow_redirects=False) as http:
        page = 0
        while total_pages is None or page < total_pages:
            params = urlencode({
                "size": args.page_size,
                "page": page,
                "businessDate": args.date,
            })
            url = f"{client.get_full_url(endpoint)}?{params}"
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
                if total_pages < 1 or total_elements < 0:
                    raise RuntimeError("NEPSE returned invalid pagination metadata")
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

    if len(captures) != total_pages:
        raise RuntimeError(f"captured {len(captures)} pages, expected {total_pages}")
    if sum(item["rows"] for item in captures) != total_elements:
        raise RuntimeError("captured page row count does not equal NEPSE totalElements")

    manifest = {
        "status": "COMPLETE_BOARD_CAPTURE",
        "source": "NEPSE official EOD API",
        "business_date": args.date,
        "base_url": BASE_URL,
        "page_size": args.page_size,
        "total_pages": total_pages,
        "total_elements": total_elements,
        "captured_pages": captures,
        "raw_archive_mutated": False,
    }
    (args.output_dir / "capture_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "status": manifest["status"],
        "business_date": args.date,
        "total_pages": total_pages,
        "total_elements": total_elements,
        "capture_files": len(captures),
        "raw_archive_mutated": False,
    }, indent=2))


if __name__ == "__main__":
    main()
