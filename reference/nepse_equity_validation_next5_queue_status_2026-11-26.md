# NEPSE Equity Data Validation — Five-Task Queue Status
Updated: 2026-11-26

Scope: common equities only. NICEF/mutual funds are excluded. Raw OHLCV is preserved.

| # | Task | Status | Evidence |
|---|---|---|---|
| 1 | Reconcile observed trading dates against 2025/2026 closure captures | Completed; bounded to captured observed dates and closure evidence | [Reconciliation report](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_session_date_reconciliation_2026-11-26.md) |
| 2 | Cross-check disputed/exceptional dates with accepted providers | Completed for targeted dates; not an exhaustive date audit | [Provider cross-check report](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_provider_date_crosscheck_2026-11-26.md) |
| 3 | Build canonical date-level session calendar | Completed for 2025-11-25 through 2026-12-30, with observed-sample scope documented | [Canonical CSV](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_canonical_session_calendar_2025-2026.csv) · [Documentation](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_canonical_session_calendar_2025-2026.md) |
| 4 | Calculate per-symbol observed-date coverage for 281 provisional equities | Completed as an observed-date proxy; final expected-session completeness still requires lifecycle/suspension evidence | [Per-symbol CSV](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/equity_observed_date_coverage_2026-11-26.csv) · [Report](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/equity_observed_date_coverage_audit_2026-11-26.md) |
| 5 | Run row-level structural quality checks across both repositories | Completed for all 281 equity pairs: 258 byte-identical pairs audited once (same blob SHA), 23 divergent pairs audited on both sides | [258-pair audit CSV](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/equity_identical_pair_row_quality_audit_2026-11-26.csv) · [Full parity/quality report](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/equity_repository_parity_quality_audit_2026-11-26.md) |

## Key results

- 281/281 provisional equity OHLCV paths exist in both repositories.
- 258 pairs are byte-identical; 23 pairs have different file blobs, mainly due to date coverage and carry-forward construction. Numeric comparison across their 13,518 common dates found 13,517 exact matches and only one genuine mismatch (RHGCL, 2026-11-19).
- SMC repository: 246,129 rows across the 281 equity files; 1,329 OHLC invariant flags, all within the 23 divergent pairs. A 13-symbol sample matched the ShareSansar-derived archive exactly, so these are source-reported anomalies, not automatically repository corruption. See [source corroboration evidence](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/shareSansar_source_corroboration_ohlc_flags_2026-11-26.md).
- History starter: 233,457 rows across the 281 equity files; 0 invalid OHLC rows under the tested invariant.
- No duplicate dates or zero-volume rows were found in either repository's audited files.
- The 258 identical pairs contain 71,801 adjacent repeated OHLCV rows across 252 symbols.
- Across the 23 divergent pairs, SMC has 5 adjacent repeated OHLCV rows; starter has 7,067.
- Adjacent repeats are not automatically treated as executed trades or definitively labelled forward-filled without date-level/source validation.
- No raw OHLCV files were changed.

## Repeated-row quality flag pilot

A date-level adjacent-identical-OHLCV overlay has been added to branch [derived/ohlcv-v1](https://github.com/jaljala044/nepse-smc-data/tree/derived/ohlcv-v1/derived/ohlcv_v1/quality_flags), commit `e532fff6c03ad3670079d20b362a730092c35d8d`. It covers the first 14 of 281 symbols and records 3,288 adjacent-repeat rows: 688 weekly-closed-day candidates, 187 weekly-open-weekday repeats, and 2,413 rows outside the currently supported calendar-regime evidence window. This is explicitly a pilot; no OHLCV rows were removed or changed. [Pilot README](https://github.com/jaljala044/nepse-smc-data/blob/derived/ohlcv-v1/derived/ohlcv_v1/quality_flags/README.md).

## Remaining work after this queue

1. Apply the source-supported RHGCL 2026-11-19 value only in a separately versioned derived dataset; keep both raw versions. [RHGCL reconciliation](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/RHGCL_2026-11-19_source_reconciliation_2026-11-26.md) · [Candidate register](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/ohlcv_derived_correction_candidates_2026-11-26.csv).
2. Continue source-level adjudication of the 1,329 SMC OHLC invariant flags; 13 sampled rows are already corroborated by ShareSansar. Preserve raw values and produce only a provenance-tracked derived view if stronger evidence supports a correction.
4. Validate listing/suspension/lifecycle dates before claiming expected-session completeness.
