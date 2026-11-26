# Cross-repository OHLCV and scanner-input comparison — 2026-11-26

Repositories compared:
- `jaljala044/nepse-smc-data`
- `jaljala044/nepse-history-starter`

## OHLCV universe

- Both repositories contain exactly **525** files under `03_stock_charts_ohlcv/`.
- All 525 symbol filenames are present in both repositories.
- 25 files have different Git blob hashes. A byte-level difference is not automatically a numeric data conflict: formatting and historical coverage differ.
- Every common date row in the 25 differing files was compared numerically after parsing the OHLCV fields.

## Findings

### Resolved from supplied evidence
- BGWT, MEHL, RAWA, RHGCL and ULHC on 2025-07-28 now use the user's supplied ShareHub chart values and match across both repositories.
- API on 2026-11-19 matches across both repositories and the supplied evidence.
- HRL on 2026-11-19 was corrected in `nepse-smc-data` from low=483.90 to low=480.00 to match the supplied ShareHub chart evidence and `nepse-history-starter`. The corrected row was read back after commit.

### One numerical conflict remains quarantined
For `RHGCL` on `2026-11-19`, the two repositories disagree:
- `nepse-smc-data`: `2026-11-19,252.1,259.5,252.1,256,4216`
- `nepse-history-starter`: `2026-11-19,252.1,259.5,252.1,258,9054`

This date/symbol is not covered by the supplied chart/floorsheet evidence package. Neither value is selected here. Preserve both source versions and quarantine this row pending dated source evidence.

For the other common-date rows in the 25 differing OHLCV files, the numeric OHLCV values match after normalization. The remaining byte-level differences are attributable to row coverage and/or numeric formatting, not observed numeric conflicts in the common rows.

## Scanner-input comparison

Three common scanner-input files have byte-level differences:
- `scanner_inputs/index_history/closes_only.csv`: Starter contains three additional dates (2026-11-23, 2026-11-24, 2026-11-25); no differing values were found for common date/index keys.
- `scanner_inputs/market_summary_daily.csv`: Starter contains three additional dates (2026-11-23, 2026-11-24, 2026-11-25); no differing values were found for common dates.
- `scanner_inputs/sector_data.csv`: Starter contains 18 additional sector/date rows; no differing values were found for common sector/date keys.

The extra rows have source labels in Starter that reference ShareSansar, ShareHub, Merolagani, and Shikhar Signals. They were not copied into SMC by this comparison because the source artifacts and provenance for each additional row have not yet been independently audited here.

## Disposition

- 525/525 OHLCV symbol files exist in both repositories.
- Seven user-confirmed stock-date records (five July 2025 plus API/HRL November 2026) are aligned with the supplied evidence.
- One separate RHGCL 2026-11-19 numerical conflict remains unresolved and must stay quarantined.
- Three scanner-input files have coverage differences only on non-overlapping dates/keys; preserve the added rows in Starter until their provenance is audited.
- No blanket repository copy or overwrite was performed.

This comparison is not an official NEPSE verification. Source hierarchy and point-in-time provenance rules remain in force.
