#!/usr/bin/env python3
"""Build derived OHLCV v3 by applying only P4.30 official Open corrections."""
import argparse
import csv
import hashlib
import json
import shutil
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlparse

OFFICIAL_HOSTS = {"www.nepalstock.com", "nepalstock.com", "www.nepalstock.com.np", "nepalstock.com.np"}
OHLCV = ("open", "high", "low", "close", "volume")


def git_blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def dec(value):
    try:
        return Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, TypeError):
        return None


def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def build(v2_dir, raw_dir, matrix_path, correction_path, output_dir,
          expected_symbols=281, expected_corrections=11, overwrite=False):
    v2_dir, raw_dir, output_dir = Path(v2_dir), Path(raw_dir), Path(output_dir)
    if output_dir.resolve() in (v2_dir.resolve(), raw_dir.resolve()):
        raise ValueError("v3 output cannot replace v2 or raw source")
    if output_dir.exists() and any(output_dir.iterdir()):
        if not overwrite or output_dir.name != "ohlcv_v3":
            raise ValueError("output must be empty; --overwrite only allowed for ohlcv_v3")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = read_csv(v2_dir / "manifest.csv")
    if len(manifest) != expected_symbols or len({r["symbol"] for r in manifest}) != expected_symbols:
        raise ValueError(f"expected {expected_symbols} unique v2 securities")
    matrix = read_csv(matrix_path)
    corrections = read_csv(correction_path)
    if len(matrix) != expected_corrections or len(corrections) != expected_corrections:
        raise ValueError(f"expected {expected_corrections} official matrix/correction rows")
    by_key = {(r["symbol"], r["business_date"]): r for r in matrix}
    if len(by_key) != len(matrix):
        raise ValueError("duplicate official matrix symbol/date")
    correction_keys = [(r["symbol"], r["business_date"]) for r in corrections]
    if len(correction_keys) != len(set(correction_keys)):
        raise ValueError("duplicate correction ledger symbol/date")
    if set(correction_keys) != set(by_key):
        raise ValueError("correction ledger keys do not exactly match official matrix")

    correction_by_symbol = defaultdict(list)
    for corr in corrections:
        key = (corr["symbol"], corr["business_date"])
        row = by_key[key]
        if corr.get("field") != "Open" or corr.get("disposition") != "PRIMARY_OFFICIAL_NEPSE_EOD_OPEN_CORRECTION":
            raise ValueError(f"unsupported correction disposition: {key}")
        if row.get("official_capture_status") != "OFFICIAL_CAPTURE_ACCEPTED" or row.get("official_row_count") != "1":
            raise ValueError(f"official capture not accepted/unique: {key}")
        if row.get("official_quality_flags", "").strip():
            raise ValueError(f"official quality flags block promotion: {key}")
        if row.get("official_security_id") != row.get("mapping_security_id") or not row.get("official_security_id"):
            raise ValueError(f"security ID mismatch: {key}")
        if corr.get("official_security_id") != row.get("official_security_id"):
            raise ValueError(f"correction security ID mismatch: {key}")
        if corr.get("official_payload_sha256") != row.get("official_payload_sha256"):
            raise ValueError(f"payload hash mismatch: {key}")
        if corr.get("official_value") != row.get("official_open") or corr.get("candidate_value") != row.get("candidate_open"):
            raise ValueError(f"correction values differ from official matrix: {key}")
        host = urlparse(row.get("official_source_url", "")).hostname
        if host not in OFFICIAL_HOSTS or not row.get("official_payload_sha256"):
            raise ValueError(f"official source provenance missing/invalid: {key}")
        retrieved = datetime.fromisoformat(row["official_retrieved_at"])
        if retrieved.tzinfo is None or retrieved.utcoffset() is None:
            raise ValueError(f"official retrieval timestamp must be timezone-aware: {key}")

        candidate = {k: dec(row.get(f"candidate_{k}")) for k in OHLCV}
        official = {k: dec(row.get(f"official_{k}")) for k in OHLCV}
        if any(v is None for v in (*candidate.values(), *official.values())):
            raise ValueError(f"non-numeric official/candidate OHLCV: {key}")
        if candidate["open"] == official["open"] or not (
            candidate["open"] > candidate["high"] or candidate["open"] < candidate["low"]
        ):
            raise ValueError(f"candidate does not require an Open correction: {key}")
        if not official["low"] <= official["open"] <= official["high"]:
            raise ValueError(f"official Open outside range: {key}")
        for field in ("high", "low", "close", "volume"):
            if candidate[field] != official[field]:
                raise ValueError(f"unexpected {field} difference: {key}")
        correction_by_symbol[corr["symbol"]].append((corr, row))

    v2_corrections = read_csv(v2_dir / "corrections.csv")
    provenance = read_csv(v2_dir / "provenance_ledger.csv")
    new_provenance = []
    new_corrections = []
    new_manifest = []
    raw_verified = v2_verified = rows_updated = 0

    for base in manifest:
        symbol = base["symbol"]
        raw_path = raw_dir / f"{symbol}_OHLCV.csv"
        v2_path = v2_dir / f"{symbol}_OHLCV.csv"
        if not raw_path.is_file() or not v2_path.is_file():
            raise ValueError(f"missing raw/v2 file for {symbol}")
        raw_sha = git_blob_sha(raw_path.read_bytes())
        v2_bytes = v2_path.read_bytes()
        v2_sha = git_blob_sha(v2_bytes)
        if raw_sha != base["raw_source_blob_sha"]:
            raise ValueError(f"raw source changed for {symbol}")
        if v2_sha != base["derived_blob_sha"]:
            raise ValueError(f"v2 source changed for {symbol}")
        raw_verified += 1
        v2_verified += 1

        text = v2_bytes.decode("utf-8-sig")
        lines = text.splitlines()
        if not lines or lines[0].split(",") != ["Date", "Open", "High", "Low", "Close", "Volume"]:
            raise ValueError(f"unexpected v2 OHLCV header for {symbol}")
        header = lines[0]
        out_lines = [header]
        changed_for_symbol = correction_by_symbol.get(symbol, [])
        by_date = {}
        for index, line in enumerate(lines[1:], start=1):
            if not line.strip():
                continue
            parsed = next(csv.reader([line]))
            if len(parsed) != 6:
                raise ValueError(f"unexpected OHLCV field count for {symbol}: {line!r}")
            day = parsed[0]
            if day in by_date:
                raise ValueError(f"duplicate date in v2 file for {symbol}: {day}")
            by_date[day] = index

        changes_by_line = {}
        for corr, official_row in changed_for_symbol:
            day = corr["business_date"]
            if day not in by_date:
                raise ValueError(f"official correction target missing in v2: {symbol} {day}")
            index = by_date[day]
            values = next(csv.reader([lines[index]]))
            if len(values) != 6:
                raise ValueError(f"unexpected OHLCV field count: {symbol} {day}")
            if dec(values[1]) != dec(corr["candidate_value"]):
                raise ValueError(f"candidate Open no longer matches v2: {symbol} {day}")
            if dec(values[2]) != dec(official_row["official_high"]) or dec(values[3]) != dec(official_row["official_low"]):
                raise ValueError(f"v2 H/L differ from official row: {symbol} {day}")
            if dec(values[4]) != dec(official_row["official_close"]) or dec(values[5]) != dec(official_row["official_volume"]):
                raise ValueError(f"v2 Close/Volume differ from official row: {symbol} {day}")
            values[1] = corr["official_value"]
            from io import StringIO
            buf = StringIO()
            csv.writer(buf, lineterminator="").writerow(values)
            changes_by_line[index] = buf.getvalue()
            new_corrections.append({
                "symbol": symbol, "date": day, "field": "Open",
                "raw_value": corr["candidate_value"], "derived_value": corr["official_value"],
                "source": "NEPSE Official EOD API", "source_url": corr["official_source_url"],
                "reason": f"Official EOD Open correction; security ID {corr['official_security_id']}; payload SHA-256 {corr['official_payload_sha256']}",
                "status": "applied_in_derived_v3",
            })
            new_provenance.append({
                "symbol": symbol, "candidate_status": "V2_OPEN_OUTSIDE_RANGE",
                "raw_date": day, "official_business_date": day,
                "action": "OFFICIAL_OPEN_FIELD_CORRECTION",
                "official_security_id": corr["official_security_id"],
                "official_open": official_row["official_open"], "official_high": official_row["official_high"],
                "official_low": official_row["official_low"], "official_close": official_row["official_close"],
                "official_volume": official_row["official_volume"], "official_turnover": official_row["official_turnover"],
                "candidate_open": corr["candidate_value"], "candidate_high": official_row["candidate_high"],
                "candidate_low": official_row["candidate_low"], "candidate_close": official_row["candidate_close"],
                "candidate_volume": official_row["candidate_volume"], "candidate_turnover": "",
                "changed_fields": "open", "official_payload_sha256": corr["official_payload_sha256"],
                "official_source_url": corr["official_source_url"], "official_retrieved_at": corr["official_retrieved_at"],
            })

        for index, line in enumerate(lines[1:], start=1):
            if line.strip():
                out_lines.append(changes_by_line.get(index, line))
        output_bytes = v2_bytes if not changed_for_symbol else ("\n".join(out_lines) + "\n").encode("utf-8")
        (output_dir / f"{symbol}_OHLCV.csv").write_bytes(output_bytes)
        rows_updated += len(changed_for_symbol)
        new_manifest.append({
            "symbol": symbol, "raw_source_blob_sha": raw_sha,
            "v2_source_blob_sha": v2_sha,
            "derived_path": f"derived/ohlcv_v3/{symbol}_OHLCV.csv",
            "derived_blob_sha": git_blob_sha(output_bytes),
            "rows": len(by_date), "official_open_corrections": len(changed_for_symbol),
        })

    if raw_verified != expected_symbols or v2_verified != expected_symbols or rows_updated != expected_corrections:
        raise ValueError("raw/v2 preservation or correction coverage incomplete")

    write_csv(output_dir / "manifest.csv", new_manifest, list(new_manifest[0]))
    correction_fields = ["symbol", "date", "field", "raw_value", "derived_value", "source", "source_url", "reason", "status"]
    write_csv(output_dir / "corrections.csv", v2_corrections + new_corrections, correction_fields)
    provenance_fields = list(dict.fromkeys(k for r in (provenance + new_provenance) for k in r))
    write_csv(output_dir / "provenance_ledger.csv", provenance + new_provenance, provenance_fields)
    if (v2_dir / "quality_flags").is_dir():
        shutil.copytree(v2_dir / "quality_flags", output_dir / "quality_flags")
    totals = {
        "status": "OFFICIAL_EOD_V3_11_OPEN_CORRECTIONS_APPLIED",
        "symbols": expected_symbols,
        "derived_rows": sum(int(r["rows"]) for r in new_manifest),
        "raw_source_files_verified": raw_verified,
        "v2_source_files_verified": v2_verified,
        "official_open_corrections_applied": rows_updated,
        "raw_source_files_modified": 0,
        "v2_source_files_modified": 0,
        "unverified_rows_promoted": 0,
    }
    (output_dir / "totals.json").write_text(json.dumps(totals, indent=2) + "\n", encoding="utf-8")
    (output_dir / "README.md").write_text(
        "# NEPSE Common-Equity OHLCV — Derived Dataset v3\n\n"
        "Status: official-EOD-backed; 11 additional recent Open corrections applied\n"
        f"Scope: {expected_symbols} common-equity securities; {totals['derived_rows']} rows\n\n"
        "## P4.30 corrections\n\n"
        "- 11 official NEPSE EOD Open corrections applied to the v2 derived series.\n"
        "- Each correction has exact symbol/date, official security ID, payload SHA-256, source URL and retrieval timestamp.\n"
        "- Only Open changed; High, Low, Close and Volume were independently checked against the official row.\n"
        "- v2 and raw OHLCV sources remain immutable.\n"
        "- Historical anomalies without primary evidence remain flagged; no other rows were repaired.\n",
        encoding="utf-8",
    )
    print(json.dumps(totals, indent=2))
    return totals


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--v2-dir", type=Path, required=True)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--corrections", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--expected-symbols", type=int, default=281)
    parser.add_argument("--expected-corrections", type=int, default=11)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    build(args.v2_dir, args.raw_dir, args.matrix, args.corrections, args.output_dir,
          args.expected_symbols, args.expected_corrections, args.overwrite)


if __name__ == "__main__":
    main()
