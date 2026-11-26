"""Bulk date-grouped floorsheet evidence recovery; never promote or infer absence."""
import argparse
import csv
import json
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from pathlib import Path

try:
    from tools.p443_classify_repeated_candles import source_rows
    from tools.validate_historical_floorsheets import download_one, validate_file
except ModuleNotFoundError:
    from p443_classify_repeated_candles import source_rows
    from validate_historical_floorsheets import download_one, validate_file

EXPECTED_P2_REQUESTS = 68773
INVENTORY_PATH = "reference/p419_observed_date_floorsheet_archive_inventory_2026-11-26.csv"


def build_expected_tuples(keys, refs, loader=source_rows):
    """Load each pinned OHLCV source file once and resolve every lineage row."""
    grouped = defaultdict(list)
    for key, links in refs.items():
        for path, blob_sha, row_number in links:
            grouped[(path, blob_sha)].append((key, str(row_number)))

    expected = defaultdict(set)
    for (path, blob_sha), requests in sorted(grouped.items()):
        source = loader(path, blob_sha)
        for key, row_number in requests:
            if row_number not in source:
                raise ValueError(f"lineage row missing: {path}:{row_number}")
            day, values = source[row_number]
            if day != key[1]:
                raise ValueError(f"lineage date mismatch: {path}:{row_number}")
            expected[key].add(tuple(values))

    if set(expected) != set(keys):
        raise ValueError("source tuple coverage mismatch")
    return expected


def select_dates(bydate, inventory, max_dates):
    if max_dates < 1:
        raise ValueError("--max-dates must be at least 1")
    available = set(bydate).intersection(inventory)
    return sorted(available, key=lambda day: (-len(bydate[day]), day))[:max_dates]


def classify_request(expected_tuples, observed, has_inventory, fetched_status):
    """Return a conservative disposition; never infer no trade from missing rows."""
    if len(expected_tuples) != 1:
        return "SOURCE_TUPLE_CONFLICT"
    if not has_inventory:
        return "NO_PINNED_PARTITION"
    if fetched_status is None:
        return "AVAILABLE_NOT_FETCHED"
    if fetched_status != "PASS":
        return "PARTITION_VALIDATION_FAILED"
    if not observed:
        return "NO_OBSERVED_CONTRACT_UNKNOWN"

    _, expected_high, expected_low, _, expected_volume = next(iter(expected_tuples))
    observed_high = max(row[0] for row in observed)
    observed_low = min(row[0] for row in observed)
    observed_volume = sum((row[1] for row in observed), Decimal("0"))
    if (observed_high, observed_low, observed_volume) == (
        expected_high, expected_low, expected_volume
    ):
        return "HIGH_LOW_VOLUME_MATCH_OPEN_CLOSE_UNVERIFIED"
    return "HIGH_LOW_VOLUME_CONFLICT"


def compare_high_low_volume(source_tuple, observed):
    """Compare floorsheet-derived high/low/volume only; leave open/close unverified."""
    if len(source_tuple) != 5 or not observed:
        return None
    observed_high = max(row[0] for row in observed)
    observed_low = min(row[0] for row in observed)
    observed_volume = sum((row[1] for row in observed), Decimal("0"))
    return {
        "observed_high": observed_high,
        "observed_low": observed_low,
        "observed_volume": observed_volume,
        "high_match": observed_high == source_tuple[1],
        "low_match": observed_low == source_tuple[2],
        "volume_match": observed_volume == source_tuple[4],
    }


def read_inventory():
    inventory = {}
    with open(INVENTORY_PATH, newline="") as handle:
        for row in csv.DictReader(handle):
            if row["inventory_status"] != "FILE_PRESENT_IN_PINNED_GIT_TREE":
                continue
            day = row["date"]
            if day in inventory and inventory[day] != row:
                raise ValueError(f"ambiguous floorsheet inventory date: {day}")
            inventory[day] = row
    return inventory


def recover_partition(day, item, symbols, raw_directory):
    downloaded = download_one(item, raw_directory)
    summary, _ = validate_file(item, downloaded, symbols, {}, {})
    observed_by_symbol = defaultdict(list)

    if summary["content_status"] == "PASS":
        with open(downloaded["path"], newline="", encoding="utf-8-sig") as handle:
            for row in csv.DictReader(handle):
                symbol = row["symbol"].strip().upper()
                if symbol in symbols:
                    observed_by_symbol[symbol].append((
                        Decimal(row["rate"].replace(",", "")),
                        Decimal(row["quantity"].replace(",", "")),
                        row["transaction"],
                    ))

    return day, {
        "status": summary["content_status"],
        "observed": observed_by_symbol,
        "summary": summary,
        "download": downloaded,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", required=True)
    parser.add_argument("--max-dates", type=int, default=20)
    args = parser.parse_args()
    if args.max_dates < 1:
        parser.error("--max-dates must be at least 1")

    root = Path(args.directory)
    raw_directory = root.parent / "bulk-floor-cache"
    raw_directory.mkdir(exist_ok=True)

    with (root / "equity_security_date_recovery_queue.csv").open(newline="") as handle:
        queue = [
            row for row in csv.DictReader(handle)
            if row["priority"] == "P2_SESSION_AND_EXECUTION"
        ]
    keys = {(row["symbol"], row["date"]) for row in queue}
    if len(queue) != EXPECTED_P2_REQUESTS or len(keys) != len(queue):
        raise ValueError("equity evidence queue coverage or uniqueness mismatch")

    refs = defaultdict(set)
    with (root / "equity_security_date_source_lineage.csv").open(newline="") as handle:
        for row in csv.DictReader(handle):
            key = (row["symbol"], row["date"])
            if key in keys:
                refs[key].add((row["path"], row["blob_sha"], row["row"]))
    if set(refs) != keys:
        raise ValueError("lineage coverage mismatch")

    expected = build_expected_tuples(keys, refs)
    bydate = defaultdict(set)
    for symbol, day in keys:
        bydate[day].add(symbol)

    inventory = read_inventory()
    selected_dates = select_dates(bydate, inventory, args.max_dates)
    results = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [
            pool.submit(recover_partition, day, inventory[day], bydate[day], raw_directory)
            for day in selected_dates
        ]
        for future in futures:
            day, result = future.result()
            results[day] = result

    counts = Counter()
    output_path = root / "bulk_equity_floorsheet_disposition.csv"
    with output_path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "symbol", "date", "status", "source_blob", "contracts",
            "source_open", "source_high", "source_low", "source_close", "source_volume",
            "observed_high", "observed_low", "observed_volume",
            "high_match", "low_match", "volume_match",
            "source_tuple_count", "promotion_allowed",
        ])
        for symbol, day in sorted(keys):
            observed = []
            result = results.get(day)
            if result is not None and result["status"] == "PASS":
                observed = result["observed"].get(symbol, [])
            source_tuple_set = expected[(symbol, day)]
            status = classify_request(
                source_tuple_set,
                observed,
                day in inventory,
                result["status"] if result is not None else None,
            )
            source_values = next(iter(source_tuple_set)) if len(source_tuple_set) == 1 else ()
            field_comparison = compare_high_low_volume(source_values, observed)
            observed_high = field_comparison["observed_high"] if field_comparison else None
            observed_low = field_comparison["observed_low"] if field_comparison else None
            observed_volume = field_comparison["observed_volume"] if field_comparison else None
            high_match = field_comparison["high_match"] if field_comparison else None
            low_match = field_comparison["low_match"] if field_comparison else None
            volume_match = field_comparison["volume_match"] if field_comparison else None
            counts[status] += 1
            writer.writerow([
                symbol,
                day,
                status,
                inventory.get(day, {}).get("git_blob_sha", ""),
                len(observed),
                *(source_values if source_values else ("", "", "", "", "")),
                observed_high if observed_high is not None else "",
                observed_low if observed_low is not None else "",
                observed_volume if observed_volume is not None else "",
                str(high_match).lower() if high_match is not None else "",
                str(low_match).lower() if low_match is not None else "",
                str(volume_match).lower() if volume_match is not None else "",
                len(source_tuple_set),
                "false",
            ])

    report = {
        "requests": len(keys),
        "unique_dates": len(bydate),
        "available_dates": sum(day in inventory for day in bydate),
        "available_requests": sum(
            len(bydate[day]) for day in bydate if day in inventory
        ),
        "selected_dates": selected_dates,
        "status_counts": dict(counts),
        "session_validation": [results[day]["summary"] for day in selected_dates],
        "partition_downloads": [results[day]["download"] for day in selected_dates],
        "promoted": 0,
        "limitations": (
            "This is a bounded first batch selected by date-level request count. "
            "Only high, low and volume are compared; open and close remain unverified. "
            "Archive completeness and upstream independence are UNKNOWN. "
            "Missing contracts are UNKNOWN, not evidence of no trade. "
            "No source or canonical data is changed."
        ),
    }
    (root / "bulk_equity_floorsheet_summary.json").write_text(
        json.dumps(report, indent=2, default=str)
    )
    print(json.dumps({key: value for key, value in report.items()
                      if key not in {"session_validation", "partition_downloads"}}))


if __name__ == "__main__":
    main()
