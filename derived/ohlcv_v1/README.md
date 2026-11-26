# NEPSE Common-Equity OHLCV — Derived Dataset v1

**Status:** conservative, provenance-tracked derived release  
**Scope:** 281 provisional common-equity symbols  
**Raw source:** `03_stock_charts_ohlcv/{SYMBOL}_OHLCV.csv` in the parent repository  
**Raw preservation:** no raw source file was modified.

## Derivation rules

1. Each derived symbol file starts from the corresponding SMC raw OHLCV file. This retains the broader date coverage seen in the 23-pair numeric comparison.
2. All source rows are retained. No calendar-day repeats are deleted, no dates are invented, and no missing or unusual OHLC fields are guessed or filled.
3. Exactly one row correction is applied: RHGCL on 2026-11-19. Close is changed from 256.0 to 258.0 and Volume from 4216.0 to 9054.0. Open, High and Low are unchanged.
4. The corrected values are now confirmed by the direct official NEPSE EOD board for 2026-11-19 (Security ID 8108; 47 trades; NPR 2,332,952.50 turnover). The immutable raw response SHA-256 is `303d92756ffbcaa2e6ab5020c29e1eab1b63ed99797bf024914dbb863cbae183`; capture artifact ID 15137973461. See [official evidence record](../../reference/official_eod_captures/RHGCL_2026-11-19_nepse_eod.json), [row-level reconciliation](../../reference/RHGCL_2026-11-19_source_reconciliation_2026-11-26.md) and [candidate register](../../reference/ohlcv_derived_correction_candidates_2026-11-26.csv). The original SMC raw row remains unchanged.
5. The 1,329 SMC OHLC invariant flags are retained, not silently repaired. A 13-symbol sample was corroborated against ShareSansar-derived rows; this is not exhaustive verification. See [source corroboration report](../../reference/shareSansar_source_corroboration_ohlc_flags_2026-11-26.md).
6. Adjacent repeated OHLCV rows are retained pending date-level session adjudication. Do not automatically interpret them as executed trades.
7. This release does not certify full expected-session completeness, lifecycle coverage, or every upstream price/volume value.

## Quality flags

A date-level adjacent-repeat classification pilot is available in [quality_flags/](./quality_flags/). It currently covers 14 of 281 symbols; see its README for scope and limitations. These flags do not delete or alter OHLCV rows.

## Files

- `{SYMBOL}_OHLCV.csv`: one six-column CSV per symbol (Date, Open, High, Low, Close, Volume).
- `manifest.csv`: source and derived blob SHA, row count and derivation status per symbol.
- `corrections.csv`: row-level correction ledger.

## Reproducibility

All unmodified derived files reuse the exact Git blob of their SMC raw source file. RHGCL uses a new blob containing only the single documented row correction. Therefore every other row and every other symbol is byte-identical to its raw source.

This is a conservative derived view for downstream experiments, not a claim that every upstream value is economically correct or that every row represents an actual trading session.
