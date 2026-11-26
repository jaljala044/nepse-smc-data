# NEPSE Equity Data Validation — Five-Task Queue Status
Updated: 2026-11-26

Scope: common equities only. Raw OHLCV is preserved. NICEF/mutual funds are excluded from this work queue.

| # | Task | Status | Evidence |
|---|---|---|---|
| 1 | Reconcile observed trading dates against 2025/2026 closure captures | Completed; sample scope retained | [Reconciliation report](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_session_date_reconciliation_2026-11-26.md) |
| 2 | Cross-check disputed/exceptional dates with accepted providers | Completed; targeted dates only | [Provider cross-check report](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_provider_date_crosscheck_2026-11-26.md) |
| 3 | Build canonical date-level session calendar | Completed for 2025-11-25 through 2026-12-30 | [Canonical CSV](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_canonical_session_calendar_2025-2026.csv) · [Documentation](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_canonical_session_calendar_2025-2026.md) |
| 4 | Calculate per-symbol observed-date coverage for 281 provisional equities | Completed as a bounded observed-date proxy; final expected-session completeness pending lifecycle/suspension evidence | [Per-symbol CSV](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/equity_observed_date_coverage_2026-11-26.csv) · [Report](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/equity_observed_date_coverage_audit_2026-11-26.md) |
| 5 | Extend OHLCV row-quality audit across both repositories | Partial: repository parity complete for all 281; detailed row-level checks completed for 23 divergent pairs plus earlier 10-symbol pilot; 258 byte-identical pairs still need full row-level checks | [Divergence CSV](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/equity_repository_divergence_audit_2026-11-26.csv) · [Parity/quality report](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/equity_repository_parity_quality_audit_2026-11-26.md) |

## Key measured results

- 281/281 provisional equity OHLCV paths exist in both repositories.
- 258 file pairs have identical Git blob SHA; 23 file pairs differ.
- Across the 23 divergent pairs, `nepse-smc-data` contains 1,329 invalid OHLC rows under the tested invariant. The corresponding starter files contain 0 invalid OHLC rows but 7,067 adjacent repeated OHLCV rows.
- The 23 divergent pairs disagree on OHLCV values for every shared date in the inspected pairs. Neither source should be silently selected as canonical.
- The 225 positive-trade dates in the canonical calendar come from sampled security ID 8108; they are not a complete market-wide expected-session denominator.
- No raw OHLCV files have been modified by these audits.

## Next actions

1. Resolve the 23 divergent symbol histories using ShareHub, Chukul, ShareSansar and NepseAlpha evidence, preserving raw copies and producing a provenance-tracked derived view.
2. Run full row-level quality checks across the 258 byte-identical pairs; identical files can still contain shared data-quality problems.
3. Verify symbol listing, suspension, and lifecycle dates before converting observed-date overlap into true expected-session coverage.
4. Investigate the NLO archive ending 2026-09-30 and the low-overlap symbols in the Task 4 report.
