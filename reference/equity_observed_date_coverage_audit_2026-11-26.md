# Equity Observed-Date Coverage Audit — 2026-11-26

## Scope

Task 4 of the five-task equity OHLCV validation queue. Audited all 281 provisional common-equity OHLCV files in `jaljala044/nepse-history-starter/03_stock_charts_ohlcv` against the 225 positive-trade dates in the canonical calendar for sampled security ID 8108.

This is an **observed-date overlap audit**, not a final per-symbol expected-session completeness score. The universe is still provisional and lifecycle/suspension dates are not fully verified. A symbol can legitimately have no row on a date when the sampled reference security traded.

## Deliverables

- Per-symbol CSV: `reference/equity_observed_date_coverage_2026-11-26.csv`
- Canonical comparison calendar: `reference/nepse_canonical_session_calendar_2025-2026.csv`
- Candidate universe source: `reference/nepse_target_universe_candidates_2026-11-26.csv`

## Coverage results

| Metric | Result |
|---|---:|
| Provisional common-equity symbols | 281 |
| OHLCV files found in history repository | 281 |
| Missing OHLCV files | 0 |
| Unique coverage rows | 281 |
| Reference positive-trade dates | 225 |
| Mean observed-date overlap | 94.38% |
| Median observed-date overlap | 99.11% |
| Minimum observed-date overlap | 3.11% |
| Maximum observed-date overlap | 99.11% |
| Symbols below 90% overlap | 26 |
| Symbols below 50% overlap | 13 |
| Duplicate dates within each symbol's sample-window rows | 0 |

The per-symbol CSV stores each file's blob SHA, total row count, first/last dates, rows in the sample window, matching observed dates, dates without a row, overlap percentage, and duplicate-date count.

## Symbols flagged below 90% observed-date overlap

| Symbol | Match % | First archive date | Last archive date |
|---|---:|---|---|
| NLO | 3.11% | 2024-03-26 | 2026-09-30 |
| BENH | 7.11% | 2026-10-15 | 2026-11-20 |
| SAPIL | 24.89% | 2026-08-13 | 2026-11-20 |
| MEPDL | 25.33% | 2026-08-12 | 2026-11-20 |
| ECL | 32.89% | 2026-07-17 | 2026-11-20 |
| KAHL | 37.78% | 2026-07-02 | 2026-11-20 |
| SGHL | 37.78% | 2026-07-02 | 2026-11-20 |
| SNORL | 39.56% | 2026-06-26 | 2026-11-20 |
| TPKHL | 41.33% | 2026-06-22 | 2026-11-20 |
| YMHL | 41.33% | 2026-06-22 | 2026-11-20 |
| APHL | 44.89% | 2026-06-10 | 2026-11-20 |
| SOPL | 45.78% | 2026-06-08 | 2026-11-20 |
| KHPL | 48.89% | 2026-05-26 | 2026-11-20 |
| BNL | 50.67% | 2024-03-04 | 2026-11-19 |
| PCIL | 62.22% | 2026-04-10 | 2026-11-20 |
| SIPD | 62.22% | 2026-04-10 | 2026-11-20 |
| SKHEL | 66.22% | 2026-03-29 | 2026-11-20 |
| RLEL | 66.67% | 2026-03-29 | 2026-11-20 |
| SKHL | 67.56% | 2026-03-25 | 2026-11-20 |
| BJHL | 68.89% | 2026-03-22 | 2026-11-20 |
| SOHL | 70.67% | 2026-03-15 | 2026-11-20 |
| HFIN | 71.11% | 2026-03-12 | 2026-11-20 |
| SABBL | 75.56% | 2026-02-16 | 2026-11-20 |
| RSML | 76.00% | 2026-02-16 | 2026-11-20 |
| PFL | 78.67% | 2024-03-04 | 2026-11-20 |
| UNL | 80.89% | 2024-03-05 | 2026-11-20 |

## Interpretation

- The 12 lowest-overlap symbols other than NLO have archive start dates from February through October 2026. Their low overlap may reflect later listing/trading start, not missing historical sessions. Lifecycle dates must be checked before classifying them as data gaps.
- NLO is a separate high-priority review case: its file begins in March 2024 but ends on 2026-09-30, substantially earlier than the other archive files. Verify whether this reflects a trading suspension, listing/lifecycle change, or incomplete data capture.
- BNL and PFL also warrant symbol-specific review because their overlap is materially below the main cluster despite older archive start dates.
- The common 225-date reference belongs to security ID 8108. It is not a full exchange session calendar and does not establish that all 281 equities should have traded on every reference date.
- No duplicate dates were found within the audited sample-window rows. This does not replace the full OHLCV value/row-quality audit planned in Task 5.

## Task 4 outcome

**Completed as a bounded observed-date overlap audit; final expected-session completeness remains pending.**

Do not label the 26 flagged symbols as defective solely from this proxy. Next, validate symbol lifecycle/suspension dates and extend the row-level quality checks across both repositories. Preserve raw OHLCV.

## Links

- [Per-symbol coverage CSV](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/equity_observed_date_coverage_2026-11-26.csv)
- [Canonical session calendar](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_canonical_session_calendar_2025-2026.csv)
- [Candidate equity inventory](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_target_universe_candidates_2026-11-26.csv)
