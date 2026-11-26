"""Second-source HF floorsheet recovery for equity-priority repeat-pair dates."""
import argparse
import csv
import gzip
import hashlib
import io
import json
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from pathlib import Path

try:
    from tools.capture_p433_first_trade_floorsheets import BASE, fetch, tree_metadata
    from tools.p443_bulk_equity_floorsheet_recovery import (
        build_expected_tuples,
        classify_request,
        compare_high_low_volume,
        read_inventory,
    )
    from tools.p443_full_session_parity import signature
except ModuleNotFoundError:
    from capture_p433_first_trade_floorsheets import BASE, fetch, tree_metadata
    from p443_bulk_equity_floorsheet_recovery import (
        build_expected_tuples,
        classify_request,
        compare_high_low_volume,
        read_inventory,
    )
    from p443_full_session_parity import signature

EXPECTED_P2_REQUESTS = 68773


def select_hf_dates(bydate, primary_dates, hf_dates, max_dates, offset=0):
    if max_dates < 1 or offset < 0:
        raise ValueError("max_dates must be positive and offset non-negative")
    candidates = set(bydate).intersection(hf_dates).difference(primary_dates)
    ordered = sorted(candidates, key=lambda day: (-len(bydate[day]), day))
    return ordered[offset:offset + max_dates], ordered


def read_queue(root):
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
    return keys, refs


def parse_hf_session(reader, day, stats=None):
    """Validate rows but retain duplicate contract IDs as a separate review finding."""
    contracts = Counter()
    contract_ids = Counter()
    for row in reader:
        key = signature(row, True, day, stats)
        contracts[key] += 1
        contract_ids[key[1]] += 1
    if not contracts:
        raise ValueError("empty session")
    collisions = {contract: count for contract, count in contract_ids.items() if count > 1}
    collision_rows = [
        (key, count) for key, count in contracts.items() if key[1] in collisions
    ]
    return contracts, collisions, collision_rows


def recover_hf_partition(day, metadata, symbols, raw_directory):
    path = f"floorsheet/{day}.csv.gz"
    meta = metadata[path]
    try:
        status, headers, compressed = fetch(BASE + path)
        if status != 200:
            raise ValueError(f"HF HTTP status {status}")
        expected_sha256 = (meta.get("lfs") or {}).get("oid")
        actual_sha256 = hashlib.sha256(compressed).hexdigest()
        if not expected_sha256 or actual_sha256 != expected_sha256:
            raise ValueError("HF LFS SHA-256 mismatch")
        if len(compressed) != meta["size"]:
            raise ValueError("HF compressed size mismatch")

        raw = gzip.decompress(compressed)
        (raw_directory / f"floorsheet_{day}.csv").write_bytes(raw)
        stats = Counter()
        contracts, collisions, collision_rows = parse_hf_session(
            csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))),
            day,
            stats,
        )
        observed = defaultdict(list)
        if not collisions:
            for row, occurrences in contracts.items():
                date, contract, symbol, buyer, seller, quantity, rate, amount = row
                if symbol in symbols:
                    observed[symbol].extend([(rate, quantity, contract)] * occurrences)

        return day, {
            "status": "CONTRACT_ID_COLLISION_REVIEW" if collisions else "PASS",
            "observed": observed,
            "collision_rows": collision_rows,
            "summary": {
                "date": day,
                "rows": contracts.total(),
                "symbols": len({row[2] for row in contracts}),
                "unique_contract_ids": len(contracts),
                "duplicate_contract_ids": len(collisions),
                "duplicate_contract_occurrences": sum(count - 1 for count in collisions.values()),
                "leading_apostrophe_contract_ids": stats["leading_apostrophe_contract_ids"],
                "amount_exact_rows": stats["amount_exact_match"],
                "amount_floor_rows": stats["amount_floor_truncated"],
                "compressed_bytes": len(compressed),
                "compressed_sha256": actual_sha256,
                "compressed_git_blob": meta.get("oid"),
                "expected_lfs_sha256": expected_sha256,
                "expected_size_bytes": meta["size"],
            },
        }
    except Exception as error:
        return day, {
            "status": "FAIL",
            "observed": {},
            "error": str(error),
            "summary": {"date": day, "content_status": "UNKNOWN", "error": str(error)},
        }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", required=True)
    parser.add_argument("--max-dates", type=int, default=22)
    parser.add_argument("--offset", type=int, default=0)
    args = parser.parse_args()
    if args.max_dates < 1 or args.offset < 0:
        parser.error("--max-dates must be positive and --offset non-negative")

    root = Path(args.directory)
    raw_directory = root.parent / "hf-bulk-floor-cache"
    raw_directory.mkdir(exist_ok=True)

    keys, refs = read_queue(root)
    expected = build_expected_tuples(keys, refs)
    bydate = defaultdict(set)
    for symbol, day in keys:
        bydate[day].add(symbol)

    primary_inventory = read_inventory()
    primary_dates = set(primary_inventory).intersection(bydate)
    metadata = tree_metadata()
    hf_dates = {
        path.removeprefix("floorsheet/").removesuffix(".csv.gz")
        for path in metadata
        if path.startswith("floorsheet/") and path.endswith(".csv.gz")
    }
    selected, ordered_hf_only = select_hf_dates(
        bydate, primary_dates, hf_dates, args.max_dates, args.offset
    )
    hf_available = set(bydate).intersection(hf_dates)
    hf_only_available = hf_available.difference(primary_dates)

    results = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [
            pool.submit(recover_hf_partition, day, metadata, bydate[day], raw_directory)
            for day in selected
        ]
        for future in futures:
            day, result = future.result()
            results[day] = result

    counts = Counter()
    output_path = root / "hf_bulk_equity_floorsheet_disposition.csv"
    with output_path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "symbol", "date", "status", "source_path", "source_git_blob",
            "source_sha256", "contracts", "source_open", "source_high",
            "source_low", "source_close", "source_volume", "observed_high",
            "observed_low", "observed_volume", "high_match", "low_match",
            "volume_match", "source_tuple_count", "promotion_allowed",
        ])
        for symbol, day in sorted(keys):
            source_tuple_set = expected[(symbol, day)]
            observed = []
            result = results.get(day)
            if day in primary_dates:
                status = "PRIMARY_ARCHIVE_ALREADY_CHECKED"
            elif day not in hf_dates:
                status = "NO_HF_PINNED_PARTITION"
            elif result is None:
                status = "HF_AVAILABLE_NOT_FETCHED"
            elif result["status"] == "CONTRACT_ID_COLLISION_REVIEW":
                status = "CONTRACT_ID_COLLISION_REVIEW"
            elif result["status"] != "PASS":
                status = "PARTITION_VALIDATION_FAILED"
            else:
                observed = result["observed"].get(symbol, [])
                status = classify_request(source_tuple_set, observed, True, "PASS")

            source_values = next(iter(source_tuple_set)) if len(source_tuple_set) == 1 else ()
            field_comparison = compare_high_low_volume(source_values, observed)
            observed_high = field_comparison["observed_high"] if field_comparison else None
            observed_low = field_comparison["observed_low"] if field_comparison else None
            observed_volume = field_comparison["observed_volume"] if field_comparison else None
            high_match = field_comparison["high_match"] if field_comparison else None
            low_match = field_comparison["low_match"] if field_comparison else None
            volume_match = field_comparison["volume_match"] if field_comparison else None
            meta = metadata.get(f"floorsheet/{day}.csv.gz", {})
            counts[status] += 1
            writer.writerow([
                symbol,
                day,
                status,
                f"floorsheet/{day}.csv.gz" if day in hf_dates else "",
                meta.get("oid", ""),
                (meta.get("lfs") or {}).get("oid", ""),
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

    collision_path = root / "hf_bulk_equity_contract_collisions.csv"
    with collision_path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "date", "contract", "symbol", "buyer", "seller",
            "quantity", "rate", "amount", "occurrences",
        ])
        for day in selected:
            result = results[day]
            for signature_row, occurrences in result.get("collision_rows", []):
                writer.writerow([*signature_row, occurrences])

    selected_requests = sum(len(bydate[day]) for day in selected)
    report = {
        "task": "P4.43 second-source HF bulk floorsheet recovery",
        "requests": len(keys),
        "unique_dates": len(bydate),
        "primary_archive_covered_dates": len(primary_dates),
        "hf_available_dates": len(hf_available),
        "hf_only_available_dates": len(hf_only_available),
        "hf_only_available_requests": sum(len(bydate[day]) for day in hf_only_available),
        "selected_dates": selected,
        "selected_requests": selected_requests,
        "offset": args.offset,
        "max_dates": args.max_dates,
        "status_counts": dict(counts),
        "session_validation": [results[day]["summary"] for day in selected],
        "promoted": 0,
        "promotion_allowed": False,
        "limitations": (
            "The HF dataset is a third-party archive. SHA/size checks pin downloaded bytes "
            "to the captured HF tree metadata but do not prove exchange origin, full-session "
            "completeness or independent upstream lineage. High/low/volume only are compared; "
            "open and close are not verified. Missing or unselected partitions are UNKNOWN, "
            "not evidence of no trade. No source or canonical data is changed."
        ),
    }
    (root / "hf_bulk_equity_floorsheet_summary.json").write_text(
        json.dumps(report, indent=2)
    )
    print(json.dumps({
        key: value for key, value in report.items()
        if key != "session_validation"
    }))
    if any(result["status"] == "FAIL" for result in results.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
