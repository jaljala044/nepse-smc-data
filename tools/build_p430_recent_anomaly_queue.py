#!/usr/bin/env python3
"""Extract recent OHLCV invariant anomalies into a primary-source audit queue."""
import argparse
import csv
from pathlib import Path

TARGET_DATES = {"2026-04-24", "2026-04-27", "2026-04-28", "2026-04-29"}
EXPECTED_COUNT = 11
FIELDS = ["symbol", "date", "status", "open", "high", "low", "close", "volume", "turnover"]


def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def build(v2_dir, flags_path, mapping_path, output_path, expected_count=EXPECTED_COUNT):
    v2_dir = Path(v2_dir)
    flags = read_csv(flags_path)
    mapping = {r["symbol"].strip().upper(): r for r in read_csv(mapping_path)}
    candidates = [r for r in flags if r.get("date") in TARGET_DATES]
    if any(r.get("flag") != "OPEN_OUTSIDE_RANGE" for r in candidates):
        raise ValueError("unexpected invariant type in the selected recent-date queue")
    keys = [(r["symbol"].strip().upper(), r["date"]) for r in candidates]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate symbol/date in recent anomaly flags")
    if expected_count is not None and len(candidates) != expected_count:
        raise ValueError(f"expected {expected_count} recent anomalies, found {len(candidates)}")

    output = []
    for flag in candidates:
        symbol = flag["symbol"].strip().upper()
        if symbol not in mapping:
            raise ValueError(f"missing security-ID mapping for {symbol}")
        file_path = v2_dir / f"{symbol}_OHLCV.csv"
        if not file_path.is_file():
            raise ValueError(f"missing v2 OHLCV file for {symbol}")
        rows = read_csv(file_path)
        matches = [r for r in rows if r.get("Date") == flag["date"]]
        if len(matches) != 1:
            raise ValueError(f"expected one v2 row for {symbol} {flag['date']}, found {len(matches)}")
        row = matches[0]
        if not (float(row["Open"]) > float(row["High"]) or float(row["Open"]) < float(row["Low"])):
            raise ValueError(f"flag no longer matches v2 OHLC for {symbol} {flag['date']}")
        output.append({
            "symbol": symbol, "date": flag["date"], "status": flag["flag"],
            "open": row["Open"], "high": row["High"], "low": row["Low"],
            "close": row["Close"], "volume": row["Volume"],
            "turnover": row.get("Turnover", ""),
        })

    output.sort(key=lambda r: (r["date"], r["symbol"]))
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(output)
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--v2-dir", type=Path, required=True)
    parser.add_argument("--flags", type=Path, required=True)
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = build(args.v2_dir, args.flags, args.mapping, args.output)
    print({"rows": len(rows), "dates": sorted({r["date"] for r in rows}), "symbols": len({r["symbol"] for r in rows})})


if __name__ == "__main__":
    main()
