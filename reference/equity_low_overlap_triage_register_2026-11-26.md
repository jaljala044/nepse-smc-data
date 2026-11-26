# Equity Low-Overlap Triage Register — 2026-11-26

## Purpose and method

This register triages the 26 provisional common-equity symbols below 90% observed-date overlap in the 2026-11-26 audit. The comparison denominator is 225 positive-trade dates for sampled security ID 8108; it is a screening proxy, not a universal expected-session calendar. Absence of a symbol row can mean no execution, later listing/trading start, suspension, lifecycle event, or source omission.

## Triage summary

| Triage group | Count | Interpretation | Current disposition |
|---|---:|---|---|
| Symbol-specific reviewed | 4 | NLO, BNL, PFL, BENH | Evidence reports linked below; classifications updated |
| Later-start candidates lifecycle-checked | 11 | All 11 archive start boundaries reviewed; APHL and KHPL first execution occurred one session after scheduled commencement; archive first positive-volume rows align with reported actual debut dates | Boundary disposition reviewed using dated secondary evidence; not exchange-authenticated floorsheet proof |
| Mid-2026 start / low overlap boundary-reviewed | 10 | PCIL, SIPD, SKHEL, RLEL and six further equities have archive starts aligned with published commencement or reported first-debut evidence | Start-boundary explanation is documented; later session-by-session completeness remains unproven |
| Long-history source boundary | 1 | UNL archive begins 2024-03-05 despite long-established listing; alternate source audit found 1,467 earlier rows but severe OHLC defects | Alternate file rejected for ingestion; historical backfill remains blocked |

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

Nine symbols have matching dated commencement/debut evidence and first positive-volume archive rows. APHL (scheduled commencement 2026-06-09; first reported execution/archive row 2026-06-10) and KHPL (scheduled commencement 2026-05-25; first reported execution/archive row 2026-05-26) are now reconciled as scheduled-vs-actual first-trade shifts, not unresolved archive defects. See [first-trade boundary reconciliation](first_trade_boundary_reconciliation_2026-11-26.md). Dates before supported first execution must not be counted as missing OHLCV; do not infer an execution on a scheduled date.

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

PCIL, SIPD, SKHEL and RLEL have archive starts aligned with published commencement or reported first special pre-open trades. SKHL, BJHL, SOHL, HFIN, SABBL and RSML have dated first-trading/debut evidence aligned with archive first positive-volume rows. See [mid-2026 boundary review](mid_2026_low_overlap_equity_archive_boundary_review_2026-11-26.md) and [first-trade reconciliation](first_trade_boundary_reconciliation_2026-11-26.md). These are secondary-source lifecycle checks, not independent proof of every later expected session. UNL is a distinct historical source-coverage issue; see [UNL alternate-source audit](UNL_historical_coverage_alternate_source_audit_2026-11-26.md).

## Next validation sequence

1. APHL/KHPL scheduled-vs-actual debut differences reconciled from dated reports; all 11 later-start archive boundaries now have a documented lifecycle disposition, with secondary-source provenance caveat.
2. Obtain symbol-specific executed-trade calendars or daily floorsheet summaries to distinguish no-trade sessions from source omissions after the first-debut boundary for the 10 mid-2026-start equities.
3. Reconcile the BNL 23 November row and obtain independent confirmation of the 24 November candidate.
4. Keep no-trade dates separate from missing-source records; never synthesize OHLCV from a carried-forward close.
5. Recompute coverage only against symbol-specific expected-trade evidence, retaining the original proxy audit for reproducibility.

## Release control

No raw OHLCV was edited by this triage. No symbol is promoted to canonical or training data by this register. NLO and BNL remain excluded from ordinary BUY eligibility on liquidity grounds pending repeated executable trading.


## Reconciliation update — 2026-11-26

The 2026-11-26 first-trade reconciliation resolves the APHL/KHPL scheduled-vs-actual debut exceptions and documents matching archive first positive-volume rows for SKHL, BJHL, SOHL, HFIN, SABBL and RSML. The mid-2026 boundary review also documents PCIL, SIPD, SKHEL and RLEL. Therefore, the earlier label “11 unresolved” is superseded for archive-start boundaries: ten 2026-start equities have lifecycle-aligned start boundaries, while UNL remains a separate historical source-coverage issue. This does not establish complete daily OHLCV coverage after those dates. No raw rows were added, removed, or promoted.
