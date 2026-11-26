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
- 258 pairs are byte-identical; 23 pairs differ.
- SMC repository: 246,129 rows across the 281 equity files; 1,329 invalid OHLC rows, all within the 23 divergent pairs.
- History starter: 233,457 rows across the 281 equity files; 0 invalid OHLC rows under the tested invariant.
- No duplicate dates or zero-volume rows were found in either repository's audited files.
- The 258 identical pairs contain 71,801 adjacent repeated OHLCV rows across 252 symbols.
- Across the 23 divergent pairs, SMC has 5 adjacent repeated OHLCV rows; starter has 7,067.
- Adjacent repeats are not automatically treated as executed trades or definitively labelled forward-filled without date-level/source validation.
- No raw OHLCV files were changed.

## Remaining work after this queue

1. Reconcile all 23 divergent symbol histories using ShareHub, Chukul, ShareSansar and NepseAlpha, keeping both raw versions.
2. Investigate the 1,329 SMC OHLC invariant failures and produce a provenance-tracked derived view rather than editing raw files.
3. Classify repeated OHLCV rows against the correct weekly closure regime.
4. Validate listing/suspension/lifecycle dates before claiming expected-session completeness.
