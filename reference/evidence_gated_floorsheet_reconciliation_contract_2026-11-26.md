# Evidence-gated floorsheet reconciliation contract — 2026-11-26

## Purpose

The daily reconciler produces one record per archived equity symbol and floorsheet date. It separates the fact that a contract was observed from the separate question of whether the OHLCV bar reconciles. It must not infer NO_TRADE from a missing symbol in a partial extract.

## Status semantics

- `TRADED`: at least one valid, unique, date-matched contract for the symbol exists in a valid floorsheet file. This is positive contract evidence even if OHLCV is absent or mismatched.
- `NO_TRADE`: zero symbol contracts, verified-open session, valid file, HTTPS source URI, matching SHA-256, explicit completeness evidence, and independently recorded market totals matching the file (trade count, shares, turnover and distinct traded symbols). A positive or malformed OHLCV volume observation blocks this status.
- `UNKNOWN`: every other case, including missing/partial files, invalid contracts, unverified session, failed hash, missing totals, totals mismatch or conflicting positive OHLCV volume.

The separate `ohlcv_reconciliation` field is `MATCH`, `CONFLICT` or `NOT_COMPARABLE`. A positive contract remains TRADED when OHLCV volume conflicts; the conflict is not hidden by the trade status.

## Required manifest columns

One row per date in the manifest CSV:

| Field | Requirement |
|---|---|
| `trading_date` | Exact local exchange date, YYYY-MM-DD |
| `floorsheet_complete` | Literal true only after full-day completeness checks |
| `completeness_evidence` | Specific evidence such as pagination exhausted and source total reconciliation |
| `source_uri` | HTTPS source reference |
| `source_sha256` | SHA-256 of the exact raw floorsheet file |
| `expected_trades` | Independently recorded market-wide contract count |
| `expected_shares` | Independently recorded market-wide share total |
| `expected_turnover_npr` | Independently recorded market-wide turnover |
| `expected_symbols` | Independently recorded distinct traded-symbol count |

A free-text completeness claim alone is not sufficient. The raw file hash must match, and all four aggregate totals must match the parsed file. The source evidence itself still requires human/source-quality review; HTTPS does not prove that a source is official or complete.

## Data handling

- Raw floorsheet and OHLCV files are read-only inputs.
- No rows are filled, deleted, forward-filled or silently adjusted.
- Missing OHLCV bar with positive contracts is retained as TRADED and marked NOT_COMPARABLE.
- Positive OHLCV volume with zero floorsheet contracts is UNKNOWN, not NO_TRADE.
- A date classified closed but containing valid contracts remains a positive trade observation and creates a calendar reconciliation conflict for separate review.
- The engine outputs evidence fields, observed totals and source hashes to support audit.

## Regression coverage

Tests cover positive trades in partial files, duplicate contract IDs, absence in incomplete files, strict no-trade gates, missing OHLCV bars, closed sessions, positive OHLCV contradiction, market-total mismatch and traded-volume conflict.

## Current release status

The code and tests are committed, but CI status has not yet been observed for the latest commits. The available 2026-11-19/20 500-row samples are not established as full-day extracts and therefore cannot produce NO_TRADE results. No canonical data promotion or model training is authorized by this implementation alone.
