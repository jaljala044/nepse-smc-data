#!/usr/bin/env python3
"""Compare flagged v3 rows to a pinned ShareSansar-derived archive without retaining source data."""
import argparse
import csv
import hashlib
import io
import json
import urllib.request
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

SOURCE_REPO = "srijankarki07/nepse-data"
SOURCE_COMMIT = "688d59c03915dcee73ecad4230d2083a41c61764"
EXPECTED_BLOBS = {
    "AHPC": "9d03bc7630fd2f631e2a2df32093b4502d5b6591",
    "SKBBL": "c2cd3f77ba5614823246a40748f24b6f5430b9e8",
    "API": "7d8d252ae3016bcb8cd5d3751076045bff42db08",
    "MERO": "a6ce6696fead7b463f332ede6aac95da9b068fdc",
    "SPDL": "69d181fd958cd11866aa019a27cafb25b957bb0a",
    "CHL": "30d6756c83c5bf8dfbf553b9feb9a246b32e61bb",
    "HIDCL": "c519422607e431db404ca8b9e2d5b876b0eb0cc0",
    "RADHI": "8660064b7a8520efe8f7cfd2fbec9455014608cc",
    "UNHPL": "19fc28fe57e2690d7c191f5b6aa6ffb8d4014d97",
}
FIELDS = ["symbol", "date", "flag", "secondary_status", "different_fields",
          "secondary_ohlc_valid", "source_repository", "source_commit",
          "source_path", "source_git_blob_sha", "disposition"]


def blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def dec(value):
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, TypeError):
        return None


def parse_csv_bytes(data):
    return list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))


def compare_flag(flag, v3_row, secondary_row):
    fields = {"open": ("Open", "open"), "high": ("High", "high"),
              "low": ("Low", "low"), "close": ("Close", "close"),
              "volume": ("Volume", "volume")}
    different = []
    for name, (v3_key, secondary_key) in fields.items():
        if dec(v3_row.get(v3_key)) != dec(secondary_row.get(secondary_key)):
            different.append(name)
    o, h, l, c = (dec(secondary_row.get(k)) for k in ("open", "high", "low", "close"))
    valid = all(v is not None for v in (o, h, l, c)) and h >= l and l <= o <= h and l <= c <= h and min(o, h, l, c) > 0
    status = "EXACT_MATCH_NOT_INDEPENDENT_CORROBORATION" if not different else "SECONDARY_VALUE_DIFFERENCE_REVIEW"
    return status, ";".join(different), valid


def fetch_series(symbol):
    path = f"data/series/{symbol}.csv"
    url = f"https://raw.githubusercontent.com/{SOURCE_REPO}/{SOURCE_COMMIT}/{path}"
    request = urllib.request.Request(url, headers={"User-Agent": "NEPSE-Data-Quality-Audit/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read()
    actual = blob_sha(data)
    expected = EXPECTED_BLOBS[symbol]
    if actual != expected:
        raise ValueError(f"pinned source blob mismatch for {symbol}: {actual}")
    rows = parse_csv_bytes(data)
    indexed = {}
    for row in rows:
        day = row.get("date", "")
        if not day or day in indexed:
            raise ValueError(f"missing/duplicate date in secondary series {symbol}: {day}")
        indexed[day] = row
    return path, actual, indexed


def build(flags_path, v3_dir, output_path, summary_path, expected_flags=1368):
    flags = list(csv.DictReader(Path(flags_path).open(newline="", encoding="utf-8-sig")))
    if len(flags) != expected_flags:
        raise ValueError(f"expected {expected_flags} invariant flags, found {len(flags)}")
    symbols = sorted({r["symbol"].strip().upper() for r in flags})
    if set(symbols) != set(EXPECTED_BLOBS):
        raise ValueError(f"symbol coverage differs from pinned secondary batch: {symbols}")

    secondary = {}
    v3 = {}
    source_meta = {}
    for symbol in symbols:
        path, sha, rows = fetch_series(symbol)
        secondary[symbol] = rows
        source_meta[symbol] = (path, sha)
        v3_path = Path(v3_dir) / f"{symbol}_OHLCV.csv"
        with v3_path.open(newline="", encoding="utf-8-sig") as fh:
            v3rows = list(csv.DictReader(fh))
        v3[symbol] = {r["Date"]: r for r in v3rows}
        if len(v3[symbol]) != len(v3rows):
            raise ValueError(f"duplicate date in v3 file for {symbol}")

    out_rows = []
    counts = Counter()
    by_symbol = Counter()
    by_flag = Counter()
    for flag in flags:
        symbol, day = flag["symbol"].strip().upper(), flag["date"]
        source = secondary[symbol].get(day)
        v3row = v3[symbol].get(day)
        if v3row is None:
            raise ValueError(f"flag date missing from v3 source for {symbol} {day}")
        path, sha = source_meta[symbol]
        if source is None:
            status, different, valid = "NO_SECONDARY_ROW", "", ""
        else:
            status, different, valid = compare_flag(flag, v3row, source)
            counts["matched_secondary_rows"] += 1
            counts["secondary_ohlc_valid"] += int(valid)
            counts["secondary_ohlc_invalid"] += int(not valid)
        counts[status] += 1
        by_symbol[symbol] += 1
        by_flag[flag["flag"]] += 1
        out_rows.append({
            "symbol": symbol, "date": day, "flag": flag["flag"],
            "secondary_status": status, "different_fields": different,
            "secondary_ohlc_valid": str(valid).upper() if valid != "" else "",
            "source_repository": SOURCE_REPO, "source_commit": SOURCE_COMMIT,
            "source_path": path, "source_git_blob_sha": sha,
            "disposition": "UNKNOWN_NO_INDEPENDENT_PRIMARY_SOURCE",
        })

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(out_rows)

    summary = {
        "status": "SECONDARY_PARITY_AUDIT_COMPLETE_NO_PROMOTIONS",
        "source_repository": SOURCE_REPO, "source_commit": SOURCE_COMMIT,
        "source_provenance": "ShareSansar-derived; not an independent NEPSE feed",
        "symbols": len(symbols), "flag_rows": len(out_rows),
        "secondary_rows_matched": counts["matched_secondary_rows"],
        "exact_matches_not_independent": counts["EXACT_MATCH_NOT_INDEPENDENT_CORROBORATION"],
        "secondary_value_differences": counts["SECONDARY_VALUE_DIFFERENCE_REVIEW"],
        "no_secondary_row": counts["NO_SECONDARY_ROW"],
        "secondary_rows_with_valid_ohlc": counts["secondary_ohlc_valid"],
        "secondary_rows_with_invalid_ohlc": counts["secondary_ohlc_invalid"],
        "promoted_or_repaired_rows": 0,
        "by_symbol": dict(by_symbol), "by_flag": dict(by_flag),
        "file_blob_shas": {s: meta[1] for s, meta in source_meta.items()},
    }
    Path(summary_path).write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--flags", type=Path, required=True)
    parser.add_argument("--v3-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--expected-flags", type=int, default=1368)
    args = parser.parse_args()
    build(args.flags, args.v3_dir, args.output, args.summary, args.expected_flags)


if __name__ == "__main__":
    main()
