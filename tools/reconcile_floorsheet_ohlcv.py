"""Evidence-gated daily floorsheet to OHLCV reconciliation.

TRADED requires at least one valid contract in the date-matched file.
NO_TRADE requires a verified-open session AND a complete, hash-matched
floorsheet manifest. Every other absence is UNKNOWN.
"""
import argparse
import csv
import hashlib
import json
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def dec(value):
    try:
        return Decimal(str(value).strip().replace(",", ""))
    except (InvalidOperation, TypeError, ValueError):
        return None


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def reconcile_date(date, floor_path, ohlcv_dir, calendar, manifest):
    result = []
    session_status = calendar.get(date, "UNKNOWN")
    meta = manifest.get(date, {})
    raw_hash = sha256(floor_path) if floor_path.is_file() else ""
    hash_matches = bool(meta.get("source_sha256")) and raw_hash == meta.get("source_sha256")
    claimed_complete = (
        str(meta.get("floorsheet_complete", "")).strip().lower() == "true"
        and bool(meta.get("completeness_evidence", "").strip())
        and str(meta.get("source_uri", "")).strip().lower().startswith("https://")
        and hash_matches
    )

    trades = defaultdict(lambda: {"contracts": 0, "quantity": 0, "turnover": Decimal("0"), "bad_rows": 0})
    file_valid = floor_path.is_file()
    seen_contracts = set()
    if file_valid:
        with floor_path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            headers = {str(name).strip().lower() for name in (reader.fieldnames or [])}
            required_aliases = (
                bool(headers & {"trading_date", "trade_date", "date"}),
                "symbol" in headers,
                bool(headers & {"quantity"}),
                bool(headers & {"rate"}),
                bool(headers & {"transaction", "contract_no"}),
            )
            if not all(required_aliases):
                file_valid = False
            rows = list(reader) if file_valid else []
        for row in rows:
            d = (row.get("Trading_Date") or row.get("trade_date") or row.get("Date") or "").strip()
            symbol = (row.get("Symbol") or row.get("symbol") or "").strip().upper()
            qty = dec(row.get("Quantity") or row.get("quantity"))
            rate = dec(row.get("Rate") or row.get("rate"))
            contract = (row.get("Transaction") or row.get("Contract_No") or row.get("contract_no") or "").strip()
            if (d != date or not symbol or qty is None or rate is None or qty <= 0
                    or qty != qty.to_integral_value() or rate <= 0 or not contract
                    or contract in seen_contracts):
                file_valid = False
                if symbol:
                    trades[symbol]["bad_rows"] += 1
                continue
            seen_contracts.add(contract)
            trades[symbol]["contracts"] += 1
            trades[symbol]["quantity"] += int(qty)
            trades[symbol]["turnover"] += qty * rate

    observed_trade_count = sum(item["contracts"] for item in trades.values())
    observed_share_count = sum(item["quantity"] for item in trades.values())
    observed_turnover = sum((item["turnover"] for item in trades.values()), Decimal("0"))
    observed_symbol_count = sum(item["contracts"] > 0 for item in trades.values())
    totals_match = (
        dec(meta.get("expected_trades")) == observed_trade_count
        and dec(meta.get("expected_shares")) == observed_share_count
        and dec(meta.get("expected_turnover_npr")) == observed_turnover
        and dec(meta.get("expected_symbols")) == observed_symbol_count
    )
    complete = claimed_complete and file_valid and totals_match

    ohlcv_by_symbol = {}
    universe_symbols = set()
    for path in sorted(ohlcv_dir.glob("*_OHLCV.csv")):
        symbol = path.name[:-10].upper()
        universe_symbols.add(symbol)
        for row in read_csv(path):
            if (row.get("Date") or row.get("date") or "").strip() == date:
                if symbol in ohlcv_by_symbol:
                    # Duplicate date bars are ambiguous and must never support NO_TRADE.
                    ohlcv_by_symbol[symbol] = None
                else:
                    ohlcv_by_symbol[symbol] = dec(row.get("Volume") or row.get("volume"))

    # Include every current archive symbol, even when that date has no OHLCV row.
    # Otherwise an absent bar could silently disappear instead of receiving UNKNOWN/NO_TRADE.
    symbols = sorted(set(trades) | universe_symbols)
    for symbol in symbols:
        t = trades[symbol]
        contracts = t["contracts"]
        if contracts > 0 and t["bad_rows"] == 0 and file_valid:
            status = "TRADED"
        elif (contracts == 0 and file_valid and complete and hash_matches
              and session_status == "verified_open"
              and (symbol not in ohlcv_by_symbol or ohlcv_by_symbol[symbol] == 0)):
            status = "NO_TRADE"
        else:
            status = "UNKNOWN"

        ohlcv_volume = ohlcv_by_symbol.get(symbol)
        qty = Decimal(t["quantity"])
        turnover = t["turnover"]
        result.append({
            "date": date,
            "symbol": symbol,
            "trade_status": status,
            "session_status": session_status,
            "floorsheet_file": str(floor_path),
            "floorsheet_sha256": raw_hash,
            "floorsheet_complete_claim": str(meta.get("floorsheet_complete", "")).lower(),
            "completeness_evidence": meta.get("completeness_evidence", ""),
            "source_uri": meta.get("source_uri", ""),
            "manifest_hash_match": hash_matches,
            "floorsheet_claimed_complete": claimed_complete,
            "floorsheet_totals_match": totals_match,
            "observed_market_trades": observed_trade_count,
            "observed_market_shares": observed_share_count,
            "observed_market_turnover_npr": str(observed_turnover.quantize(Decimal("0.01"))),
            "observed_market_symbols": observed_symbol_count,
            "floorsheet_file_valid": file_valid,
            "contracts": contracts,
            "floorsheet_quantity": int(qty),
            "floorsheet_turnover_npr": str(turnover.quantize(Decimal("0.01"))),
            "floorsheet_vwap_npr": str((turnover / qty).quantize(Decimal("0.01"))) if qty else "",
            "ohlcv_volume": str(ohlcv_volume) if ohlcv_volume is not None else "",
            "volume_match": (ohlcv_volume == qty) if ohlcv_volume is not None and status == "TRADED" else "",
            "ohlcv_reconciliation": (
                "MATCH" if status == "TRADED" and ohlcv_volume == qty else
                "CONFLICT" if status == "TRADED" and ohlcv_volume is not None else
                "NOT_COMPARABLE"
            ),
            "resolution_reason": (
                "Positive valid date-matched contracts observed" if status == "TRADED" else
                "Verified-open session plus hash-matched complete extract, independently matching market totals, and zero symbol contracts/volume" if status == "NO_TRADE" else
                "Insufficient session, file validity, completeness, provenance or hash evidence"
            ),
        })
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--floorsheet-dir", type=Path, required=True)
    parser.add_argument("--ohlcv-dir", type=Path, required=True)
    parser.add_argument("--calendar", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    calendar = {r["date"]: r["status"] for r in read_csv(args.calendar)}
    manifest = {r["trading_date"]: r for r in read_csv(args.manifest)}
    dates = sorted({p.stem.replace("floorsheet_", "") for p in args.floorsheet_dir.glob("floorsheet_*.csv")})
    output = []
    for date in dates:
        output.extend(reconcile_date(date, args.floorsheet_dir / f"floorsheet_{date}.csv",
                                    args.ohlcv_dir, calendar, manifest))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(output[0]) if output else ["date", "symbol", "trade_status", "resolution_reason"]
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(output)
    counts = {}
    for row in output:
        counts[row["trade_status"]] = counts.get(row["trade_status"], 0) + 1
    print(json.dumps({"rows": len(output), "status_counts": counts, "no_trade_requires_verified_open_complete_hash_match": True}, indent=2))


if __name__ == "__main__":
    main()
