#!/usr/bin/env python3
"""Compare open-session adjacent-repeat rows with official NEPSE EOD board captures."""
import argparse
import csv
import json
import sys
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

from validate_nepse_eod_capture import EvidenceError, validate_capture

FIELDS = ("open", "high", "low", "close", "volume", "turnover")


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def dec(value):
    try:
        return Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, TypeError):
        return None


def pairs_from_flags(path):
    pairs = []
    for row in read_csv(path):
        if row.get("classification") == "OPEN_SESSION_REPEAT_REVIEW":
            pairs.append({
                "symbol": row["symbol"].strip().upper(),
                "previous_date": row["previous_date"],
                "date": row["date"],
            })
    return pairs


def load_board(capture_dir, day):
    folder = Path(capture_dir) / day
    manifest = json.loads((folder / "capture_manifest.json").read_text(encoding="utf-8"))
    if manifest.get("status") != "COMPLETE_BOARD_CAPTURE" or manifest.get("business_date") != day:
        raise ValueError(f"incomplete or wrong-date official EOD board capture: {day}")
    if len(manifest.get("captured_pages", [])) != int(manifest.get("total_pages", -1)):
        raise ValueError(f"page count mismatch: {day}")
    rows = []
    for page in manifest["captured_pages"]:
        raw = Path(page["file"]).read_bytes()
        import hashlib
        if hashlib.sha256(raw).hexdigest() != page["sha256"]:
            raise ValueError(f"payload hash mismatch: {page['file']}")
        payload = json.loads(raw.decode("utf-8"))
        if len(payload.get("content", [])) != int(page["rows"]):
            raise ValueError(f"page row count mismatch: {page['file']}")
        rows.extend((row, page, raw, Path(page["file"])) for row in payload["content"])
    if len(rows) != int(manifest.get("total_elements", -1)):
        raise ValueError(f"board totalElements mismatch: {day}")
    return manifest, rows


def compare(repeat_flags, mapping_path, v2_dir, capture_dir, output_dir, expected_pairs=5):
    pairs = pairs_from_flags(repeat_flags)
    if len(pairs) != expected_pairs:
        raise ValueError(f"expected {expected_pairs} open repeat pairs, found {len(pairs)}")
    mapping = {r["symbol"].strip().upper(): r["security_id"].strip()
               for r in read_csv(mapping_path)}
    boards = {}
    output_rows = []
    for pair in pairs:
        symbol = pair["symbol"]
        if symbol not in mapping:
            raise ValueError(f"missing security ID for {symbol}")
        symbol_path = Path(v2_dir) / f"{symbol}_OHLCV.csv"
        v2_rows = {r["Date"]: r for r in read_csv(symbol_path)}
        for day in (pair["previous_date"], pair["date"]):
            if day not in boards:
                boards[day] = load_board(capture_dir, day)
            manifest, board_rows = boards[day]
            matches = [(row, page, raw, path) for row, page, raw, path in board_rows
                       if str(row.get("symbol", "")).strip().upper() == symbol
                       and str(row.get("businessDate", ""))[:10] == day]
            status = "UNKNOWN_OFFICIAL_EOD_ROW_NOT_FOUND"
            official = {}
            page = {}
            payload_path = Path("")
            if len(matches) > 1:
                status = "UNKNOWN_DUPLICATE_OFFICIAL_EOD_ROWS"
            elif len(matches) == 1:
                row, page, raw, payload_path = matches[0]
                try:
                    evidence = validate_capture(raw, symbol, day, page["url"],
                                                page["retrieved_at"], payload_path)
                    official = evidence["parsed_ohlcv"]
                    status = evidence["status"]
                except EvidenceError as exc:
                    status = "OFFICIAL_EOD_REVIEW_REQUIRED:" + str(exc)
                    official = {}
                official_id = str(row.get("securityId", ""))
                if status == "OFFICIAL_CAPTURE_ACCEPTED" and official_id != mapping[symbol]:
                    status = "UNKNOWN_SECURITY_ID_MISMATCH"

            v2 = v2_rows.get(day)
            changed = []
            if v2 and official:
                for field in FIELDS:
                    v2_value = v2.get(field.title(), "")
                    if dec(v2_value) != dec(official.get(field)):
                        changed.append(field)
            if status == "OFFICIAL_CAPTURE_ACCEPTED":
                if v2 is None:
                    status = "OFFICIAL_EOD_ROW_FOUND_BUT_V2_ROW_MISSING"
                elif changed:
                    status = "OFFICIAL_EOD_DIFFERS_FROM_V2"
                else:
                    status = "OFFICIAL_EOD_MATCHES_V2"

            output_rows.append({
                "symbol": symbol, "previous_date": pair["previous_date"],
                "repeat_date": pair["date"], "business_date_checked": day,
                "security_id": mapping[symbol],
                "official_capture_status": status,
                "official_open": official.get("open", ""),
                "official_high": official.get("high", ""),
                "official_low": official.get("low", ""),
                "official_close": official.get("close", ""),
                "official_volume": official.get("volume", ""),
                "official_turnover": official.get("turnover", ""),
                "official_trades": (matches[0][0].get("totalTrades", "") if len(matches) == 1 else ""),
                "v2_open": v2.get("Open", "") if v2 else "",
                "v2_high": v2.get("High", "") if v2 else "",
                "v2_low": v2.get("Low", "") if v2 else "",
                "v2_close": v2.get("Close", "") if v2 else "",
                "v2_volume": v2.get("Volume", "") if v2 else "",
                "changed_fields": ";".join(changed),
                "official_payload_sha256": page.get("sha256", "") if page else "",
                "official_source_url": page.get("url", "") if page else "",
                "official_retrieved_at": page.get("retrieved_at", "") if page else "",
            })

    summary_rows = []
    grouped = defaultdict(dict)
    for row in output_rows:
        grouped[(row["symbol"], row["previous_date"], row["repeat_date"])][row["business_date_checked"]] = row
    for (symbol, previous_date, repeat_date), dates in sorted(grouped.items()):
        prev = dates.get(previous_date, {})
        curr = dates.get(repeat_date, {})
        prev_ok = prev.get("official_capture_status") == "OFFICIAL_EOD_MATCHES_V2"
        curr_ok = curr.get("official_capture_status") == "OFFICIAL_EOD_MATCHES_V2"
        same_official = (
            prev_ok and curr_ok and all(
                dec(prev.get(f"official_{field}")) == dec(curr.get(f"official_{field}"))
                for field in FIELDS
            )
        )
        summary_rows.append({
            "symbol": symbol, "previous_date": previous_date, "repeat_date": repeat_date,
            "previous_eod_status": prev.get("official_capture_status", ""),
            "repeat_eod_status": curr.get("official_capture_status", ""),
            "both_official_rows_match_v2": str(prev_ok and curr_ok).upper(),
            "official_ohlcv_identical_across_pair": str(same_official).upper(),
            "risk_disposition": (
                "UNKNOWN_PENDING_FLOORSHEET_UNL_POLICY" if symbol == "UNL"
                else "OFFICIAL_EOD_CONFIRMED_LOW_LIQUIDITY_FLOORSHEET_STILL_REQUIRED"
                if prev_ok and curr_ok
                else "UNKNOWN_OFFICIAL_EOD_EVIDENCE_INCOMPLETE"
            ),
        })

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    row_fields = list(output_rows[0].keys()) if output_rows else []
    with (output_dir / "repeat_pair_official_eod_rows.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=row_fields)
        writer.writeheader()
        writer.writerows(output_rows)
    summary_fields = list(summary_rows[0].keys()) if summary_rows else []
    with (output_dir / "repeat_pair_official_eod_summary.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=summary_fields)
        writer.writeheader()
        writer.writerows(summary_rows)

    totals = {
        "repeat_pairs": len(summary_rows),
        "date_rows_checked": len(output_rows),
        "official_eod_matches_v2": sum(r["official_capture_status"] == "OFFICIAL_EOD_MATCHES_V2" for r in output_rows),
        "official_eod_differences": sum(r["official_capture_status"] == "OFFICIAL_EOD_DIFFERS_FROM_V2" for r in output_rows),
        "official_rows_missing_or_unresolved": sum(r["official_capture_status"] not in {"OFFICIAL_EOD_MATCHES_V2", "OFFICIAL_EOD_DIFFERS_FROM_V2"} for r in output_rows),
        "unl_pairs_kept_unknown": sum(r["symbol"] == "UNL" for r in summary_rows),
    }
    (output_dir / "repeat_pair_official_eod_totals.json").write_text(json.dumps(totals, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(totals, indent=2))
    return totals


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeat-flags", type=Path, required=True)
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--v2-dir", type=Path, required=True)
    parser.add_argument("--capture-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    compare(args.repeat_flags, args.mapping, args.v2_dir, args.capture_dir, args.output_dir)


if __name__ == "__main__":
    main()
