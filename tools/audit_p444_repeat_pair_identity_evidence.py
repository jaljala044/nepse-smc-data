#!/usr/bin/env python3
"""Build a fail-closed, exact-ID evidence matrix for repeated OHLCV pairs.

This tool never changes canonical OHLCV. It only admits an exact symbol/date
join when identity and execution evidence are rights-cleared, hash-backed,
and uniquely effective on that date. Every other row remains HOLD.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

REQUIRED_IDENTITY = {
    "security_id", "symbol", "instrument_type", "effective_from", "effective_to",
    "source_url", "retrieved_at", "raw_sha256", "authorization_status", "evidence_tier",
}
REQUIRED_EXECUTION = {
    "security_id", "business_date", "traded_quantity", "source_url",
    "retrieved_at", "raw_sha256", "authorization_status", "evidence_tier",
}
REQUIRED_PAIR = {"pair_id", "symbol", "business_date", "source_path", "source_blob_sha", "source_row"}


def read_csv(path: str | Path, required: set[str]) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        missing = sorted(required - fields)
        if missing:
            raise ValueError(f"{path}: missing required columns: {', '.join(missing)}")
        return list(reader)


def valid_hash(value: str) -> bool:
    value = (value or "").strip().lower()
    return len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat((value or "").strip()[:10])
    except (TypeError, ValueError):
        return None


def evidence_eligible(row: dict[str, str]) -> bool:
    return (
        (row.get("authorization_status") or "").strip().lower() in {"authorized", "rights_cleared"}
        and (row.get("evidence_tier") or "").strip().lower() in {"primary", "approved"}
        and bool((row.get("source_url") or "").strip())
        and bool((row.get("retrieved_at") or "").strip())
        and valid_hash(row.get("raw_sha256", ""))
    )


def build_matrix(pairs: list[dict[str, str]], identities: list[dict[str, str]],
                 executions: list[dict[str, str]]) -> list[dict[str, str]]:
    identities_by_symbol: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in identities:
        identities_by_symbol[(row.get("symbol") or "").strip().upper()].append(row)

    executions_by_id_date: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in executions:
        key = ((row.get("security_id") or "").strip(), (row.get("business_date") or "").strip()[:10])
        executions_by_id_date[key].append(row)

    output = []
    for pair in pairs:
        symbol = (pair.get("symbol") or "").strip().upper()
        day = parse_date(pair.get("business_date", ""))
        candidates = identities_by_symbol.get(symbol, [])
        eligible_identity = []
        for identity in candidates:
            start = parse_date(identity.get("effective_from", ""))
            end_text = (identity.get("effective_to") or "").strip()
            end = parse_date(end_text) if end_text else None
            if (day and start and start <= day and (end is None or day <= end)
                    and evidence_eligible(identity)
                    and (identity.get("security_id") or "").strip()):
                eligible_identity.append(identity)

        status, reason, security_id = "HOLD", "identity_not_uniquely_proven", ""
        execution_sha = ""
        if len(eligible_identity) == 1:
            identity = eligible_identity[0]
            security_id = identity["security_id"].strip()
            exec_rows = executions_by_id_date.get((security_id, day.isoformat() if day else ""), [])
            eligible_exec = [
                row for row in exec_rows
                if evidence_eligible(row)
                and (parse_date(row.get("business_date", "")) == day)
                and row.get("traded_quantity", "").strip() not in {"", "0", "0.0"}
            ]
            if len(eligible_exec) == 1:
                status, reason = "IDENTITY_AND_EXECUTION_EVIDENCE_MATCHED", "exact_security_id_and_date"
                execution_sha = eligible_exec[0]["raw_sha256"].strip().lower()
            elif len(eligible_exec) > 1:
                reason = "multiple_execution_evidence_rows"
            else:
                reason = "no_rights_cleared_execution_on_exact_date"
        elif len(eligible_identity) > 1:
            reason = "multiple_effective_identity_rows"

        output.append({
            **pair,
            "resolved_security_id": security_id,
            "disposition": status,
            "reason": reason,
            "execution_raw_sha256": execution_sha,
            "canonical_promotion_allowed": "false",
        })
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeat-pairs", required=True)
    parser.add_argument("--security-master", required=True)
    parser.add_argument("--executions", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    pairs = read_csv(args.repeat_pairs, REQUIRED_PAIR)
    identities = read_csv(args.security_master, REQUIRED_IDENTITY)
    executions = read_csv(args.executions, REQUIRED_EXECUTION)
    result = build_matrix(pairs, identities, executions)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(result[0]) if result else sorted(REQUIRED_PAIR | {
        "resolved_security_id", "disposition", "reason", "execution_raw_sha256",
        "canonical_promotion_allowed",
    })
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(result)
    summary = {
        "rows": len(result),
        "matched": sum(r["disposition"] == "IDENTITY_AND_EXECUTION_EVIDENCE_MATCHED" for r in result),
        "held": sum(r["disposition"] == "HOLD" for r in result),
        "canonical_promotion_allowed": False,
        "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
    }
    output.with_suffix(output.suffix + ".summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
