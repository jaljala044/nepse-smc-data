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


def _effective_interval(row: Mapping[str, str], line: int) -> tuple[date, date] | None:
    start_text = row.get("valid_from", "").strip()
    end_text = row.get("valid_to", "").strip()
    if not start_text:
        return None
    start = _parse_date(start_text, f"line {line} valid_from")
    end = _parse_date(end_text, f"line {line} valid_to") if end_text else date.max
    if end < start:
        raise ValueError(f"line {line}: valid_to precedes valid_from")
    return start, end


def validate_instrument_rows(
    rows: Iterable[Mapping[str, str]],
    dataset_symbols: Iterable[str] = (),
) -> list[str]:
    """Validate stable IDs, symbol/date intervals, duplicates and dataset coverage.

    Reusing one stable security ID for a later, non-overlapping symbol rename is
    permitted. Overlapping records for one ID, or one symbol assigned to different
    IDs during an overlapping interval, are rejected.
    """
    errors: list[str] = []
    materialized = list(rows)
    normalized_symbols: set[str] = set()
    normalized: list[tuple[int, str, str, tuple[date, date] | None]] = []

    for line, row in enumerate(materialized, start=2):
        symbol = row.get("symbol", "").strip().upper()
        security_id = row.get("security_id", "").strip()
        if not symbol:
            errors.append(f"line {line}: missing symbol")
            continue
        normalized_symbols.add(symbol)
        if not security_id:
            errors.append(f"line {line}: {symbol} missing stable security_id")
        elif not re.fullmatch(r"[0-9]+", security_id) or not any(ch != "0" for ch in security_id):
            errors.append(f"line {line}: {symbol} security_id must be a positive integer")
        try:
            interval = _effective_interval(row, line)
            if interval is None:
                errors.append(f"line {line}: {symbol} missing valid_from")
        except ValueError as exc:
            errors.append(str(exc))
            interval = None
        normalized.append((line, symbol, security_id, interval))

    for index, left in enumerate(normalized):
        lline, lsymbol, lid, lint = left
        if not lid or lint is None:
            continue
        for rline, rsymbol, rid, rint in normalized[index + 1:]:
            if not rid or rint is None:
                continue
            overlaps = max(lint[0], rint[0]) <= min(lint[1], rint[1])
            if not overlaps:
                continue
            if lid == rid:
                errors.append(
                    f"overlapping stable security_id {lid}: rows {lline} and {rline} "
                    f"claim {lsymbol} and {rsymbol}"
                )
            elif lsymbol == rsymbol:
                errors.append(
                    f"overlapping symbol mapping for {lsymbol}: different security IDs"
                )

    for symbol in sorted({s.strip().upper() for s in dataset_symbols if s.strip()} - normalized_symbols):
        errors.append(f"unknown instrument symbol in dataset: {symbol}")
    return errors
