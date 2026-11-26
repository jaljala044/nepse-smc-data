#!/usr/bin/env python3
"""Validate the immutable NEPSE holiday-capture evidence index."""
import argparse, json, re
from pathlib import Path

EXPECTED_FILES = {
    "SHA256SUMS", "capture-report.json", "parsed-response.json",
    "response-body.bin", "response-headers.json", "source-url.txt",
}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")

def validate(data):
    errors = []
    if data.get("source_commit") != "39747bd2ade2bdb59ef7665f454bcbc04b3060df":
        errors.append("source commit is not pinned to the audited capture commit")
    years = data.get("years", [])
    if [x.get("year") for x in years] != list(range(2015, 2027)):
        errors.append("expected annual captures in order for 2015-2026")
    all_urls = []
    for item in years:
        year = item.get("year")
        files = item.get("files", [])
        names = [x.get("name") for x in files]
        if set(names) != EXPECTED_FILES or len(names) != len(EXPECTED_FILES):
            errors.append(f"{year}: expected exactly six capture evidence files")
        for file in files:
            if not SHA_RE.fullmatch(file.get("git_blob_sha", "")):
                errors.append(f"{year}/{file.get('name')}: invalid Git blob SHA")
            url = file.get("immutable_url", "")
            if data.get("source_commit", "") not in url or f"/{year}-11-25/" not in url:
                errors.append(f"{year}/{file.get('name')}: URL is not pinned to the expected year/commit")
            all_urls.append(url)
    if len(all_urls) != 72 or len(set(all_urls)) != 72:
        errors.append("expected 72 unique immutable file URLs")
    audit = data.get("audit_summary", {})
    if audit.get("http_200_years") != 12 or audit.get("total_records") != 499 or audit.get("unique_dates") != 498:
        errors.append("archive-level audit totals do not match the reviewed audit")
    if audit.get("duplicate_date") != "2020-04-13":
        errors.append("duplicate-date exception missing")
    if data.get("calendar_616_recovery", {}).get("exact_date_list_recovered") is not False:
        errors.append("must explicitly preserve unrecovered 616-date status")
    return errors

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    errors = validate(data)
    if errors:
        raise SystemExit("\n".join(errors))
    print("PASS: 12 years, 72 immutable file references, archive controls and 616 UNKNOWN status")

if __name__ == "__main__":
    main()
