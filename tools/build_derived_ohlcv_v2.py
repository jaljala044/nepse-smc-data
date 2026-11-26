#!/usr/bin/env python3
"""Build derived OHLCV v2 using only row-matched official NEPSE EOD evidence.

Raw source files are read-only. Date shifts, insertions and field corrections
are applied only to a new derived directory.
"""
import argparse
import csv
import hashlib
import json
import shutil
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

V1_FIELDS = ["Date", "Open", "High", "Low", "Close", "Volume"]
OFFICIAL_FIELDS = ("open", "high", "low", "close", "volume")
SHIFT_RAW_DATES = {"2026-03-01": "2026-03-02", "2026-07-24": "2026-07-25"}
EXPECTED_STATUS = {
    "ALREADY_RECOVERED_DATE_SHIFT",
    "QUARANTINE_INVALID_EXTERNAL_OHLCV",
}


def git_blob_sha(data):
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


def dec(value):
    try:
        return Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, TypeError):
        return None


def fmt(value):
    number = dec(value)
    if number is None:
        raise ValueError(f"not a numeric OHLCV value: {value!r}")
    return format(number, "f")


def valid_ohlcv(row):
    o, h, l, c, v = (dec(row.get(k)) for k in OFFICIAL_FIELDS)
    return (
        None not in (o, h, l, c, v)
        and min(o, h, l, c) > 0
        and h >= max(o, l, c)
        and l <= min(o, h, c)
        and v >= 0
    )


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def read_preserved_lines(path):
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    if not lines:
        raise ValueError(f"empty OHLCV file: {path}")
    header = next(csv.reader([lines[0]]))
    if header != V1_FIELDS:
        raise ValueError(f"unexpected OHLCV header in {path}: {header}")
    rows = {}
    for line in lines[1:]:
        if not line.strip():
            continue
        values = next(csv.reader([line]))
        if len(values) != len(V1_FIELDS):
            raise ValueError(f"invalid OHLCV line in {path}: {line!r}")
        row = dict(zip(V1_FIELDS, values))
        day = row["Date"]
        if day in rows:
            raise ValueError(f"duplicate date {day} in {path}")
        rows[day] = (row, line)
    return lines[0], rows


def official_line(row):
    values = [
        row["business_date"],
        fmt(row["official_open"]),
        fmt(row["official_high"]),
        fmt(row["official_low"]),
        fmt(row["official_close"]),
        fmt(row["official_volume"]),
    ]
    return ",".join(values)


def build(v1_dir, raw_dir, official_matrix, calendar_path, output_dir,
          expected_official_rows=599, expected_symbols=281, expected_shift_rows=490, expected_insert_rows=109, overwrite=False):
    v1_dir = Path(v1_dir)
    raw_dir = Path(raw_dir)
    output_dir = Path(output_dir)
    if output_dir.resolve() == v1_dir.resolve() or output_dir.resolve() == raw_dir.resolve():
        raise ValueError("output directory cannot replace v1 or raw source directory")
    if output_dir.exists() and any(output_dir.iterdir()):
        if not overwrite:
            raise ValueError("output directory must be empty unless --overwrite is supplied")
        if output_dir.name != "ohlcv_v2":
            raise ValueError("--overwrite is restricted to an output directory named ohlcv_v2")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    v1_manifest = read_csv(v1_dir / "manifest.csv")
    if len(v1_manifest) != expected_symbols or len({r["symbol"] for r in v1_manifest}) != expected_symbols:
        raise ValueError(f"v1 manifest must contain exactly {expected_symbols} unique symbols")
    calendar = {r["date"]: r["status"] for r in read_csv(calendar_path)}
    matrix = read_csv(official_matrix)
    if expected_official_rows is not None and len(matrix) != expected_official_rows:
        raise ValueError(f"expected {expected_official_rows} official rows, found {len(matrix)}")
    keys = [(r["symbol"], r["business_date"]) for r in matrix]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate symbol/business_date rows in official matrix")

    counts = defaultdict(int)
    by_symbol = defaultdict(list)
    for row in matrix:
        if row.get("candidate_status") not in EXPECTED_STATUS:
            raise ValueError(f"unexpected candidate status: {row.get('candidate_status')}")
        if row.get("official_capture_status") != "OFFICIAL_CAPTURE_ACCEPTED":
            raise ValueError(f"official capture not accepted: {row['symbol']} {row['business_date']}")
        if row.get("official_quality_flags", "").strip():
            raise ValueError(f"official quality flags: {row['symbol']} {row['business_date']}")
        if row.get("official_row_count") != "1":
            raise ValueError(f"official row is not unique: {row['symbol']} {row['business_date']}")
        if not row.get("official_security_id") or row["official_security_id"] != row.get("mapping_security_id"):
            raise ValueError(f"security ID mismatch: {row['symbol']} {row['business_date']}")
        if not valid_ohlcv({k: row.get(f"official_{k}") for k in OFFICIAL_FIELDS}):
            raise ValueError(f"official OHLCV invalid: {row['symbol']} {row['business_date']}")
        by_symbol[row["symbol"]].append(row)
        counts[row["candidate_status"]] += 1

    if counts["ALREADY_RECOVERED_DATE_SHIFT"] != expected_shift_rows or counts["QUARANTINE_INVALID_EXTERNAL_OHLCV"] != expected_insert_rows:
        raise ValueError(f"unexpected candidate counts: {dict(counts)}")

    correction_rows = []
    v1_corrections_path = v1_dir / "corrections.csv"
    if v1_corrections_path.exists():
        correction_rows.extend(read_csv(v1_corrections_path))
    provenance_rows = []
    new_manifest = []
    total_raw_rows = total_derived_rows = total_removed = total_inserted = 0

    for base in v1_manifest:
        symbol = base["symbol"]
        raw_path = raw_dir / f"{symbol}_OHLCV.csv"
        v1_path = v1_dir / f"{symbol}_OHLCV.csv"
        if not raw_path.is_file() or not v1_path.is_file():
            raise ValueError(f"missing raw/v1 file for {symbol}")
        raw_bytes = raw_path.read_bytes()
        v1_bytes = v1_path.read_bytes()
        raw_blob = git_blob_sha(raw_bytes)
        v1_blob = git_blob_sha(v1_bytes)
        if raw_blob != base["raw_source_blob_sha"]:
            raise ValueError(f"raw source blob changed for {symbol}")
        if v1_blob != base["derived_blob_sha"]:
            raise ValueError(f"v1 derived blob changed for {symbol}")

        header, rows = read_preserved_lines(v1_path)
        original_count = len(rows)
        actions = by_symbol.get(symbol, [])
        remove_dates = set()
        insert_rows = {}
        symbol_action_count = 0
        symbol_shift_count = 0
        symbol_insert_count = 0
        symbol_field_corrections = 0

        for item in actions:
            day = item["business_date"]
            raw_day = ""
            candidate = {k: item.get(f"candidate_{k}", "") for k in OFFICIAL_FIELDS}
            official = {k: item.get(f"official_{k}", "") for k in OFFICIAL_FIELDS}
            changed_fields = [
                k for k in ("open", "high", "low", "close", "volume", "turnover")
                if dec(item.get(f"candidate_{k}")) != dec(item.get(f"official_{k}"))
            ]
            if any(k not in {"open", "close"} for k in changed_fields):
                raise ValueError(f"unexpected official field changes for {symbol} {day}: {changed_fields}")

            if item["candidate_status"] == "ALREADY_RECOVERED_DATE_SHIFT":
                raw_day = SHIFT_RAW_DATES.get(day, "")
                if not raw_day:
                    raise ValueError(f"unexpected date-shift business date: {day}")
                if calendar.get(day) != "verified_open_observed" or calendar.get(raw_day) != "verified_closed":
                    raise ValueError(f"session calendar does not support shift {symbol}: {raw_day} -> {day}")
                if raw_day not in rows:
                    raise ValueError(f"raw date row missing for shift {symbol}: {raw_day}")
                if raw_day in remove_dates:
                    raise ValueError(f"duplicate shift removal for {symbol} {raw_day}")
                raw_row = rows[raw_day][0]
                raw_tuple = tuple(dec(raw_row[k.title()]) for k in ("open", "high", "low", "close", "volume"))
                candidate_tuple = tuple(dec(candidate[k]) for k in OFFICIAL_FIELDS)
                if raw_tuple != candidate_tuple:
                    raise ValueError(f"raw row does not match candidate tuple for {symbol} {raw_day}")
                if day in rows or day in insert_rows:
                    raise ValueError(f"target date already exists for shifted row {symbol} {day}")
                remove_dates.add(raw_day)
                insert_rows[day] = item
                symbol_shift_count += 1
                correction_rows.append({
                    "symbol": symbol, "date": day, "field": "Date",
                    "raw_value": raw_day, "derived_value": day,
                    "source": "NEPSE Official EOD API", "source_url": item["official_source_url"],
                    "reason": f"Official businessDate; raw SMC row on {raw_day} is a verified closed session; payload SHA-256 {item['official_payload_sha256']}",
                    "status": "applied_in_derived_v2",
                })
                action = "SHIFT_RAW_CLOSED_DATE_TO_OFFICIAL_BUSINESS_DATE"
            else:
                if day in rows or day in insert_rows:
                    raise ValueError(f"cannot insert official row over existing raw row: {symbol} {day}")
                if dec(candidate["open"]) is None or not (
                    dec(candidate["open"]) > dec(candidate["high"])
                    or dec(candidate["open"]) < dec(candidate["low"])
                ):
                    raise ValueError(f"candidate was not OHLC-invalid as expected: {symbol} {day}")
                insert_rows[day] = item
                symbol_insert_count += 1
                correction_rows.append({
                    "symbol": symbol, "date": day, "field": "Row",
                    "raw_value": "MISSING_IN_V1_RAW_DERIVED",
                    "derived_value": "|".join([day] + [fmt(official[k]) for k in OFFICIAL_FIELDS]),
                    "source": "NEPSE Official EOD API", "source_url": item["official_source_url"],
                    "reason": f"Official row found exactly once and passed validation; inserted using payload SHA-256 {item['official_payload_sha256']}",
                    "status": "applied_in_derived_v2",
                })
                action = "INSERT_OFFICIAL_EOD_ROW"

            for field in changed_fields:
                correction_rows.append({
                    "symbol": symbol, "date": day, "field": field.title(),
                    "raw_value": item.get(f"candidate_{field}", ""),
                    "derived_value": item.get(f"official_{field}", ""),
                    "source": "NEPSE Official EOD API", "source_url": item["official_source_url"],
                    "reason": f"Official EOD differs from secondary candidate; payload SHA-256 {item['official_payload_sha256']}",
                    "status": "applied_in_derived_v2",
                })
                symbol_field_corrections += 1
            symbol_action_count += 1 + len(changed_fields)

            provenance_rows.append({
                "symbol": symbol, "candidate_status": item["candidate_status"],
                "raw_date": raw_day, "official_business_date": day, "action": action,
                "official_security_id": item["official_security_id"],
                "official_open": item["official_open"], "official_high": item["official_high"],
                "official_low": item["official_low"], "official_close": item["official_close"],
                "official_volume": item["official_volume"], "official_turnover": item["official_turnover"],
                "candidate_open": item["candidate_open"], "candidate_high": item["candidate_high"],
                "candidate_low": item["candidate_low"], "candidate_close": item["candidate_close"],
                "candidate_volume": item["candidate_volume"], "candidate_turnover": item["candidate_turnover"],
                "changed_fields": ";".join(changed_fields),
                "official_payload_sha256": item["official_payload_sha256"],
                "official_source_url": item["official_source_url"],
                "official_retrieved_at": item["official_retrieved_at"],
            })

        output_lines = []
        for day, (row, line) in rows.items():
            if day not in remove_dates:
                output_lines.append((day, line))
        for day, item in insert_rows.items():
            output_lines.append((day, official_line(item)))
        output_lines.sort(key=lambda x: x[0])
        output_dates = [day for day, _ in output_lines]
        if len(output_dates) != len(set(output_dates)):
            raise ValueError(f"duplicate output dates for {symbol}")
        output_bytes = v1_bytes if not actions else (header + "\n" + "\n".join(line for _, line in output_lines) + "\n").encode("utf-8")
        out_path = output_dir / f"{symbol}_OHLCV.csv"
        out_path.write_bytes(output_bytes)

        _, final_rows = read_preserved_lines(out_path)
        for day, item in insert_rows.items():
            row = final_rows.get(day)
            if row is None:
                raise ValueError(f"official row missing after build: {symbol} {day}")
            expected = tuple(dec(item.get(f"official_{k}")) for k in OFFICIAL_FIELDS)
            actual = tuple(dec(row[0][k.title()]) for k in ("open", "high", "low", "close", "volume"))
            if actual != expected:
                raise ValueError(f"official row mismatch after build: {symbol} {day}")

        total_raw_rows += original_count
        total_derived_rows += len(output_lines)
        total_removed += len(remove_dates)
        total_inserted += len(insert_rows)
        new_manifest.append({
            "symbol": symbol,
            "raw_source_path": base["raw_source_path"],
            "raw_source_blob_sha": raw_blob,
            "derived_path": f"derived/ohlcv_v2/{symbol}_OHLCV.csv",
            "derived_blob_sha": git_blob_sha(output_bytes),
            "rows": len(output_lines),
            "derivation_status": "official_eod_v2" if actions else base["derivation_status"],
            "correction_count": int(base.get("correction_count", 0)) + symbol_action_count,
            "official_rows_applied": len(actions),
            "date_shift_count": symbol_shift_count,
            "inserted_rows": symbol_insert_count,
            "field_correction_count": symbol_field_corrections,
        })

    if len(provenance_rows) != expected_official_rows or total_removed != expected_shift_rows or total_inserted != expected_official_rows:
        raise ValueError(
            f"unexpected applied counts: official={len(provenance_rows)}, "
            f"removed={total_removed}, inserted={total_inserted}"
        )

    correction_fields = ["symbol", "date", "field", "raw_value", "derived_value", "source", "source_url", "reason", "status"]
    with (output_dir / "corrections.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=correction_fields)
        writer.writeheader()
        writer.writerows(correction_rows)

    provenance_fields = list(provenance_rows[0].keys())
    with (output_dir / "provenance_ledger.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=provenance_fields)
        writer.writeheader()
        writer.writerows(provenance_rows)

    manifest_fields = list(new_manifest[0].keys())
    with (output_dir / "manifest.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=manifest_fields)
        writer.writeheader()
        writer.writerows(new_manifest)

    if (v1_dir / "quality_flags").is_dir():
        shutil.copytree(v1_dir / "quality_flags", output_dir / "quality_flags")

    totals = {
        "status": "OFFICIAL_EOD_V2_DERIVED_NOT_FULL_SESSION_CLEAN",
        "symbols": len(new_manifest),
        "raw_source_rows": total_raw_rows,
        "derived_rows": total_derived_rows,
        "official_eod_rows_applied": len(provenance_rows),
        "date_shift_rows": counts["ALREADY_RECOVERED_DATE_SHIFT"],
        "inserted_rows": counts["QUARANTINE_INVALID_EXTERNAL_OHLCV"],
        "raw_rows_removed_from_closed_dates": total_removed,
        "field_corrections": sum(r["field_correction_count"] for r in new_manifest),
        "raw_source_files_modified": 0,
        "unverified_rows_promoted": 0,
    }
    (output_dir / "totals.json").write_text(json.dumps(totals, indent=2) + "\n", encoding="utf-8")
    readme = f"""# NEPSE Common-Equity OHLCV — Derived Dataset v2

Status: official-EOD-backed derived release; not fully session-clean  
Scope: {len(new_manifest)} common-equity symbols  
Raw preservation: all raw source files are read-only and their Git blob SHAs were checked against the v1 manifest.

## P4.28 official evidence applied

- 599 official NEPSE EOD rows across 254 symbols and six business dates.
- 490 one-day date shifts moved from raw closed dates to the official business dates in this derived view.
- 109 official rows inserted where the SMC v1 raw-derived file had no row.
- 112 field corrections applied from official EOD: 109 Open and 3 Close.
- Every official row passed the strict EOD capture validator with zero quality flags and a matching security ID.
- Original official payload SHA-256, URL and retrieval timestamp are preserved in provenance_ledger.csv.

## Preservation and limitations

- No file under 03_stock_charts_ohlcv/ was modified.
- v1 remains unchanged and is preserved as the prior release.
- Adjacent repeated OHLCV rows and remaining source quality flags are retained; this release does not claim full expected-session completeness.
- Rows without official evidence are not changed or promoted.

## Files

- *_OHLCV.csv: derived symbol files.
- manifest.csv: raw and derived Git blob hashes, row counts and official coverage.
- corrections.csv: row/date/field changes, including the prior RHGCL correction.
- provenance_ledger.csv: 599 exact official EOD row references.
- totals.json: build totals.
"""
    (output_dir / "README.md").write_text(readme, encoding="utf-8")
    print(json.dumps(totals, indent=2))
    return totals


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--v1-dir", type=Path, required=True)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--official-matrix", type=Path, required=True)
    parser.add_argument("--calendar", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--expected-official-rows", type=int, default=599)
    parser.add_argument("--expected-symbols", type=int, default=281)
    parser.add_argument("--expected-shift-rows", type=int, default=490)
    parser.add_argument("--expected-insert-rows", type=int, default=109)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    build(args.v1_dir, args.raw_dir, args.official_matrix, args.calendar,
          args.output_dir, args.expected_official_rows, args.expected_symbols, args.expected_shift_rows, args.expected_insert_rows, args.overwrite)


if __name__ == "__main__":
    main()
