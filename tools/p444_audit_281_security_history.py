"""Read-only audit of the pinned 281-symbol NEPSE security-history capture."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import date
from pathlib import Path


REQUIRED_FIELDS = (
    "businessDate",
    "totalTrades",
    "totalTradedQuantity",
    "totalTradedValue",
    "highPrice",
    "lowPrice",
    "closePrice",
)
NUMERIC_FIELDS = REQUIRED_FIELDS[1:]


def _manifest_entries(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            raise ValueError(f"invalid manifest line {line_number}")
        digest, relative = parts
        relative = relative.lstrip("*").strip()
        if len(digest) != 64 or any(ch not in "0123456789abcdefABCDEF" for ch in digest):
            raise ValueError(f"invalid SHA-256 on manifest line {line_number}")
        if relative in entries:
            raise ValueError(f"duplicate manifest path: {relative}")
        entries[relative] = digest.lower()
    return entries


def audit(root: Path, manifest: Path, expected_symbols: int | None = 281) -> dict:
    root = Path(root)
    manifest = Path(manifest)
    entries = _manifest_entries(manifest)
    files = sorted(root.glob("*/response-01.bin"))
    issues: list[dict] = []
    symbol_reports: list[dict] = []
    seen_symbols: set[str] = set()
    total_rows = 0
    symbols_with_open = 0
    required_manifest_paths = set()

    for payload in files:
        symbol = payload.parent.name
        relative = f"symbols/{symbol}/response-01.bin"
        required_manifest_paths.add(relative)
        if symbol in seen_symbols:
            issues.append({"symbol": symbol, "code": "DUPLICATE_SYMBOL_FILE"})
            continue
        seen_symbols.add(symbol)

        expected_digest = entries.get(relative)
        if expected_digest is None:
            issues.append({"symbol": symbol, "code": "MANIFEST_ENTRY_MISSING"})
        raw = payload.read_bytes()
        actual_digest = hashlib.sha256(raw).hexdigest()
        if expected_digest and actual_digest != expected_digest:
            issues.append({"symbol": symbol, "code": "SHA256_MISMATCH"})

        try:
            document = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError):
            issues.append({"symbol": symbol, "code": "INVALID_JSON"})
            continue

        rows = document.get("content") if isinstance(document, dict) else None
        if not isinstance(rows, list):
            issues.append({"symbol": symbol, "code": "CONTENT_NOT_ARRAY"})
            continue

        dates: list[str] = []
        row_issues = 0
        has_open = False
        for index, row in enumerate(rows):
            current_row_issues = 0
            if not isinstance(row, dict):
                issues.append({"symbol": symbol, "row": index, "code": "ROW_NOT_OBJECT"})
                row_issues += 1
                continue
            missing = [key for key in REQUIRED_FIELDS if key not in row]
            if missing:
                issues.append({"symbol": symbol, "row": index, "code": "REQUIRED_FIELDS_MISSING", "fields": missing})
                row_issues += 1
                continue
            if "openPrice" in row:
                has_open = True
            raw_day = row["businessDate"]
            try:
                parsed_day = date.fromisoformat(raw_day)
                if parsed_day.isoformat() != raw_day:
                    raise ValueError
                dates.append(raw_day)
            except (TypeError, ValueError):
                issues.append({"symbol": symbol, "row": index, "code": "INVALID_BUSINESS_DATE"})
                current_row_issues += 1

            for key in NUMERIC_FIELDS:
                value = row[key]
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                    issues.append({"symbol": symbol, "row": index, "code": "NON_NUMERIC_FIELD", "field": key})
                    current_row_issues += 1
            if current_row_issues:
                row_issues += current_row_issues
                continue
            if row["totalTrades"] < 0 or int(row["totalTrades"]) != row["totalTrades"]:
                issues.append({"symbol": symbol, "row": index, "code": "INVALID_TOTAL_TRADES"})
                current_row_issues += 1
            if row["totalTradedQuantity"] < 0 or int(row["totalTradedQuantity"]) != row["totalTradedQuantity"]:
                issues.append({"symbol": symbol, "row": index, "code": "INVALID_TOTAL_QUANTITY"})
                current_row_issues += 1
            if row["totalTradedValue"] < 0 or row["highPrice"] < 0 or row["lowPrice"] < 0 or row["closePrice"] < 0:
                issues.append({"symbol": symbol, "row": index, "code": "NEGATIVE_MARKET_VALUE"})
                current_row_issues += 1
            if row["highPrice"] < row["lowPrice"] or not row["lowPrice"] <= row["closePrice"] <= row["highPrice"]:
                issues.append({"symbol": symbol, "row": index, "code": "PRICE_RANGE_INCONSISTENT"})
                current_row_issues += 1
            row_issues += current_row_issues

        if len(dates) != len(set(dates)):
            issues.append({"symbol": symbol, "code": "DUPLICATE_BUSINESS_DATE"})
        if dates != sorted(dates, reverse=True):
            issues.append({"symbol": symbol, "code": "DATES_NOT_DESCENDING"})
        total_rows += len(rows)
        symbols_with_open += int(has_open)
        symbol_reports.append({
            "symbol": symbol,
            "rows": len(rows),
            "date_min": min(dates) if dates else None,
            "date_max": max(dates) if dates else None,
            "open_price_present": has_open,
            "row_level_issues": row_issues,
            "sha256": actual_digest,
            "manifest_sha256_match": bool(expected_digest and actual_digest == expected_digest),
        })

    missing_files = sorted(required_manifest_paths - set(entries))
    unrepresented_manifest = sorted(
        path for path in entries if path.startswith("symbols/") and path.endswith("/response-01.bin")
        and path not in required_manifest_paths
    )
    if missing_files:
        issues.append({"code": "MANIFEST_PATHS_MISSING", "paths": missing_files})
    if unrepresented_manifest:
        issues.append({"code": "MANIFEST_PAYLOADS_NOT_FOUND", "paths": unrepresented_manifest})
    if expected_symbols is not None and len(seen_symbols) != expected_symbols:
        issues.append({"code": "SYMBOL_COUNT_MISMATCH", "expected": expected_symbols, "actual": len(seen_symbols)})

    return {
        "task": "P4.44 281-symbol security-history capture audit",
        "symbols": len(seen_symbols),
        "payload_files": len(files),
        "total_rows": total_rows,
        "date_min": min((x["date_min"] for x in symbol_reports if x["date_min"]), default=None),
        "date_max": max((x["date_max"] for x in symbol_reports if x["date_max"]), default=None),
        "symbols_with_open_price": symbols_with_open,
        "symbols_without_open_price": len(seen_symbols) - symbols_with_open,
        "manifest_symbol_payload_entries": sum(
            path.startswith("symbols/") and path.endswith("/response-01.bin") for path in entries
        ),
        "issues": issues,
        "valid": not issues,
        "promotion_allowed": False,
        "canonical_data_modified": False,
        "limitations": [
            "The capture is a point-in-time source payload inventory, not proof of historical security-ID continuity.",
            "No Open field is synthesized where absent.",
            "Missing dates are not classified as non-trading days without an authoritative session calendar.",
            "Payload validity and manifest integrity do not prove exchange completeness or independent source authenticity.",
        ],
        "symbol_reports": symbol_reports,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path, help="symbols directory")
    parser.add_argument("--manifest", required=True, type=Path, help="SHA256SUMS manifest")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--expected-symbols", type=int, default=281)
    args = parser.parse_args()
    result = audit(args.root, args.manifest, args.expected_symbols)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in (
        "symbols", "payload_files", "total_rows", "date_min", "date_max",
        "symbols_with_open_price", "symbols_without_open_price", "valid", "issues",
    )}, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
