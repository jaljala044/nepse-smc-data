#!/usr/bin/env python3
"""Capture exact NEPSE company floorsheet pages for adjacent-repeat review pairs."""
import argparse
import csv
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
from nepse import Nepse

NPT = timezone(timedelta(hours=5, minutes=45))


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def repeat_pairs(repeat_flags):
    pairs = set()
    for row in read_csv(repeat_flags):
        if row.get("classification") != "OPEN_SESSION_REPEAT_REVIEW":
            continue
        symbol = row["symbol"].strip().upper()
        pairs.add((symbol, row["previous_date"]))
        pairs.add((symbol, row["date"]))
    return sorted(pairs, key=lambda x: (x[0], x[1]))


def page_parts(payload):
    if payload in (None, {}, []):
        return [], 0, 0, "EMPTY_RESPONSE"
    if not isinstance(payload, dict) or not isinstance(payload.get("floorsheets"), dict):
        return [], None, None, "UNRECOGNIZED_RESPONSE_SCHEMA"
    sheet = payload["floorsheets"]
    content = sheet.get("content")
    if not isinstance(content, list):
        return [], None, None, "MISSING_CONTENT_ARRAY"
    return content, int(sheet.get("totalPages", 0)), int(sheet.get("totalElements", len(content))), "OK"


def post_page(client, url):
    for attempt in range(2):
        headers = client.getAuthorizationHeaders()
        payload_id = client.getPOSTPayloadIDForFloorSheet()
        response = client.client.post(url, headers=headers, data=json.dumps({"id": payload_id}))
        if response.status_code == 401 and attempt == 0:
            client.token_manager.update()
            continue
        return response
    raise RuntimeError("NEPSE floorsheet authentication retry exhausted")


def capture_pair(client, symbol, day, security_id, output_dir):
    endpoint = client.api_end_points["company_floorsheet"] + str(security_id)
    base_url = (
        f"{client.get_full_url(endpoint)}?&businessDate={day}"
        f"&size=500&sort=contractid,desc"
    )
    captures = []
    rows = []
    total_pages = None
    total_elements = None
    schema_status = "OK"
    page = 0

    while total_pages is None or page < total_pages:
        url = base_url if page == 0 else f"{base_url}&page={page}"
        response = post_page(client, url)
        retrieved_at = datetime.now(NPT).isoformat()
        if response.status_code != 200:
            raise RuntimeError(
                f"NEPSE floorsheet failed for {symbol} {day}: "
                f"HTTP {response.status_code}: {response.text[:300]!r}"
            )
        content_type = response.headers.get("content-type", "")
        if "json" not in content_type.lower():
            raise RuntimeError(f"NEPSE floorsheet returned non-JSON content: {content_type}")
        raw = response.content
        payload = json.loads(raw.decode("utf-8"))
        page_rows, pages, elements, status = page_parts(payload)

        if status == "EMPTY_RESPONSE":
            if page == 0:
                total_pages, total_elements = 0, 0
                schema_status = "EMPTY_RESPONSE_REQUIRES_EOD_CROSSCHECK"
                page_rows = []
            else:
                raise RuntimeError(f"unexpected empty later page for {symbol} {day} page {page}")
        elif status != "OK":
            schema_status = status
            if page == 0:
                total_pages, total_elements = 0, 0
            break
        else:
            if total_pages is None:
                total_pages, total_elements = pages, elements
            elif pages != total_pages or elements != total_elements:
                raise RuntimeError(f"pagination metadata changed for {symbol} {day}")
            if total_pages == 0 and page_rows:
                raise RuntimeError(f"NEPSE returned rows with totalPages=0 for {symbol} {day}")

        file_path = output_dir / f"{symbol}_{day}_page_{page}.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(raw)
        captures.append({
            "page": page, "file": str(file_path), "url": str(response.request.url),
            "retrieved_at": retrieved_at, "http_status": response.status_code,
            "content_type": content_type, "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(), "rows": len(page_rows),
        })
        rows.extend(page_rows)
        if total_pages == 0:
            break
        page += 1

    if schema_status == "OK" and len(rows) != total_elements:
        raise RuntimeError(
            f"floorsheet row count mismatch for {symbol} {day}: "
            f"captured={len(rows)} totalElements={total_elements}"
        )

    row_fields = sorted({key for row in rows for key in row}) if rows else []
    identity_checks = []
    for row in rows:
        row_symbol = row.get("symbol", row.get("stockSymbol", row.get("securitySymbol")))
        row_day = str(row.get("businessDate", row.get("business_date", "")))[:10]
        row_security_id = row.get("securityId", row.get("security_id"))
        if row_symbol and str(row_symbol).upper() != symbol:
            identity_checks.append("SYMBOL_MISMATCH")
        if row_day and row_day != day:
            identity_checks.append("DATE_MISMATCH")
        if row_security_id is not None and str(row_security_id) != str(security_id):
            identity_checks.append("SECURITY_ID_MISMATCH")

    if identity_checks:
        schema_status = "IDENTITY_REVIEW_REQUIRED"

    manifest = {
        "symbol": symbol, "business_date": day, "security_id": str(security_id),
        "source": "NEPSE official company floorsheet API",
        "endpoint": base_url, "status": (
            "COMPLETE_FLOORSHEET_CAPTURE" if schema_status == "OK" and rows
            else "NO_FLOORSHEET_RECORDS_REQUIRES_EOD_CROSSCHECK" if schema_status == "OK" and not rows
            else schema_status
        ),
        "total_pages": total_pages, "total_elements": total_elements,
        "captured_rows": len(rows), "row_fields": row_fields,
        "identity_checks": sorted(set(identity_checks)),
        "captured_pages": captures,
        "raw_payloads_mutated": False,
    }
    pair_dir = output_dir / symbol / day
    pair_dir.mkdir(parents=True, exist_ok=True)
    (pair_dir / "capture_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return manifest, rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeat-flags", type=Path, required=True)
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    mapping = {r["symbol"].strip().upper(): r["security_id"].strip()
               for r in read_csv(args.mapping)}
    pairs = repeat_pairs(args.repeat_flags)
    if len(pairs) != 10:
        raise SystemExit(f"expected 10 symbol/date pairs from five repeat flags, found {len(pairs)}")

    client = Nepse()
    client.setTLSVerification(True)
    official_ids = client.getSecurityIDKeyMap()
    manifests = []
    for symbol, day in pairs:
        if symbol not in mapping or symbol not in official_ids:
            raise RuntimeError(f"missing official security ID for {symbol}")
        if str(official_ids[symbol]) != mapping[symbol]:
            raise RuntimeError(f"security-ID snapshot mismatch for {symbol}")
        manifest, _ = capture_pair(client, symbol, day, mapping[symbol], args.output_dir)
        manifests.append(manifest)

    summary = {
        "status": "CAPTURED_WITH_ROW_LEVEL_DISPOSITIONS",
        "pairs_requested": len(pairs),
        "complete_pairs": sum(m["status"] == "COMPLETE_FLOORSHEET_CAPTURE" for m in manifests),
        "empty_pairs": sum(m["status"] == "NO_FLOORSHEET_RECORDS_REQUIRES_EOD_CROSSCHECK" for m in manifests),
        "review_pairs": sum(m["status"] not in {"COMPLETE_FLOORSHEET_CAPTURE", "NO_FLOORSHEET_RECORDS_REQUIRES_EOD_CROSSCHECK"} for m in manifests),
        "pairs": manifests,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "batch_manifest.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "pairs_requested": len(pairs), "complete_pairs": summary["complete_pairs"],
        "empty_pairs": summary["empty_pairs"], "review_pairs": summary["review_pairs"],
    }, indent=2))


if __name__ == "__main__":
    main()
