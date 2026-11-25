# NEPSE reference-data validation stage — 2026-11-26

## Added code
- `nepse_reference_validation.py`
- `test_nepse_reference_validation.py`

The validator enforces evidence-first calendar status, date uniqueness, explicit provenance for verified statuses, instrument symbol coverage, stable security IDs, non-overlapping effective-dated symbol mappings, and inclusive validity boundaries.

## Test status
Unit tests were authored for the above conditions. They were not executed in this session; no passing CI claim is made.

## Evidence status
The repository contains 525 OHLCV symbol files and a 2026 NEPSE holiday API closure-only snapshot. It does not currently contain multi-year raw holiday captures or a complete dated official instrument master. No missing open-session dates or instrument lifecycle fields have been guessed.

Official discovery references:
- NEPSE stock list: https://www.nepalstock.com.np/stocklist
- NEPSE homepage / corporate information: https://www.nepalstock.com.np/
- Existing 2026 official holiday API endpoint: https://nepalstock.com.np/api/nots/holiday/list?year=2026

## Next
Capture authenticated raw holiday API responses for every historical year represented in OHLCV data, plus the official listed-securities/instrument response. Preserve raw bytes, SHA-256, retrieval timestamp, and parser version; then run the validators and report exceptions.

This stage adds validation safeguards, not a completed historical calendar or canonical instrument master.
