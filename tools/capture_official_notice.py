#!/usr/bin/env python3
"""Capture an official NEPSE/SEBON notice as immutable raw bytes plus metadata.

This utility does not parse notices or populate the session calendar. A human
must review the captured evidence and create an evidence-backed calendar row.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ALLOWED_HOSTS = {"nepalstock.com.np", "www.nepalstock.com.np", "nepalstock.com", "www.nepalstock.com", "sebon.gov.np", "www.sebon.gov.np"}


def capture_notice(url: str, source_id: str, output_dir: str | Path,
                   published_at: str | None = None, timeout: int = 30) -> dict:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError("notice URL must use HTTPS on an approved NEPSE or SEBON host")
    if not source_id or not source_id.strip():
        raise ValueError("source_id is required")
    if timeout < 1 or timeout > 120:
        raise ValueError("timeout must be between 1 and 120 seconds")
    if published_at:
        try:
            published = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("published_at must be an ISO-8601 timestamp") from exc
        if published.tzinfo is None:
            raise ValueError("published_at must be timezone-aware")
    request = Request(url, headers={"User-Agent": "NEPSE-AI-Evidence-Capture/1.0", "Accept": "application/pdf,application/octet-stream,text/html,*/*"})
    with urlopen(request, timeout=timeout) as response:
        status = getattr(response, "status", 200)
        if status != 200:
            raise RuntimeError(f"official notice request returned HTTP {status}")
        raw = response.read()
        headers = dict(response.headers.items())
        final_url = response.geturl()
    final = urlparse(final_url)
    if final.scheme != "https" or final.hostname not in ALLOWED_HOSTS:
        raise ValueError("redirect target is not an approved official HTTPS host")
    if not raw:
        raise ValueError("official notice response is empty")
    digest = hashlib.sha256(raw).hexdigest()
    retrieved = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    raw_path = root / f"{source_id}-{digest}.bin"
    metadata_path = root / f"{source_id}-{digest}.json"
    if raw_path.exists() and raw_path.read_bytes() != raw:
        raise RuntimeError("content-addressed notice path contains different bytes")
    if not raw_path.exists():
        raw_path.write_bytes(raw)
    metadata = {
        "source_id": source_id,
        "url": url,
        "final_url": final_url,
        "published_at": published_at,
        "retrieved_at_utc": retrieved,
        "http_status": status,
        "content_type": headers.get("Content-Type") or headers.get("content-type"),
        "content_length_header": headers.get("Content-Length") or headers.get("content-length"),
        "raw_byte_count": len(raw),
        "raw_evidence_sha256": digest,
        "raw_evidence_path": str(raw_path),
        "calendar_populated": False,
        "human_review_required": True,
    }
    encoded = json.dumps(metadata, indent=2, ensure_ascii=False) + "\n"
    if metadata_path.exists() and metadata_path.read_text(encoding="utf-8") != encoded:
        raise RuntimeError("content-addressed notice metadata conflicts with existing file")
    metadata_path.write_text(encoded, encoding="utf-8")
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--published-at")
    parser.add_argument("--output-dir", type=Path, default=Path("data/evidence/notices"))
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()
    result = capture_notice(args.url, args.source_id, args.output_dir, args.published_at, args.timeout)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
