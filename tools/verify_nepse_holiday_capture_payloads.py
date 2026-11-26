#!/usr/bin/env python3
"""Fetch and cryptographically verify every immutable NEPSE holiday capture."""
import argparse
import concurrent.futures
import hashlib
import json
import time
import urllib.request
from pathlib import Path

def git_blob_sha(data):
    return hashlib.sha1(f"blob {len(data)}\\0".encode("ascii") + data).hexdigest()

def verify_file(record, fetch):
    data = fetch(record["url"])
    errors = []
    if len(data) != record["size_bytes"]:
        errors.append(f"size mismatch: expected {record['size_bytes']}, got {len(data)}")
    actual_blob = git_blob_sha(data)
    if actual_blob != record["git_blob_sha"]:
        errors.append(f"Git blob SHA mismatch: expected {record['git_blob_sha']}, got {actual_blob}")
    return data, errors

def fetch_url(url):
    request = urllib.request.Request(url, headers={"User-Agent": "NEPSE-Data-Evidence-Audit/1.0"})
    last_error = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                if response.status != 200:
                    raise RuntimeError(f"HTTP {response.status}: {url}")
                return response.read()
        except Exception as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"download failed after 3 attempts: {url}: {last_error}")

def verify(manifest, fetch=fetch_url):
    errors, checked = [], 0
    for annual in manifest["annual_captures"]:
        records = {f["name"]: f for f in annual["files"]}
        payloads = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            futures = {pool.submit(verify_file, rec, fetch): name for name, rec in records.items()}
            for future in concurrent.futures.as_completed(futures):
                name = futures[future]
                try:
                    data, issues = future.result()
                    payloads[name] = data
                    checked += 1
                    errors.extend(f"{annual['year']}/{name}: {issue}" for issue in issues)
                except Exception as exc:
                    errors.append(f"{annual['year']}/{name}: {exc}")
        if len(payloads) != 6:
            continue
        try:
            body = payloads["response-body.bin"]
            expected_sha = payloads["SHA256SUMS"].decode("utf-8").split()[0]
            actual_sha = hashlib.sha256(body).hexdigest()
            if actual_sha != expected_sha:
                errors.append(f"{annual['year']}: response-body SHA-256 mismatch")
            parsed = json.loads(body.decode("utf-8"))
            parsed_copy = json.loads(payloads["parsed-response.json"].decode("utf-8"))
            if parsed != parsed_copy:
                errors.append(f"{annual['year']}: parsed-response.json differs from raw response body")
            report = json.loads(payloads["capture-report.json"].decode("utf-8"))
            if report.get("requested_year") != annual["year"]:
                errors.append(f"{annual['year']}: capture report requested_year mismatch")
            if report.get("http_status") != 200:
                errors.append(f"{annual['year']}: capture report is not HTTP 200")
            if report.get("parsed_record_count") != len(parsed):
                errors.append(f"{annual['year']}: capture report parsed_record_count mismatch")
            if report.get("response_bytes") != len(body):
                errors.append(f"{annual['year']}: capture report response_bytes mismatch")
            if report.get("response_sha256") != actual_sha:
                errors.append(f"{annual['year']}: capture report response_sha256 mismatch")
            source_url = payloads["source-url.txt"].decode("utf-8").strip()
            if source_url != report.get("source_url") or f"year={annual['year']}" not in source_url:
                errors.append(f"{annual['year']}: source URL mismatch")
        except Exception as exc:
            errors.append(f"{annual['year']}: payload cross-check failed: {exc}")
    return {"checked_files": checked, "errors": errors}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    result = verify(json.loads(args.manifest.read_text(encoding="utf-8")))
    if result["errors"]:
        raise SystemExit("\\n".join(result["errors"]))
    print(f"PASS: fetched and verified {result['checked_files']}/72 files; Git blob SHA, size, raw-body SHA-256, JSON parity and annual metadata match")

if __name__ == "__main__":
    main()
