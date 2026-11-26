"""Compare complete contract multisets across the bounded P4.43 floorsheet batch."""
import csv
import gzip
import hashlib
import io
import json
from collections import Counter
from decimal import Decimal, ROUND_FLOOR
from pathlib import Path

try:
    from tools.capture_p433_first_trade_floorsheets import fetch, BASE, pick
    from tools.validate_historical_floorsheets import download_one
except ModuleNotFoundError:
    from capture_p433_first_trade_floorsheets import fetch, BASE, pick
    from validate_historical_floorsheets import download_one

BATCH_SUMMARY = Path("reference/P443_BULK_EQUITY_FLOORSHEET_BATCH01_2026-11-27.json")
PRIMARY_INVENTORY = Path("reference/p419_observed_date_floorsheet_archive_inventory_2026-11-26.csv")
HF_TREE = Path("reference/p433_floorsheets/huggingface_repo_tree.json")


def signature(row, secondary, day, stats=None):
    get = lambda key: pick(row, key) if secondary else row[
        key if key != "contract_no" else "transaction"
    ]
    raw_contract = get("contract_no").strip()
    contract = raw_contract
    # Some CSV exports prefix numeric IDs with one apostrophe. Preserve that
    # fact in per-source counters, but compare the underlying digits only.
    if raw_contract.startswith("'") and raw_contract[1:].isdigit():
        contract = raw_contract[1:]
        if stats is not None:
            stats["leading_apostrophe_contract_ids"] += 1
    date = get("date")[:10]
    symbol = get("symbol").strip().upper()
    buyer, seller = (row[key].strip() for key in ("buyer", "seller"))
    quantity, rate, amount = (
        Decimal(get(key).replace(",", "")) for key in ("quantity", "rate", "amount")
    )
    amount_exact_match = abs(quantity * rate - amount) <= Decimal("0.01")
    amount_floor_match = (
        amount == amount.to_integral_value()
        and amount == (quantity * rate).to_integral_value(rounding=ROUND_FLOOR)
    )
    if (
        not contract.isdigit()
        or date != day
        or not symbol
        or not buyer.isdigit()
        or not seller.isdigit()
        or not all(value.is_finite() for value in (quantity, rate, amount))
        or quantity <= 0
        or quantity != quantity.to_integral_value()
        or rate <= 0
        or amount <= 0
        or not (amount_exact_match or amount_floor_match)
    ):
        raise ValueError("invalid contract " + raw_contract)
    if stats is not None:
        if amount_exact_match:
            stats["amount_exact_match"] += 1
        elif amount_floor_match:
            stats["amount_floor_truncated"] += 1
    return (date, contract, symbol, buyer, seller, quantity, rate, amount)


def parse(reader, secondary, day, stats=None):
    counts = Counter()
    contract_ids = Counter()
    for row in reader:
        key = signature(row, secondary, day, stats)
        counts[key] += 1
        contract_ids[key[1]] += 1
    if not counts or any(count != 1 for count in contract_ids.values()):
        raise ValueError("empty file or duplicate contract")
    return counts


def has_collection_failures(results):
    """A row conflict is an audit finding; only unavailable/invalid capture fails collection."""
    return any(row.get("status") == "UNAVAILABLE_OR_INVALID" for row in results)


def load_targets():
    batch = json.loads(BATCH_SUMMARY.read_text(encoding="utf-8"))
    dates = batch.get("selected_dates", [])
    if len(dates) != 22 or len(set(dates)) != 22:
        raise ValueError("bulk batch must contain 22 unique selected dates")
    return set(dates), batch


def main():
    output = Path("full-session-parity")
    output.mkdir(exist_ok=True)
    raw = output / "raw"
    raw.mkdir(exist_ok=True)

    target_dates, batch = load_targets()
    with PRIMARY_INVENTORY.open(newline="") as handle:
        inventory_rows = [
            row for row in csv.DictReader(handle)
            if row["date"] in target_dates
            and row["inventory_status"] == "FILE_PRESENT_IN_PINNED_GIT_TREE"
        ]
    if len(inventory_rows) != len(target_dates):
        raise ValueError("primary archive inventory does not cover the selected batch dates")

    tree = json.loads(HF_TREE.read_text(encoding="utf-8"))
    metadata = {entry["path"]: entry for entry in tree.get("files", [])}
    missing_secondary = [
        f"floorsheet/{day}.csv.gz"
        for day in sorted(target_dates)
        if f"floorsheet/{day}.csv.gz" not in metadata
    ]
    if missing_secondary:
        raise ValueError("secondary archive missing selected dates: " + ",".join(missing_secondary))

    results = []
    for item in sorted(inventory_rows, key=lambda row: row["date"]):
        day = item["date"]
        result = {
            "date": day,
            "promotion_allowed": False,
            "primary_git_blob": item["git_blob_sha"],
            "secondary_source_path": f"floorsheet/{day}.csv.gz",
        }
        try:
            primary = download_one(item, raw)
            if primary["download_status"] != "PASS":
                raise ValueError("primary download failed")

            secondary_path = f"floorsheet/{day}.csv.gz"
            secondary_meta = metadata[secondary_path]
            status, _, compressed = fetch(BASE + secondary_path)
            secondary_sha256 = hashlib.sha256(compressed).hexdigest()
            expected_lfs = (secondary_meta.get("lfs") or {}).get("oid")
            if (
                status != 200
                or not expected_lfs
                or secondary_sha256 != expected_lfs
                or len(compressed) != secondary_meta["size"]
            ):
                raise ValueError("secondary hash or size mismatch")

            primary_stats = Counter()
            secondary_stats = Counter()
            with open(primary["path"], newline="", encoding="utf-8-sig") as handle:
                primary_contracts = parse(csv.DictReader(handle), False, day, primary_stats)
            secondary_contracts = parse(
                csv.DictReader(io.StringIO(gzip.decompress(compressed).decode("utf-8-sig"))),
                True,
                day,
                secondary_stats,
            )

            primary_only = primary_contracts - secondary_contracts
            secondary_only = secondary_contracts - primary_contracts
            result.update(
                primary_rows=primary_contracts.total(),
                secondary_rows=secondary_contracts.total(),
                matched_rows=(primary_contracts & secondary_contracts).total(),
                primary_only=primary_only.total(),
                secondary_only=secondary_only.total(),
                primary_sha256=primary["actual_sha256"],
                secondary_git_blob=secondary_meta.get("oid"),
                secondary_sha256=secondary_sha256,
                secondary_bytes=len(compressed),
                primary_leading_apostrophe_contract_ids=primary_stats["leading_apostrophe_contract_ids"],
                secondary_leading_apostrophe_contract_ids=secondary_stats["leading_apostrophe_contract_ids"],
                primary_amount_exact_rows=primary_stats["amount_exact_match"],
                primary_amount_floor_rows=primary_stats["amount_floor_truncated"],
                secondary_amount_exact_rows=secondary_stats["amount_exact_match"],
                secondary_amount_floor_rows=secondary_stats["amount_floor_truncated"],
                status="EXACT_PARITY" if primary_contracts == secondary_contracts else "ROW_CONFLICT",
            )

            with (output / f"differences_{day}.csv").open("w", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow([
                    "source", "date", "contract", "symbol", "buyer", "seller",
                    "quantity", "rate", "amount", "count",
                ])
                for side, differences in (("primary", primary_only), ("secondary", secondary_only)):
                    for key, count in sorted(differences.items()):
                        writer.writerow([side, *key, count])

        except Exception as error:
            result.update(status="UNAVAILABLE_OR_INVALID", error=str(error))
        results.append(result)

    review_rows = [row for row in results if row["status"] == "ROW_CONFLICT"]
    report = {
        "task": "P4.43 full-session contract parity for bulk batch 01",
        "selected_dates": sorted(target_dates),
        "primary_input_commit": "56362fb4f65b91fdcca8f50b50e53ad80e703649",
        "primary_archive_commit": "70324524df83eaa7c2964441ad4026d6ab00cc7e",
        "secondary_tree_retrieved_at": tree.get("retrieved_at_utc"),
        "secondary_tree_file_count": tree.get("file_count"),
        "results": results,
        "counts": dict(Counter(row["status"] for row in results)),
        "exact_parity_rows": sum(
            row.get("matched_rows", 0) for row in results if row["status"] == "EXACT_PARITY"
        ),
        "matched_rows_including_conflict_sessions": sum(
            row.get("matched_rows", 0) for row in results
        ),
        "primary_only_rows": sum(row.get("primary_only", 0) for row in results),
        "secondary_only_rows": sum(row.get("secondary_only", 0) for row in results),
        "review_required_dates": [row["date"] for row in review_rows],
        "review_required_secondary_only_rows": sum(
            row.get("secondary_only", 0) for row in review_rows
        ),
        "limitations": (
            "Parity covers date, contract number, symbol, buyer/seller broker IDs, quantity, "
            "rate and amount only. A ROW_CONFLICT is a review finding, not a collection failure. "
            "No timestamp parity, independent upstream provenance, official completeness or "
            "canonical promotion is established."
        ),
        "promotion_allowed": False,
    }
    (output / "full_session_parity.json").write_text(json.dumps(report, indent=2))
    print(json.dumps({
        "dates": len(target_dates),
        "counts": report["counts"],
        "exact_parity_rows": report["exact_parity_rows"],
        "review_required_dates": report["review_required_dates"],
        "secondary_only_rows": report["secondary_only_rows"],
        "promotion_allowed": False,
    }))
    if len(results) != len(target_dates) or has_collection_failures(results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
