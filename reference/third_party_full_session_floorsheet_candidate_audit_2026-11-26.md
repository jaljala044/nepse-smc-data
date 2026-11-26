# Third-party full-session floorsheet candidate audit — 2026-11-26

## Scope and source

Inspected `socrateai-official/nepse-open-data`, specifically `floorsheet/floorsheet_2026-11-20.csv`, its repository README and LICENSE.

- Repository: https://github.com/socrateai-official/nepse-open-data
- Raw file: https://github.com/socrateai-official/nepse-open-data/blob/main/floorsheet/floorsheet_2026-11-20.csv
- Git blob SHA: `6f74994849641296e2a16cad22fb555b08955c35`
- File size: 2,335,392 bytes
- Source repository commit: `cfa92493e93211c7019a5cd0b2cbe7d400d9c4e3` (2026-11-24)
- Repository README describes the folder as daily raw trade data; it does not document the exact capture mechanism, upstream NEPSE pagination totals, raw response hashes, or a per-date completeness manifest.
- Repository LICENSE is MIT. That does not independently establish rights to redistribute underlying exchange-origin data commercially.

This is a third-party public archive candidate, not an authenticated NEPSE-origin raw response. Do not promote it to authoritative source status based only on the repository description.

## File-level validation (2026-11-20)

Parsed 39,966 contract rows.

| Check | Result |
|---|---:|
| Rows | 39,966 |
| Distinct symbols | 352 |
| Duplicate transaction IDs | 0 |
| Rows with date other than 2026-11-20 | 0 |
| Non-positive quantity/rate | 0 |
| Amount identity failures where abs(quantity × rate − amount) > NPR 0.01 | 0 |
| Total shares | 10,602,468 |
| Total turnover | NPR 3,887,563,470.82 |

These checks establish internal consistency, not full-day completeness. No independent upstream `totalElements`/page count or exchange-issued day total was present in the repository metadata examined.

## Cross-check against the current data repository

Compared the third-party floorsheet's aggregate quantities with the existing five current-equity OHLCV files for the same date.

| Symbol | Floorsheet contracts | Floorsheet shares | Existing OHLCV volume | Result |
|---|---:|---:|---:|---|
| NESDO | 22 | 1,521 | 1,521 | MATCH |
| SYPNL | 367 | 32,947 | 32,947 | MATCH |
| ULBSL | 24 | 504 | 504 | MATCH |
| USLB | 26 | 1,595 | 1,595 | MATCH |
| YMHL | 169 | 5,951 | 5,951 | MATCH |

The five-symbol cross-check covers 608 contracts and 42,518 shares. It is positive independent corroboration for these five symbol/date quantities only. It does not establish completeness for every security or date.

## Comparison with the existing 500-row extract

The existing `02_floorsheet_daily/floorsheet_2026-11-20.csv` contains 500 rows and has a different schema/transaction-ID representation. No exact match was found between its rows and the third-party file using symbol, buyer, seller, quantity and rate. This is a source-level discrepancy requiring provenance investigation; do not merge the 500 rows into the candidate file or treat them as a verified subset.

## Decision

- Candidate classification: `THIRD_PARTY_FULL_SESSION_CANDIDATE`, not `VERIFIED_COMPLETE`.
- Positive trade evidence can be used cautiously for rows that pass symbol/date/contract validation and independent OHLCV reconciliation.
- Absence of a symbol from this candidate file must remain `UNKNOWN` until full-day completeness is independently evidenced.
- Do not write this file into canonical floorsheet storage, do not infer `NO_TRADE`, and do not use it for broker-footprint scoring yet.
- Next validation: obtain source capture metadata/upstream total for 2026-11-20, investigate the 500-row extract mismatch, then repeat the five-symbol and broader equity-universe quantity reconciliation across additional dates.

## Reproducibility references

- Third-party floorsheet Git blob: `6f74994849641296e2a16cad22fb555b08955c35`
- Third-party EOD board Git blob used for inspection only: `33784c60c509be30812cd2c8004276271fc0df8a`
- Existing local floorsheet sample Git blob: `0ca3de49d855b240ddf568fa95ce5999e4603c40`
- Existing five-symbol OHLCV blobs are recorded in the five-symbol reconciliation report dated 2026-11-26.
