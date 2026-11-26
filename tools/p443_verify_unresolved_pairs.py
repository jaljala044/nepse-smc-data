"""Cross-check unresolved repeated OHLCV pairs against pinned official security EOD captures.

Read-only: official HLCV/execution fields cannot validate opening price or replace a source row.
"""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

try:
    from tools.p443_classify_repeated_candles import source_rows
    from tools.p443_verify_open_pairs import compare, load_evidence
except ModuleNotFoundError:
    from p443_classify_repeated_candles import source_rows
    from p443_verify_open_pairs import compare, load_evidence

TARGET_CLASSES = {"BOTH_OPEN_TUPLE_UNVERIFIED", "INSUFFICIENT_SESSION_EVIDENCE"}


def classify_pair(current_result, previous_result):
    results = (current_result, previous_result)
    if "CONFLICTING_OFFICIAL_EVIDENCE" in results:
        return "CONFLICTING_OFFICIAL_EVIDENCE_REVIEW"
    if "HLCV_MISMATCH" in results:
        return "HLCV_MISMATCH_REVIEW"
    matched = results.count("HLCV_MATCH_OPEN_UNVERIFIED")
    if matched == 2:
        return "BOTH_DATES_HLCV_EXECUTION_MATCH_OPEN_UNVERIFIED"
    if matched == 1:
        return "ONE_DATE_HLCV_EXECUTION_MATCH_OTHER_UNVERIFIED"
    if results == ("NO_SECURITY_DATE_EVIDENCE", "NO_SECURITY_DATE_EVIDENCE"):
        return "NO_SECURITY_DATE_EVIDENCE_BOTH_DATES"
    return "NO_COMPLETE_TWO_DATE_MATCH"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", required=True)
    root = Path(parser.parse_args().directory)
    evidence = load_evidence()
    counts = Counter()
    evidence_coverage = Counter()
    symbols = set()
    expected = 58972
    with (root / "repeat_evidence_review.csv").open(newline="") as src, (root / "unresolved_pair_security_evidence.csv").open("w", newline="") as dst:
        reader = csv.DictReader(src)
        fields = reader.fieldnames + [
            "current_result", "previous_result", "pair_evidence_result",
            "current_evidence", "previous_evidence", "promotion_allowed"
        ]
        writer = csv.DictWriter(dst, fieldnames=fields)
        writer.writeheader()
        for row in reader:
            if row["pair_classification"] not in TARGET_CLASSES:
                continue
            symbol = row["symbol"]
            symbols.add(symbol)
            source = source_rows(row["path"], row["blob_sha"])
            current_date, current_values = source[row["row"]]
            previous_date, previous_values = source[row["previous_row"]]
            if current_date != row["date"] or previous_date != row["previous_date"] or current_values != previous_values:
                raise ValueError("repeat source lineage mismatch")
            current_records = evidence[(symbol, current_date)]
            previous_records = evidence[(symbol, previous_date)]
            current_result = compare(current_values, current_records)
            previous_result = compare(previous_values, previous_records)
            pair_result = classify_pair(current_result, previous_result)
            counts[(row["pair_classification"], pair_result)] += 1
            evidence_coverage["current_date_present" if current_records else "current_date_missing"] += 1
            evidence_coverage["previous_date_present" if previous_records else "previous_date_missing"] += 1
            writer.writerow({
                **row,
                "current_result": current_result,
                "previous_result": previous_result,
                "pair_evidence_result": pair_result,
                "current_evidence": ";".join(path + ":" + sha for path, sha, _ in current_records),
                "previous_evidence": ";".join(path + ":" + sha for path, sha, _ in previous_records),
                "promotion_allowed": "false",
            })
    total = sum(counts.values())
    if total != expected:
        raise ValueError(f"expected {expected} unresolved pairs, found {total}")
    summary = {
        "pairs": total,
        "symbols": len(symbols),
        "results": [
            {"calendar_pair_class": calendar_class, "official_evidence_result": result, "pairs": n}
            for (calendar_class, result), n in sorted(counts.items())
        ],
        "evidence_record_presence": dict(evidence_coverage),
        "promoted": 0,
        "limitations": "Pinned official history may provide HLCV and execution counts but not opening price. A match does not validate the full OHLCV tuple; missing capture is not proof of no trade. No floorsheet validation or canonical correction.",
    }
    (root / "unresolved_pair_security_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
