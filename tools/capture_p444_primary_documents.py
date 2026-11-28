#!/usr/bin/env python3
"""Capture explicitly listed NEPSE primary-document URLs as immutable raw evidence.

The tool does not parse or promote documents. It stores exact response bytes,
checks the PDF signature, hashes the bytes, and writes a provenance manifest.
HTTP failures are recorded as failures; no rendered-page substitute is used.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def capture(url: str, output_dir: Path, timeout: int = 45) -> dict:
    retrieved = datetime.now(timezone.utc).isoformat(timespec="seconds")
    record = {
        "source_url": url,
        "retrieved_at_utc": retrieved,
        "authorization_status": "not_assessed",
        "evidence_tier": "unreviewed",
        "canonical_promotion_allowed": False,
    }
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "NEPSE-Evidence-Capture/1.0 (+https://github.com/jaljala044/nepse-smc-data)"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read()
            record["http_status"] = response.status
            record["content_type"] = response.headers.get("Content-Type", "")
            record["content_length_header"] = response.headers.get("Content-Length", "")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        record.update({"status": "capture_failed", "error": str(exc)})
        return record

    digest = hashlib.sha256(payload).hexdigest()
    record.update({
        "byte_length": len(payload),
        "raw_sha256": digest,
        "pdf_signature_valid": payload.startswith(b"%PDF-"),
    })
    if not payload.startswith(b"%PDF-"):
        record.update({"status": "rejected_non_pdf_response", "raw_bytes_saved": False})
        return record

    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{digest}.pdf"
    path = output_dir / filename
    if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise RuntimeError(f"Existing content-addressed file does not match its name: {path}")
    if not path.exists():
        path.write_bytes(payload)
    record.update({
        "status": "captured",
        "raw_bytes_saved": True,
        "raw_path": str(path),
        "raw_sha256_verified_after_write": hashlib.sha256(path.read_bytes()).hexdigest() == digest,
    })
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url-list", required=True, help="CSV with a source_url column")
    parser.add_argument("--output-dir", default="artifacts/p444_primary_documents")
    parser.add_argument("--manifest", default="artifacts/p444_primary_documents/manifest.json")
    args = parser.parse_args()

    with Path(args.url_list).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if "source_url" not in (reader.fieldnames or []):
            raise ValueError("URL list must contain a source_url column")
        urls = [row["source_url"].strip() for row in reader if row.get("source_url", "").strip()]

    results = []
    for index, url in enumerate(urls):
        results.append(capture(url, Path(args.output_dir)))
        if index + 1 < len(urls):
            time.sleep(1)

    manifest_path = Path(args.manifest)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps({
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "requested_count": len(urls),
        "captured_count": sum(r.get("status") == "captured" for r in results),
        "failed_count": sum(r.get("status") != "captured" for r in results),
        "canonical_promotion_allowed": False,
        "records": results,
    }, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"requested": len(urls), "captured": sum(r.get("status") == "captured" for r in results),
                      "failed": sum(r.get("status") != "captured" for r in results),
                      "manifest": str(manifest_path)}, sort_keys=True))
    return 0 if all(r.get("status") == "captured" for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
