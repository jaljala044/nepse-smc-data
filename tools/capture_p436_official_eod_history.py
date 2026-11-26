#!/usr/bin/env python3
"""Capture official NEPSE historical EOD price-volume responses for lifecycle cross-checks.

This is EOD evidence only: it is not a floorsheet, broker-flow, or contract-identity source.
Authentication secrets are held in memory and never persisted or printed.
"""
import base64
import hashlib
import json
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from capture_p435_authenticated_historical_floorsheets import (
    BASE, WASM_B64, WASM_GIT_BLOB_SHA, git_blob_sha, token_parser, request,
    parse_json, metadata,
)

TARGETS = [
    ("NMLBBL", 396, "2024-05-19", 864),
    ("NMLBBL", 396, "2024-05-16", 0),
    ("SMPDA", 2896, "2024-08-18", 5314),
    ("SMPDA", 2896, "2024-08-14", 0),
]
HISTORY_PATH = "/api/nots/market/history/security/{security_id}"

def find_rows(obj):
    """Return a discovered row collection and its JSON path; do not invent absent rows."""
    if isinstance(obj, list):
        return obj, "$"
    if not isinstance(obj, dict):
        return None, None
    for key in ("securityHistory", "content", "data", "history", "records", "result"):
        value = obj.get(key)
        if isinstance(value, list):
            return value, f"$.{key}"
        if isinstance(value, dict):
            rows, path = find_rows(value)
            if rows is not None:
                return rows, f"$.{key}{path[1:]}"
    return None, None

def find_total(obj):
    if not isinstance(obj, dict):
        return None, None, None
    for key in ("securityHistory", "data", "result"):
        nested = obj.get(key)
        if isinstance(nested, dict):
            te = nested.get("totalElements")
            tp = nested.get("totalPages")
            if isinstance(te, int) and isinstance(tp, int):
                return te, tp, f"$.{key}"
    te, tp = obj.get("totalElements"), obj.get("totalPages")
    if isinstance(te, int) and isinstance(tp, int):
        return te, tp, "$"
    return None, None, None

def first_value(row, names):
    for name in names:
        if name in row and row[name] is not None:
            return row[name], name
    return None, None

def inspect_rows(rows, expected_date):
    date_fields = ("businessDate", "date", "tradeDate", "transactionDate")
    symbol_fields = ("symbol", "stockSymbol", "securitySymbol")
    volume_fields = ("totalTradedQuantity", "totalTradedQty", "totalVolume", "volume", "totalTradedShares")
    ohlc_fields = {
        "open": ("openPrice", "open", "openPriceValue"),
        "high": ("highPrice", "high", "maxPrice"),
        "low": ("lowPrice", "low", "minPrice"),
        "close": ("closePrice", "close", "closingPrice"),
    }
    inspected = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        date, date_key = first_value(row, date_fields)
        symbol, symbol_key = first_value(row, symbol_fields)
        volume, volume_key = first_value(row, volume_fields)
        values = {}
        for label, aliases in ohlc_fields.items():
            values[label], _ = first_value(row, aliases)
        inspected.append({
            "date": str(date)[:10] if date is not None else None,
            "date_field": date_key,
            "symbol": str(symbol).upper() if symbol is not None else None,
            "symbol_field": symbol_key,
            "volume": str(volume) if volume is not None else None,
            "volume_field": volume_key,
            "ohlc": {k: (str(v) if v is not None else None) for k, v in values.items()},
            "has_all_ohlc": all(v is not None for v in values.values()),
        })
    return inspected

def capture(output_dir, requester=request, parser=token_parser, retrieved_at=None):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    stamp = retrieved_at or datetime.now(ZoneInfo("UTC")).isoformat()
    wasm = base64.b64decode(WASM_B64)
    wasm_sha = git_blob_sha(wasm)
    if wasm_sha != WASM_GIT_BLOB_SHA:
        raise ValueError("pinned upstream WASM Git blob SHA mismatch")
    records = []
    results = []
    with tempfile.TemporaryDirectory() as td:
        wasm_path = Path(td) / "css.wasm"
        wasm_path.write_bytes(wasm)
        token_url = BASE + "/api/authenticate/prove"
        status, headers, raw = requester("GET", token_url, None, {})
        token_meta = {"name": "token_prove", "url": token_url, **metadata(status, headers, raw)}
        token = parse_json(raw)
        if status != 200 or not isinstance(token, dict):
            records.append(token_meta)
            result = {"task": "P4.36", "retrieved_at_utc": stamp, "authentication_status": "token_prove_failed", "records": records, "results": []}
            (out / "capture_report.json").write_text(json.dumps(result, indent=2) + "\n")
            return result
        token_meta["token_fields_present"] = {k: bool(token.get(k)) for k in ("accessToken", "refreshToken", "salt1", "salt2", "salt3", "salt4", "salt5", "serverTime")}
        token_meta["body_saved"] = False
        records.append(token_meta)
        access, _refresh = parser(token, wasm_path)
        auth = {"Authorization": f"Salter {access}"}
        sec_url = BASE + "/api/nots/security?nonDelisted=true"
        ss, sh, sb = requester("GET", sec_url, None, auth)
        sec_meta = {"name": "security_list", "url": sec_url, **metadata(ss, sh, sb)}
        securities = parse_json(sb)
        if ss == 200 and isinstance(securities, list):
            (out / "security_list.json").write_bytes(sb)
            sec_meta["filename"] = "security_list.json"
        else:
            securities = []
        records.append(sec_meta)
        id_map = {str(x.get("symbol", "")).upper(): x.get("id") for x in securities if isinstance(x, dict)}
        for symbol, known_id, date, expected_volume in TARGETS:
            security_id = id_map.get(symbol)
            item = {
                "symbol": symbol, "security_id": security_id, "expected_security_id_from_prior_audit": known_id,
                "business_date": date, "expected_ohlcv_volume": expected_volume,
                "endpoint": HISTORY_PATH.format(security_id=security_id if security_id is not None else known_id),
            }
            if security_id is None:
                item["status"] = "security_id_missing"
                results.append(item)
                continue
            if security_id != known_id:
                item["security_id_changed_since_p435"] = True
            rows_all, page_records = [], []
            total_elements, total_pages = None, None
            failed = False
            for page in range(0, 100):
                query = f"?size=500&startDate={date}&endDate={date}&page={page}"
                url = BASE + HISTORY_PATH.format(security_id=security_id) + query
                st, hh, body = requester("GET", url, None, auth)
                obj = parse_json(body)
                page_rec = {"page": page, "url": url, **metadata(st, hh, body)}
                if st != 200 or obj is None:
                    page_rec["status"] = "http_or_json_failure"
                    page_rec["response_snippet"] = body.decode("utf-8", "replace")[:240]
                    page_records.append(page_rec)
                    failed = True
                    break
                rows, rows_path = find_rows(obj)
                if rows is None:
                    page_rec["status"] = "row_collection_not_identified"
                    page_rec["top_level_keys"] = sorted(obj.keys()) if isinstance(obj, dict) else None
                    page_records.append(page_rec)
                    failed = True
                    break
                te, tp, total_path = find_total(obj)
                if page == 0:
                    total_elements, total_pages = te, tp
                page_rec.update(status="captured", rows_path=rows_path, row_count=len(rows), total_elements=te, total_pages=tp, total_metadata_path=total_path)
                filename = f"{symbol}_{date}_page_{page}.json"
                (out / filename).write_bytes(body)
                page_rec["filename"] = filename
                page_records.append(page_rec)
                rows_all.extend(rows)
                if tp is None:
                    # One response is retained; without pagination metadata completeness is UNKNOWN.
                    break
                if tp == 0 or page + 1 >= tp:
                    break
            inspected = inspect_rows(rows_all, date)
            dates = [r["date"] for r in inspected if r["date"] is not None]
            wrong_dates = [d for d in dates if d != date]
            volume_values = [r["volume"] for r in inspected if r["volume"] is not None]
            item.update({
                "status": "captured" if not failed else "request_or_schema_failure",
                "pages": page_records,
                "rows": len(rows_all),
                "total_elements": total_elements,
                "total_pages": total_pages,
                "pagination_complete": (not failed and isinstance(total_elements, int) and isinstance(total_pages, int) and len(rows_all) == total_elements and len(page_records) == max(1, total_pages)),
                "date_fields_observed": sorted(set(r["date_field"] for r in inspected if r["date_field"])),
                "symbol_fields_observed": sorted(set(r["symbol_field"] for r in inspected if r["symbol_field"])),
                "volume_fields_observed": sorted(set(r["volume_field"] for r in inspected if r["volume_field"])),
                "all_ohlc_present_rows": sum(1 for r in inspected if r["has_all_ohlc"]),
                "missing_date_rows": sum(1 for r in inspected if r["date"] is None),
                "wrong_date_rows": len(wrong_dates),
                "observed_dates": sorted(set(dates)),
                "observed_symbols": sorted(set(r["symbol"] for r in inspected if r["symbol"])),
                "row_summaries": inspected,
                "volume_values": volume_values,
                "eod_volume_matches_expected": (len(volume_values) == 1 and volume_values[0] == str(expected_volume)),
                "evidence_gate_pass": False,
            })
            # Only an exact date/security row with complete OHLC and pagination can be considered a verified EOD match.
            item["evidence_gate_pass"] = (
                item["pagination_complete"] and len(inspected) > 0
                and item["missing_date_rows"] == 0 and item["wrong_date_rows"] == 0
                and all(r["date"] == date for r in inspected)
                and all(r["symbol"] == symbol for r in inspected if r["symbol"] is not None)
                and item["all_ohlc_present_rows"] == len(inspected)
                and len(volume_values) == 1 and volume_values[0] == str(expected_volume)
            )
            results.append(item)
    report = {
        "task": "P4.36",
        "source": "NEPSE official API domain",
        "retrieved_at_utc": stamp,
        "upstream_authentication_client": {
            "repo": "basic-bgnr/NepseUnofficialApi",
            "commit": "180a550c60f1959983b854659e650a4c189a3c0f",
            "wasm_git_blob_sha": wasm_sha,
        },
        "authentication_status": "authenticated" if id_map else "authenticated_but_security_list_unavailable",
        "records": records,
        "results": results,
        "interpretation": "Official EOD price-volume cross-check only. These responses are not floorsheets, do not establish contract identity or broker flow, and cannot establish a first-trade boundary without complete prior-session evidence. Tokens and salts were held in memory only.",
    }
    (out / "capture_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report

if __name__ == "__main__":
    report = capture("reference/p436_official_eod_history")
    for row in report["results"]:
        print(row["symbol"], row["business_date"], row["status"], "rows=", row.get("rows"), "complete=", row.get("pagination_complete"), "eod_match=", row.get("eod_volume_matches_expected"))
