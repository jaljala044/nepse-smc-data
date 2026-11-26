# NEPSE Common-Equity OHLCV — Derived Dataset v2

Status: official-EOD-backed derived release; not fully session-clean  
Scope: 281 common-equity symbols  
Raw preservation: all raw source files are read-only and their Git blob SHAs were checked against the v1 manifest.

## P4.28 official evidence applied

- 599 official NEPSE EOD rows across 254 symbols and six business dates.
- 490 one-day date shifts moved from raw closed dates to the official business dates in this derived view.
- 109 official rows inserted where the SMC v1 raw-derived file had no row.
- 112 field corrections applied from official EOD: 109 Open and 3 Close.
- Every official row passed the strict EOD capture validator with zero quality flags and a matching security ID.
- Original official payload SHA-256, URL and retrieval timestamp are preserved in provenance_ledger.csv.

## Preservation and limitations

- No file under 03_stock_charts_ohlcv/ was modified.
- v1 remains unchanged and is preserved as the prior release.
- Adjacent repeated OHLCV rows and remaining source quality flags are retained; this release does not claim full expected-session completeness.
- Rows without official evidence are not changed or promoted.

## Files

- *_OHLCV.csv: derived symbol files.
- manifest.csv: raw and derived Git blob hashes, row counts and official coverage.
- corrections.csv: row/date/field changes, including the prior RHGCL correction.
- provenance_ledger.csv: 599 exact official EOD row references.
- totals.json: build totals.
