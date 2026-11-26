# Equity Low-Overlap Triage Register — 2026-11-26

## Purpose and method

This register triages the 26 provisional common-equity symbols below 90% observed-date overlap in the 2026-11-26 audit. The comparison denominator is 225 positive-trade dates for sampled security ID 8108; it is a screening proxy, not a universal expected-session calendar. Absence of a symbol row can mean no execution, later listing/trading start, suspension, lifecycle event, or source omission.

## Triage summary

| Triage group | Count | Interpretation | Current disposition |
|---|---:|---|---|
| Symbol-specific reviewed | 4 | NLO, BNL, PFL, BENH | Evidence reports linked below; classifications updated |
| Later-start candidates lifecycle-checked (9 aligned; 2 boundary exceptions) | 11 | Dated notices and archive first-volume rows checked for all 11; APHL and KHPL have one-session discrepancies | Verify first listing / first-trade date before treating earlier absent rows as gaps |
| Mid-2026 start / low overlap unresolved | 11 | Files start before the sample window but have materially fewer matching observations | Requires trade-level / floorsheet / lifecycle review; do not assume data defect |

## Symbol-specific reviewed

| Symbol | Overlap | Classification |
|---|---:|---|
| NLO | 3.11% | Active, exceptionally sparse trading / no recent execution. Last project trade 2026-09-30; multiple providers report no trades later. Not proven collector staleness. Bonus quantity/ratio conflict remains open. |
| BNL | 50.67% | Active, very illiquid. Project archive ends 2026-11-19 but two providers report an executed 2026-11-23 trade (10 shares at NPR 14,600) missing from archive. 2026-11-24 trade is single-source provisional. |
| PFL | 78.67% | Merger suspension/relisting interval 2026-07-10 to 2026-09-15 supported by secondary notices; preserve no-splice restriction and continue corporate-action treatment review. |

BENH has a verified late listing: NEPSE listing 2026-10-13, trading commencement scheduled 2026-10-14, first confirmed executed OHLCV row 2026-10-15. Its low overlap is explained by the short available history; the 14 October execution status remains to be checked. See [BENH listing and first-trade validation](BENH_listing_and_first_trade_validation_2026-11-26.md).

Evidence:
- [NLO sparse-trading review](NLO_sparse_trading_vs_archive_staleness_review_2026-11-26.md)
- [BNL sparse-history reconciliation](BNL_sparse_history_and_missing_trade_reconciliation_2026-11-26.md)
- [Low-coverage lifecycle review](equity_low_coverage_lifecycle_review_2026-11-26.md)

## Later-start candidates — lifecycle checked (11 symbols)

| Symbol | Overlap | First archive date | Last archive date | Rows in 225-date window |
|---|---:|---|---|---:|

| SAPIL | 24.89% | 2026-08-13 | 2026-11-20 | 108 |
| MEPDL | 25.33% | 2026-08-12 | 2026-11-20 | 57 |
| ECL | 32.89% | 2026-07-17 | 2026-11-20 | 75 |
| KAHL | 37.78% | 2026-07-02 | 2026-11-20 | 86 |
| SGHL | 37.78% | 2026-07-02 | 2026-11-20 | 86 |
| SNORL | 39.56% | 2026-06-26 | 2026-11-20 | 90 |
| TPKHL | 41.33% | 2026-06-22 | 2026-11-20 | 94 |
| YMHL | 41.33% | 2026-06-22 | 2026-11-20 | 94 |
| APHL | 44.89% | 2026-06-10 | 2026-11-20 | 108 |
| SOPL | 45.78% | 2026-06-08 | 2026-11-20 | 110 |
| KHPL | 48.89% | 2026-05-26 | 2026-11-20 | 123 |

Nine symbols have matching dated commencement/debut evidence and first positive-volume archive rows. APHL (notice 2026-06-09; archive first row 2026-06-10) and KHPL (scheduled commencement 2026-05-25; archive/debut first trade 2026-05-26) retain one-session discrepancies pending floorsheet confirmation. See [later-start lifecycle validation](later_start_equity_lifecycle_validation_2026-11-26.md). Dates before supported commencement should not be counted as missing OHLCV; do not infer an execution on a scheduled date.

## Mid-2026 start / low overlap unresolved

| Symbol | Overlap | First archive date | Last archive date |
|---|---:|---|---|
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
| UNL | 80.89% | 2024-03-05 | 2026-11-20 |

PCIL through RSML have archive starts within 2026 and need listing/lifecycle verification first; UNL has a much longer history and should receive a dedicated source/coverage audit. The overlap score alone is not enough to determine which dates should have OHLCV.

## Next validation sequence

1. Complete floorsheet reconciliation for APHL 2026-06-09 and KHPL 2026-05-25; nine other later-start candidates have aligned published commencement and archive first-volume dates.
2. Obtain symbol-specific executed-trade calendars or daily floorsheet summaries for the 11 mid-2026-start low-overlap symbols.
3. Reconcile the BNL 23 November row and obtain independent confirmation of the 24 November candidate.
4. Keep no-trade dates separate from missing-source records; never synthesize OHLCV from a carried-forward close.
5. Recompute coverage only against symbol-specific expected-trade evidence, retaining the original proxy audit for reproducibility.

## Release control

No raw OHLCV was edited by this triage. No symbol is promoted to canonical or training data by this register. NLO and BNL remain excluded from ordinary BUY eligibility on liquidity grounds pending repeated executable trading.
