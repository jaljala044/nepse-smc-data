# Derived Common-Equity OHLCV v1 Release — 2026-11-26

## Release

**Branch:** `derived/ohlcv-v1`  
**Commit:** `d60112b633f05dfe03256b49f3c327be103d93d0`  
**Scope:** 281 provisional common-equity symbols  
**Total source rows:** 246,129  
**Raw files modified:** 0  
**Derived field values changed:** 2 (one row: RHGCL, 2026-11-19)

## Dataset

- [Derived dataset directory](https://github.com/jaljala044/nepse-smc-data/tree/derived/ohlcv-v1/derived/ohlcv_v1)
- [README and derivation policy](https://github.com/jaljala044/nepse-smc-data/blob/derived/ohlcv-v1/derived/ohlcv_v1/README.md)
- [281-symbol source/derived blob manifest](https://github.com/jaljala044/nepse-smc-data/blob/derived/ohlcv-v1/derived/ohlcv_v1/manifest.csv)
- [Correction ledger](https://github.com/jaljala044/nepse-smc-data/blob/derived/ohlcv-v1/derived/ohlcv_v1/corrections.csv)

## Derivation policy and outcome

1. All 281 derived files start from the corresponding SMC raw OHLCV file, retaining the broader historical coverage.
2. Unmodified derived files reuse the exact raw Git blob. The manifest records source and derived blob SHAs.
3. Exactly one source-supported row correction is applied to the derived RHGCL file for 2026-11-19:
   - Close: 256.0 -> 258.0
   - Volume: 4,216 -> 9,054
   - Open, High unchanged; Low unchanged.
4. ShareSansar-derived daily archive evidence matches the history-starter row exactly. Raw SMC remains unchanged.
5. All other OHLCV rows, including the 1,329 OHLC invariant flags and adjacent repeated rows, are retained. No unverified correction, deletion, or forward-fill removal is performed.

## Verification performed

- Derived manifest contains exactly 281 symbols.
- 281 symbol CSV files are included in the derived branch.
- Total rows represented by the 281 manifest entries: 246,129.
- RHGCL derived row verified as `2026-11-19,252.1,259.5,252.1,258.0,9054.0`.
- RHGCL raw row verified unchanged as `2026-11-19,252.1,259.5,252.1,256.0,4216.0`.
- API derived file blob SHA matches the source raw file SHA; sample verification of byte reuse succeeded.

## Repeated-row quality flag pilot

A date-level quality-flag pilot is included under [quality_flags](https://github.com/jaljala044/nepse-smc-data/tree/derived/ohlcv-v1/derived/ohlcv_v1/quality_flags). It currently covers 14/281 symbols and flags 3,288 adjacent identical-OHLCV rows: 688 weekly-closed-day candidates, 187 weekly-open-weekday repeats, and 2,413 outside the current calendar evidence window. These are flags only; no records are removed. See the [pilot README](https://github.com/jaljala044/nepse-smc-data/blob/derived/ohlcv-v1/derived/ohlcv_v1/quality_flags/README.md).

## Limitations and next work

This is a conservative derived release, not final trading-session-clean data. Repeated OHLCV rows are retained pending date-level classification against the pre/post 2026-04-06 weekly calendar regimes. The session calendar has limited observed-open scope, and per-symbol expected-session completeness still requires lifecycle/suspension evidence. The source-reported OHLC invariant flags remain uncorrected except for the single source-supported RHGCL mismatch.
