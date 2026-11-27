"""Combine the supplemental NEPSE inputs with an existing scanner data directory."""
import argparse
import csv
import hashlib
import shutil
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from tempfile import TemporaryDirectory

try:
    from .historical_quarantine import load_holds, reject_held, validate_rows
except ImportError:
    from historical_quarantine import load_holds, reject_held, validate_rows

SUPPLEMENT = Path(__file__).resolve().parent
TABLE_EXTENSIONS = (".csv", ".xlsx", ".xls")


def rows(path):
    with path.open(newline="", encoding="utf-8-sig") as stream:
        yield from csv.DictReader(stream)


def write(path, fields, values):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(values)


def has_table(directory, *names):
    return any((directory / f"{name}{suffix}").exists()
               for name in names for suffix in TABLE_EXTENSIONS)


def validate_daily(values, closed_dates):
    """Fail closed before publishing; never silently remove or repair rows."""
    seen = set()
    for number, row in enumerate(values, 2):
        symbol = row["symbol"].strip().upper()
        day = row["date"].strip()
        try:
            if not symbol or date.fromisoformat(day).isoformat() != day:
                raise ValueError("invalid symbol/date")
            o, h, l, c, v = (Decimal(row[k]) for k in ("open", "high", "low", "close", "volume"))
            if not all(x.is_finite() for x in (o, h, l, c, v)):
                raise ValueError("non-finite OHLCV")
            if min(o, h, l, c) <= 0 or v < 0 or v != v.to_integral_value() or h < max(o, l, c) or l > min(o, h, c):
                raise ValueError("invalid OHLCV")
            if day in closed_dates:
                raise ValueError("verified closed session")
            key = (symbol, day)
            if key in seen:
                raise ValueError("duplicate symbol/date")
            seen.add(key)
        except (ValueError, InvalidOperation, TypeError, KeyError, AttributeError) as exc:
            raise ValueError(f"Rejected daily row {number}: {symbol} {day}: {exc}") from exc


def verified_closed_dates():
    reference = SUPPLEMENT.parent / "reference"
    calendar = reference / "nepse_canonical_session_calendar_2025-2026.csv"
    positive = reference / "nepse_positive_open_sessions_2025-11-26_2026-11-25.csv"
    closed = {r["date"] for r in rows(calendar)
              if r["status"] == "verified_closed" and r["scope"] == "all_securities"}
    opened = {r["date"] for r in rows(positive) if r["status"] == "verified_open"}
    if not closed or not opened or closed & opened:
        raise ValueError("Missing or conflicting session evidence")
    return closed


BLOCKED_FLOORSHEET_BLOBS = {
    "0dd938bc5e6bfd50fa09bf85f0836d443ab15983",
    "49d6498bfb30681b7896b6c5c824b518e50f941d",
}
BLOCKED_FLOORSHEET_SHA256 = {
    "441f2b64106b48086a0326604ab92c40f2e02fa163bca97cfe17385c9f88ebc8",
    "beee6326be30d364eb6b0c55a2c36d9aa847daeb0af1bf5ddb2e4d3b82850433",
}


def validate_floorsheet(path, closed_dates, holds=None):
    """Validate canonical trade CSV; reject ambiguous schemas and unsupported formats."""
    raw = path.read_bytes()
    blob_sha = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
    content_sha256 = hashlib.sha256(raw).hexdigest()
    if blob_sha in BLOCKED_FLOORSHEET_BLOBS or content_sha256 in BLOCKED_FLOORSHEET_SHA256:
        raise ValueError("Quarantined floorsheet archive")
    if path.suffix != ".csv":
        raise ValueError("Unsupported floorsheet format; verified CSV required")
    aliases = {
        "identity": ("tradebookid", "recordid", "id", "transactionid"),
        "contract": ("contractno", "contractnumber", "contractid"),
        "date": ("date", "tradingdate", "tradedate", "businessdate", "calculationdate"),
        "symbol": ("symbol", "stocksymbol", "scrip"),
        "buyer": ("buyer", "buyerbroker", "buyermemberid"),
        "seller": ("seller", "sellerbroker", "sellermemberid"),
        "quantity": ("quantity", "qty", "contractquantity"),
        "rate": ("rate", "price", "contractrate"),
        "amount": ("amount", "turnover", "contractamount"),
    }
    def norm(s):
        return "".join(x.lower() for x in s if x.isalnum())
    seen = set()
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        headers = reader.fieldnames or []
        lookup = {norm(h): h for h in headers}
        if len(lookup) != len(headers):
            raise ValueError("Ambiguous floorsheet headers")
        cols = {k: next((lookup[a] for a in opts if a in lookup), None) for k, opts in aliases.items()}
        if any(not cols[k] for k in aliases if k != "identity"):
            raise ValueError("Missing required floorsheet fields")
        for number, row in enumerate(reader, 2):
            try:
                if None in row or any(v is None for v in row.values()):
                    raise ValueError("Malformed row")
                def val(k):
                    return row[cols[k]].strip() if cols[k] else ""
                day = val("date")
                if date.fromisoformat(day).isoformat() != day or day in closed_dates:
                    raise ValueError("Invalid or closed session")
                if not all(val(k) for k in ("contract", "symbol", "buyer", "seller")):
                    raise ValueError("Missing trade fields")
                if holds is not None:
                    reject_held(val("symbol"), day, holds)
                identity = val("identity") if cols["identity"] else val("contract")
                if not identity or (day, identity) in seen:
                    raise ValueError("Missing or duplicate transaction identity")
                seen.add((day, identity))
                q, p, a = (Decimal(val(k)) for k in ("quantity", "rate", "amount"))
                if not all(x.is_finite() and x > 0 for x in (q, p, a)) or q != q.to_integral_value():
                    raise ValueError("Invalid trade quantity, rate or amount")
                if abs(q * p - a) > Decimal("0.01"):
                    raise ValueError("Trade amount mismatch")
            except (ValueError, InvalidOperation, TypeError, KeyError) as exc:
                raise ValueError(f"Rejected floorsheet row {number}: {exc}") from exc
    if not seen:
        raise ValueError("Empty floorsheet")


def aggregate_daily(values, period, closed_dates):
    """Aggregate observed sessions only; period label is last observed date."""
    if period not in ("weekly", "monthly"):
        raise ValueError("Unsupported aggregation period")
    validate_daily(values, closed_dates)
    buckets = {}
    for row in sorted(values, key=lambda r: (r["symbol"].strip().upper(), r["date"].strip())):
        symbol = row["symbol"].strip().upper()
        day = date.fromisoformat(row["date"].strip())
        # Sunday-start trading week; independent of the historical weekday schedule.
        start = day - timedelta(days=(day.weekday() + 1) % 7) if period == "weekly" else day.replace(day=1)
        key = (symbol, start)
        o, h, l, c, v = (Decimal(row[k]) for k in ("open", "high", "low", "close", "volume"))
        if key not in buckets:
            buckets[key] = dict(symbol=symbol, date=day.isoformat(), open=o, high=h, low=l, close=c, volume=v)
        else:
            b = buckets[key]
            b.update(date=day.isoformat(), high=max(b["high"], h), low=min(b["low"], l), close=c, volume=b["volume"] + v)
    result = list(buckets.values())
    validate_daily(result, closed_dates)
    return result


def validate_broker_table(path, closed_dates, holds):
    if path.suffix.lower() != ".csv":
        raise ValueError("Unsupported broker format; verified CSV required")
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames or []
        if len(set(fields)) != len(fields) or not {"symbol", "date"}.issubset(fields):
            raise ValueError("Broker table requires unambiguous symbol/date")
        for row in reader:
            if None in row or any(v is None for v in row.values()):
                raise ValueError("Malformed broker row")
            reject_held(row["symbol"], row["date"], holds)
            if row["date"].strip() in closed_dates:
                raise ValueError("Broker row on verified closed session")


def prepare(original, output, overlay=None):
    if overlay is None:
        raise ValueError("Mandatory --quarantine-overlay required")
    holds = load_holds(overlay)
    if output.exists():
        raise FileExistsError(f"Choose a new output folder: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output.parent) as temp:
        stage = Path(temp) / "scanner-data"
        shutil.copytree(original, stage)
        daily = stage / "daily_prices.csv"
        with daily.open(newline="", encoding="utf-8-sig") as stream:
            fields = csv.DictReader(stream).fieldnames
        if not fields or not {"symbol", "date", "open", "high", "low", "close", "volume"}.issubset(fields):
            raise ValueError("Expected a scanner-format daily_prices.csv in the input folder.")
        original_rows = list(rows(daily))
        closed_dates = verified_closed_dates()
        validate_daily(original_rows, closed_dates)
        validate_rows(original_rows, holds)
        present = {(row["symbol"].strip().upper(), row["date"]) for row in original_rows}
        additions = []
        for path in [SUPPLEMENT / "benchmark_daily.csv", *sorted((SUPPLEMENT / "price_gap_fills").glob("*.csv"))]:
            for row in rows(path):
                key = row["symbol"], row["date"]
                if key not in present:
                    additions.append(row)
                    present.add(key)
        validate_daily(original_rows + additions, closed_dates)
        validate_rows(original_rows + additions, holds)
        if additions:
            extra = dict.fromkeys(field for row in additions for field in row if field not in fields)
            combined = sorted(original_rows + additions, key=lambda row: (row["symbol"], row["date"]))
            write(daily, [*fields, *extra], combined)
        # Always reconstruct both periods, including when no new daily rows arrive.
        for period in ("weekly", "monthly"):
            for suffix in TABLE_EXTENSIONS:
                (stage / f"{period}_prices{suffix}").unlink(missing_ok=True)
            write(stage / f"{period}_prices.csv",
                  ["symbol", "date", "open", "high", "low", "close", "volume"],
                  aggregate_daily(original_rows + additions, period, closed_dates))
        for name in ("sectors", "sector_data", "corporate_actions"):
            destination = stage / f"{name}.csv"
            if not has_table(stage, name):
                shutil.copyfile(SUPPLEMENT / destination.name, destination)
        broker_target = stage / "broker_summary.csv"
        if not has_table(stage, "broker_summary", "brokers", "floorsheet"):
            partitions = sorted((SUPPLEMENT / "broker_summary").glob("*.csv"))
            if not partitions:
                raise ValueError("Missing supplemental broker session files.")
            expected = ["symbol", "date", "broker", "buy_qty", "sell_qty", "buy_value", "sell_value"]
            with broker_target.open("w", newline="", encoding="utf-8") as target:
                writer = csv.DictWriter(target, expected)
                writer.writeheader()
                for path in partitions:
                    writer.writerows(rows(path))
        for candidate in stage.rglob("*"):
            if not candidate.is_file():
                continue
            name = candidate.name.lower()
            if name.startswith(("floorsheet.", "floorsheet_")) or "floorsheet" in candidate.relative_to(stage).parts[:-1]:
                validate_floorsheet(candidate, closed_dates, holds)
            elif name.startswith(("broker_summary.", "broker_summary_", "brokers.", "brokers_")) or any(p in {"broker_summary", "brokers"} for p in candidate.relative_to(stage).parts[:-1]):
                validate_broker_table(candidate, closed_dates, holds)
        stage.rename(output)
    print(f"Prepared {output} with {len(additions)} new daily price rows.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path, help="Existing data directory with daily_prices.csv")
    parser.add_argument("output", type=Path, help="A new output directory")
    parser.add_argument('--quarantine-overlay', type=Path, required=True, help='Pinned P4.43 hold overlay CSV')
    args = parser.parse_args()
    prepare(args.original, args.output, args.quarantine_overlay)
