# RHGCL 2026-11-19 OHLCV Reconciliation — 2026-11-26

## Finding

The only numeric OHLCV mismatch found across the 13,518 common dates in the 23 divergent repository pairs is RHGCL on 2026-11-19.

| Field | SMC raw file | History-starter raw file | ShareSansar-derived archive |
|---|---:|---:|---:|
| Open | 252.10 | 252.10 | 252.10 |
| High | 259.50 | 259.50 | 259.50 |
| Low | 252.10 | 252.10 | 252.10 |
| Close | 256.00 | 258.00 | 258.00 |
| Volume | 4,216 | 9,054 | 9,054 |

The ShareSansar-derived daily archive row matches the history-starter values exactly, including volume, and not the SMC values.

## Evidence

- [ShareSansar-derived daily archive file for 2026-11-19](https://github.com/shawinCreates/Nepse-Market-Data/blob/main/Data/csv/daily_price/2026_11_19.csv)
- [Detailed comparison CSV](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/RHGCL_2026-11-19_source_reconciliation_2026-11-26.csv)
- [Source README: daily prices scraped from ShareSansar](https://github.com/shawinCreates/Nepse-Market-Data/blob/main/README.md)

## Decision

- Classify this row as a **source-supported correction candidate** for a derived dataset.
- If a derived canonical view is created, use Close 258.00 and Volume 9,054 for this date, with ShareSansar provenance.
- Preserve the SMC raw row unchanged.
- Do not generalize this result to any other date or symbol without row-level evidence.
