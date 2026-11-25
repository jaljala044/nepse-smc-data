"""Strict validators for evidence-backed NEPSE reference data.

This module validates claims and provenance; it does not infer trading sessions,
instrument identities, or listing lifecycles from weekdays or ticker strings.
"""
from __future__ import annotations

from datetime import date
import re
from typing import Iterable, Mapping

CALENDAR_STATUSES = {
    "verified_open",
    "verified_closed",
    "verified_exceptional_closed",
    "candidate_open",
    "candidate_closed",
    "unknown",
}
VERIFIED_STATUSES = {
    "verified_open",
    "verified_closed",
    "verified_exceptional_closed",
}
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _parse_date(value: str, field: str) -> date:
    try:
        parsed = date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field} must be a valid ISO date: {value!r}")
    if parsed.isoformat() != value:
        raise ValueError(f"{field} must use YYYY-MM-DD: {value!r}")
    return parsed


def validate_calendar_rows(rows: Iterable[Mapping[str, str]]) -> list[str]:
    """Return errors for duplicate, invalid, or unsupported calendar claims."""
    errors: list[str] = []
    seen: set[str] = set()
    for line, row in enumerate(rows, start=2):
        day = row.get("date", "")
        try:
            _parse_date(day, f"line {line} date")
        except ValueError as exc:
            errors.append(str(exc))
        if day in seen:
            errors.append(f"line {line}: duplicate calendar date {day}")
        seen.add(day)

        status = row.get("status", "")
        if status not in CALENDAR_STATUSES:
            errors.append(f"line {line}: invalid calendar status {status!r}")
            continue

        if status in VERIFIED_STATUSES:
            if not row.get("source_id", "").strip():
                errors.append(f"line {line}: verified status requires source_id")
            if not row.get("evidence_uri", "").strip():
                errors.append(f"line {line}: verified status requires evidence_uri")
            digest = row.get("raw_evidence_sha256", "").strip().lower()
            if not _SHA256.fullmatch(digest):
                errors.append(f"line {line}: verified status requires a 64-character SHA-256")
    return errors


def instrument_active_on(row: Mapping[str, str], on_date: str) -> bool:
    """Effective dates are inclusive; an empty valid_to means no known end."""
    target = _parse_date(on_date, "on_date")
    start_text = row.get("valid_from", "").strip()
    end_text = row.get("valid_to", "").strip()
    if not start_text:
        return False
    start = _parse_date(start_text, "valid_from")
    end = _parse_date(end_text, "valid_to") if end_text else None
    if end and end < start:
        raise ValueError("valid_to must not precede valid_from")
    return start <= target and (end is None or target <= end)


def validate_instrument_rows(
    rows: Iterable[Mapping[str, str]],
    dataset_symbols: Iterable[str] = (),
) -> list[str]:
    """Validate stable IDs, effective-date intervals, duplicates and coverage."""
    errors: list[str] = []
    materialized = list(rows)
    normalized_symbols: set[str] = set()
    for line, row in enumerate(materialized, start=2):
        symbol = row.get("symbol", "").strip().upper()
        security_id = row.get("security_id", "").strip()
        if not symbol:
            errors.append(f"line {line}: missing symbol")
            continue
        normalized_symbols.add(symbol)
        if not security_id:
            errors.append(f"line {line}: {symbol} missing stable security_id")
        start_text = row.get("valid_from", "").strip()
        end_text = row.get("valid_to", "").strip()
        if start_text:
            try:
                start = _parse_date(start_text, f"line {line} valid_from")
                end = _parse_date(end_text, f"line {line} valid_to") if end_text else None
                if end and end < start:
                    errors.append(f"line {line}: {symbol} valid_to precedes valid_from")
            except ValueError as exc:
                errors.append(str(exc))
        elif end_text:
            errors.append(f"line {line}: {symbol} has valid_to without valid_from")

    # Different security IDs must not claim the same symbol over overlapping
    # effective intervals. Adjacent inclusive intervals overlap on their shared day.
    for i, left in enumerate(materialized):
        ls = left.get("symbol", "").strip().upper()
        if not ls or not left.get("valid_from", "").strip():
            continue
        try:
            lstart = _parse_date(left["valid_from"], "valid_from")
            lend = _parse_date(left.get("valid_to", "").strip(), "valid_to") if left.get("valid_to", "").strip() else date.max
        except ValueError:
            continue
        for right in materialized[i + 1:]:
            if right.get("symbol", "").strip().upper() != ls or not right.get("valid_from", "").strip():
                continue
            try:
                rstart = _parse_date(right["valid_from"], "valid_from")
                rend = _parse_date(right.get("valid_to", "").strip(), "valid_to") if right.get("valid_to", "").strip() else date.max
            except ValueError:
                continue
            if max(lstart, rstart) <= min(lend, rend):
                if left.get("security_id", "").strip() != right.get("security_id", "").strip():
                    errors.append(f"overlapping symbol mapping for {ls}: different security IDs")
                    break

    for symbol in sorted({s.strip().upper() for s in dataset_symbols if s.strip()} - normalized_symbols):
        errors.append(f"unknown instrument symbol in dataset: {symbol}")
    return errors
