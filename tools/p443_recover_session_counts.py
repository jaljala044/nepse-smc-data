"""Recover secondary transaction-count candidates; never authorize publication."""
import csv
import hashlib
import io
import json
import re
import subprocess
from collections import Counter
from decimal import Decimal
from pathlib import Path

SOURCE = "524442d518d2f2705ade0680c9d2e3f90738e3d6"
INVENTORY = Path("reference/P443_SESSION_CONTROL_SECONDARY_SOURCE_INVENTORY.csv")
SUMMARY = Path("scanner_inputs/market_summary_daily.csv")

def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))

def number(value, integral=False):
    if not re.fullmatch(r"(?:[0-9]+|[0-9]{1,3}(?:,[0-9]{3})+)(?:\.[0-9]+)?", value.strip()):
        raise ValueError("Invalid numeric field")
    n = Decimal(value.replace(",", ""))
    if not n.is_finite() or n < 0 or (integral and n != n.to_integral_value()):
        raise ValueError("Invalid total component")
    return n

def summarize(raw):
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    headers = reader.fieldnames or []
    if len(headers) != len(set(headers)) or not {"Symbol","Vol","Turnover","Trans."}.issubset(headers):
        raise ValueError("Unexpected daily CSV schema")
    seen = set()
    quantity = turnover = trades = Decimal(0)
    for row in reader:
        if None in row or any(v is None for v in row.values()):
            raise ValueError("Malformed daily CSV row")
        symbol = row["Symbol"].strip().upper()
        if not symbol or symbol in seen:
            raise ValueError("Missing or duplicate symbol")
        seen.add(symbol)
        quantity += number(row["Vol"], True)
        turnover += number(row["Turnover"])
        trades += number(row["Trans."], True)
    if not seen or min(quantity, turnover, trades) <= 0:
        raise ValueError("Empty or zero daily totals")
    return len(seen), int(quantity), turnover, int(trades)

def run(source, output):
    inventory = rows(INVENTORY)
    market = rows(SUMMARY)
    baseline = {r["date"]:r for r in market}
    if len(inventory) != 149 or len({r["date"] for r in inventory}) != 149 or len(baseline) != len(market):
        raise ValueError("Inventory coverage or baseline uniqueness mismatch")
    result = []
    for item in inventory:
        day = item["date"]
        expected = baseline[day]
        record = dict(date=day, source_blob=item["git_blob_sha"], symbols="", quantity="", turnover="", transactions="", status="", error="", publication_allowed="false")
        try:
            if expected["transactions"] or item["path"] != "docs/Data/" + day.replace("-","_") + ".csv":
                raise ValueError("Unexpected recovery candidate")
            raw = subprocess.check_output(["git","-C",str(source),"show",SOURCE+":"+item["path"]])
            if len(raw) != int(item["bytes"]) or hashlib.sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest() != item["git_blob_sha"]:
                raise ValueError("Source integrity mismatch")
            symbols, quantity, turnover, trades = summarize(raw)
            record.update(symbols=symbols,quantity=quantity,turnover=str(turnover),transactions=trades)
            matches = (symbols == int(expected["traded_securities"]) and quantity == int(expected["traded_shares"]) and turnover == Decimal(expected["turnover_npr"]))
            record["status"] = "CANDIDATE_TOTALS_MATCH" if matches else "BASELINE_TOTALS_CONFLICT"
        except (ValueError, ArithmeticError, KeyError, subprocess.CalledProcessError, UnicodeError) as exc:
            record.update(status="REVIEW_ERROR",error=str(exc))
        result.append(record)
    # Flag identical archive blobs across different dates; date is filename evidence only.
    counts = Counter(r["source_blob"] for r in result)
    for record in result:
        if counts[record["source_blob"]] > 1:
            record["status"] = "REPEATED_SOURCE_BLOB_REVIEW"
    output.mkdir(parents=True, exist_ok=True)
    with (output/"session_recovery.csv").open("w",encoding="utf-8",newline="") as stream:
        writer = csv.DictWriter(stream,fieldnames=list(result[0]))
        writer.writeheader()
        writer.writerows(result)
    summary = {"rows":len(result),"counts":dict(Counter(r["status"] for r in result)),"promoted":0,"source_commit":SOURCE}
    (output/"summary.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))

if __name__ == "__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("source",type=Path)
    p.add_argument("output",type=Path)
    args=p.parse_args()
    run(args.source,args.output)
