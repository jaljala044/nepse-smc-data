# P4.21 — 281-equity OHLCV row-quality inventory

This is a read-only first-pass structural audit of the 281-symbol candidate universe. It records file SHA-256, row counts, date bounds, duplicate/invalid dates, numeric parse failures, basic OHLC invariants, zero/negative volume, row ordering and exact adjacent OHLCV carry-forwards.

## Interpretation and safety
- A flag is a review candidate, not proof of bad data or manipulation.
- Zero-volume rows are counted, not deleted.
- Missing files and missing rows are not NO_TRADE.
- Carry-forward rows are not automatically removed or classified as fabricated; calendar/session and source corroboration are separate.
- A clean result means only that these basic structural checks found no flags. It does not establish source provenance, finality, adjusted/unadjusted price basis, corporate-action clearance, session completeness, liquidity or Stage 1 eligibility.
- Raw source files are never modified.

## Output
The workflow uploads one CSV row per equity with file hash and anomaly counters. Any BUY eligibility remains governed by the separate Stage 1 hard gates.
