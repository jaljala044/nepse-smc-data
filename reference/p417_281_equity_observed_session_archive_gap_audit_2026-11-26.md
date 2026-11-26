# P4.17 — 281-equity observed-session OHLCV archive-gap audit

**Purpose:** Measure whether the existing OHLCV archive contains rows on dates for which there is positive market-open evidence. This is an archive completeness diagnostic, not a per-security expected-session calendar.

## Inputs

- 281 unique equity symbols from `reference/p410_stage1_coverage_matrix_2026-11-26.csv`.
- Canonical date rows whose status is exactly `verified_open_observed`.
- OHLCV files from the pinned `jaljala044/nepse-history-starter` checkout.

The observed-date list currently combines:
- positive NEPSE official price/volume observations for security ID 8108 (225 dates, scoped to that instrument);
- the independently cross-checked full-session third-party capture for 2026-11-20 (marketwide capture, raw bronze pages not archived).

The date count and provenance are printed by the job and retained in its workflow logs. This combined sample is not represented as an authoritative complete exchange calendar.

## Output fields

One row per equity:
- file presence;
- count of observed dates;
- OHLCV dates present within that observed-date sample;
- missing archive-date count;
- duplicate date rows and invalid date rows;
- positive-volume date count;
- earliest/latest date present in the sample;
- `ARCHIVE_GAP_REVIEW_REQUIRED` or `OBSERVATIONS_COMPLETE_FOR_SAMPLE_ONLY`.

## Critical interpretation rules

- A missing OHLCV row is only an **archive gap**. It is not `NO_TRADE`.
- An OHLCV zero-volume row is not enough to establish `NO_TRADE`.
- Positive observed activity in security ID 8108 proves the market traded on a date, not that every other equity was eligible or expected to trade.
- Unknown first-trade/listing boundaries are not inferred from this report.
- No symbol is admitted to Stage 1 by this audit. Existing corporate-action, price-basis, row provenance, floorsheet and liquidity gates remain unchanged.

## CI

The dedicated job emits a CSV artifact for the full 281-equity universe. Tests verify:
1. missing rows remain archive gaps, never `NO_TRADE`;
2. duplicate dates are counted;
3. missing files are explicit gaps;
4. candidate weekdays and closed dates are excluded from the positive-observation set;
5. the universe count is guarded.

This is a bounded evidence inventory step to prioritize raw OHLCV recovery and source reconciliation.
