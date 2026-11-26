#!/usr/bin/env python3
"""Download and validate pinned historical daily floorsheet CSV candidates.

The script separates file integrity, row validity, independent market-total
reconciliation, and per-security absence evidence. It never promotes a file
to complete merely because it parses successfully.
"""
import argparse
import csv
import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path


def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def decimal(value):
    try:
        return Decimal(str(value).strip().replace(",", ""))
    except (InvalidOperation, TypeError, ValueError):
        return None


def canonical_symbol(value):
    return str(value or "").strip().upper()


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_blob_sha1(path):
    size = path.stat().st_size
    digest = hashlib.sha1()
    digest.update(f"blob {size}\0".encode())
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_one(item, out_dir, timeout=90):
    date = item["date"]
    commit = item["source_commit"]
    path = item["path"]
    url = f"https://raw.githubusercontent.com/{item['source_repository']}/{commit}/{path}"
    target = out_dir / f"floorsheet_{date}.csv"
    last_error = ""
    headers = {}
    for attempt in range(4):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "NEPSE-P420-Evidence-Audit/1.0"})
            with urllib.request.urlopen(request, timeout=timeout) as response, target.open("wb") as output:
                headers = {k.lower(): v for k, v in response.headers.items()}
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    output.write(chunk)
            break
        except (OSError, urllib.error.URLError, TimeoutError) as exc:
            last_error = str(exc)
            target.unlink(missing_ok=True)
            time.sleep(2 ** attempt)
    else:
        return {
            "date": date, "url": url, "download_status": "FAIL",
            "error": last_error, "path": str(target),
        }

    actual_size = target.stat().st_size
    actual_sha256 = sha256_file(target)
    actual_git_sha = git_blob_sha1(target)
    expected_size = int(item["size_bytes"])
    git_match = actual_git_sha == item["git_blob_sha"]
    size_match = actual_size == expected_size
    return {
        "date": date, "url": url, "path": str(target),
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "http_etag": headers.get("etag", ""),
        "http_last_modified": headers.get("last-modified", ""),
        "http_content_length": headers.get("content-length", ""),
        "actual_size_bytes": actual_size, "expected_size_bytes": expected_size,
        "size_match": size_match, "actual_sha256": actual_sha256,
        "actual_git_blob_sha": actual_git_sha,
        "expected_git_blob_sha": item["git_blob_sha"],
        "git_blob_match": git_match,
        "download_status": "PASS" if size_match and git_match else "FAIL",
        "error": "",
    }


def validate_file(item, downloaded, equity_symbols, ohlcv):
    date = item["date"]
    path = Path(downloaded["path"])
    errors = Counter()
    by_symbol = defaultdict(lambda: {"contracts": 0, "shares": 0, "turnover": Decimal("0")})
    seen = set()
    trades = shares = 0
    turnover = Decimal("0")
    symbols = set()
    amount_failures = 0
    rows_read = 0
    headers = []
    if downloaded["download_status"] != "PASS":
        return {
            "date": date, "content_status": "UNKNOWN", "completeness_status": "UNKNOWN",
            "rows": 0, "trades": 0, "shares": 0, "turnover_npr": "",
            "symbols": 0, "duplicate_contracts": "", "amount_identity_failures": "",
            "date_mismatches": "", "invalid_rows": "", "broker_ids_missing": "",
            "ohlcv_matches": 0, "ohlcv_conflicts": 0, "ohlcv_rows_absent": 0,
        }, []

    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        headers = [str(h or "").strip().lower() for h in (reader.fieldnames or [])]
        required = {"transaction", "symbol", "buyer", "seller", "quantity", "rate", "amount", "date"}
        if not required.issubset(set(headers)):
            errors["schema"] += 1
            return {
                "date": date, "content_status": "FAIL", "completeness_status": "UNKNOWN",
                "rows": 0, "trades": 0, "shares": 0, "turnover_npr": "",
                "symbols": 0, "duplicate_contracts": 0, "amount_identity_failures": 0,
                "date_mismatches": 0, "invalid_rows": 1, "broker_ids_missing": 0,
                "ohlcv_matches": 0, "ohlcv_conflicts": 0, "ohlcv_rows_absent": 0,
                "validation_errors": "required_columns_missing",
            }, []

        for row in reader:
            rows_read += 1
            if None in row:
                errors["extra_columns"] += 1
            contract = str(row.get("transaction") or "").strip()
            symbol = canonical_symbol(row.get("symbol"))
            buyer = str(row.get("buyer") or "").strip()
            seller = str(row.get("seller") or "").strip()
            trade_date = str(row.get("date") or "").strip()[:10]
            qty = decimal(row.get("quantity"))
            rate = decimal(row.get("rate"))
            amount = decimal(row.get("amount"))

            invalid = False
            if not contract or contract in seen:
                errors["duplicate_or_missing_contract"] += 1
                invalid = True
            if contract:
                seen.add(contract)
            if not symbol:
                errors["missing_symbol"] += 1
                invalid = True
            if trade_date != date:
                errors["date_mismatch"] += 1
                invalid = True
            if qty is None or qty <= 0 or qty != qty.to_integral_value():
                errors["invalid_quantity"] += 1
                invalid = True
            if rate is None or rate <= 0:
                errors["invalid_rate"] += 1
                invalid = True
            if amount is None or amount <= 0:
                errors["invalid_amount"] += 1
                invalid = True
            if not buyer or not seller or not buyer.isdigit() or not seller.isdigit():
                errors["missing_or_invalid_broker_id"] += 1
                invalid = True
            if qty is not None and rate is not None and amount is not None:
                if abs(qty * rate - amount) > Decimal("0.01"):
                    errors["amount_identity_failure"] += 1
                    amount_failures += 1
                    invalid = True
            if invalid:
                continue

            q = int(qty)
            trades += 1
            shares += q
            turnover += amount
            symbols.add(symbol)
            by_symbol[symbol]["contracts"] += 1
            by_symbol[symbol]["shares"] += q
            by_symbol[symbol]["turnover"] += amount

    invalid_count = sum(errors.values())
    content_status = "PASS" if rows_read > 0 and invalid_count == 0 else "FAIL"
    # Only 2026-11-20 has an independent, contract-level, full-session
    # market-total comparison currently admitted by this audit.
    expected = None
    if date == "2026-11-20":
        expected = {
            "trades": 39966, "shares": 10602468,
            "turnover": Decimal("3887563470.82"), "symbols": 352,
        }
    totals_match = bool(expected and trades == expected["trades"]
                        and shares == expected["shares"]
                        and turnover == expected["turnover"]
                        and len(symbols) == expected["symbols"])
    completeness = "PASS_INDEPENDENT_TOTALS" if content_status == "PASS" and totals_match else "UNKNOWN"
    equity_rows = []
    ohlcv_matches = ohlcv_conflicts = ohlcv_absent = 0
    for symbol in sorted(equity_symbols):
        agg = by_symbol.get(symbol, {"contracts": 0, "shares": 0, "turnover": Decimal("0")})
        bar = ohlcv.get((symbol, date), "ABSENT")
        if agg["contracts"] > 0:
            status = "TRADED" if content_status == "PASS" else "UNKNOWN"
            if bar == "ABSENT":
                comparison = "OHLCV_ROW_ABSENT"
                ohlcv_absent += 1
            elif bar is None:
                comparison = "OHLCV_DUPLICATE_OR_INVALID"
                ohlcv_conflicts += 1
            elif Decimal(str(bar)) == Decimal(agg["shares"]):
                comparison = "MATCH"
                ohlcv_matches += 1
            else:
                comparison = "CONFLICT"
                ohlcv_conflicts += 1
        else:
            if completeness == "PASS_INDEPENDENT_TOTALS" and (bar == "ABSENT" or bar == 0):
                status = "NO_TRADE"
            else:
                status = "UNKNOWN"
            comparison = "NOT_COMPARABLE"
        equity_rows.append({
            "date": date, "symbol": symbol, "trade_status": status,
            "contracts": agg["contracts"], "floorsheet_shares": agg["shares"],
            "floorsheet_turnover_npr": str(agg["turnover"].quantize(Decimal("0.01"))),
            "ohlcv_volume": "" if bar == "ABSENT" else ("" if bar is None else str(bar)),
            "ohlcv_comparison": comparison,
            "session_completeness": completeness,
        })

    summary = {
        "date": date, "source_path": item["path"],
        "download_sha256": downloaded.get("actual_sha256", ""),
        "git_blob_match": downloaded.get("git_blob_match", False),
        "size_match": downloaded.get("size_match", False),
        "content_status": content_status,
        "completeness_status": completeness,
        "rows": rows_read, "trades": trades, "shares": shares,
        "turnover_npr": str(turnover.quantize(Decimal("0.01"))),
        "symbols": len(symbols),
        "duplicate_contracts": errors["duplicate_or_missing_contract"],
        "amount_identity_failures": amount_failures,
        "date_mismatches": errors["date_mismatch"],
        "invalid_rows": invalid_count,
        "broker_ids_missing": errors["missing_or_invalid_broker_id"],
        "ohlcv_matches": ohlcv_matches, "ohlcv_conflicts": ohlcv_conflicts,
        "ohlcv_rows_absent": ohlcv_absent,
        "validation_errors": json.dumps(dict(errors), sort_keys=True),
    }
    return summary, equity_rows


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--universe", type=Path, required=True)
    parser.add_argument("--ohlcv-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--download-workers", type=int, default=8)
    args = parser.parse_args()

    manifest = read_csv(args.manifest)
    if len(manifest) != 226 or len({r["date"] for r in manifest}) != 226:
        raise SystemExit(f"expected 226 unique manifest dates, got {len(manifest)}")
    equity_symbols = sorted({
        canonical_symbol(r["symbol"]) for r in read_csv(args.universe)
        if canonical_symbol(r.get("symbol"))
        and (not r.get("instrument_class_from_rendered_list")
             or r.get("instrument_class_from_rendered_list", "").strip() == "Equity")
    })
    if len(equity_symbols) != 281:
        raise SystemExit(f"expected 281 equity symbols, got {len(equity_symbols)}")

    ohlcv = {}
    for file in args.ohlcv_dir.glob("*_OHLCV.csv"):
        symbol = file.name[:-10].upper()
        with file.open(newline="", encoding="utf-8-sig") as handle:
            for row in csv.DictReader(handle):
                date = str(row.get("Date") or row.get("date") or "").strip()[:10]
                if not date:
                    continue
                key = (symbol, date)
                if key in ohlcv:
                    ohlcv[key] = None
                else:
                    ohlcv[key] = decimal(row.get("Volume") or row.get("volume"))

    input_dir = args.output_dir / "downloads"
    input_dir.mkdir(parents=True, exist_ok=True)
    downloads = {}
    with ThreadPoolExecutor(max_workers=max(1, args.download_workers)) as pool:
        futures = {pool.submit(download_one, row, input_dir): row for row in manifest}
        for future in as_completed(futures):
            row = futures[future]
            try:
                downloads[row["date"]] = future.result()
            except Exception as exc:
                downloads[row["date"]] = {
                    "date": row["date"], "download_status": "FAIL", "error": str(exc),
                    "url": "", "path": "",
                }

    download_rows = [downloads[d] for d in sorted(downloads)]
    summaries, equity_rows = [], []
    for item in manifest:
        date = item["date"]
        summary, per_equity = validate_file(item, downloads[date], equity_symbols, ohlcv)
        summaries.append(summary)
        equity_rows.extend(per_equity)

    write_csv(args.output_dir / "download_integrity.csv", download_rows)
    write_csv(args.output_dir / "daily_validation_summary.csv", summaries)
    write_csv(args.output_dir / "equity_date_dispositions.csv", equity_rows)
    counts = Counter(r["download_status"] for r in download_rows)
    content = Counter(r["content_status"] for r in summaries)
    complete = Counter(r["completeness_status"] for r in summaries)
    statuses = Counter(r["trade_status"] for r in equity_rows)
    print(json.dumps({
        "manifest_dates": len(manifest), "equity_symbols": len(equity_symbols),
        "download_status": dict(counts), "content_status": dict(content),
        "completeness_status": dict(complete), "equity_date_status": dict(statuses),
        "sha256_calculated_for": sum(bool(r.get("actual_sha256")) for r in download_rows),
        "interpretation": "File integrity and row validity do not prove full-session completeness. NO_TRADE is permitted only for 2026-11-20 with independent total reconciliation.",
    }, indent=2))
    if counts["FAIL"] or content["FAIL"]:
        raise SystemExit("One or more files failed integrity/content validation; see CSV artifacts")


if __name__ == "__main__":
    main()
