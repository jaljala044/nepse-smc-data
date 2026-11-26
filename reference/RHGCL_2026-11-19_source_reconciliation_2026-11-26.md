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

## Official NEPSE confirmation — 2026-11-26

The historical NEPSE official EOD API was queried directly for 2026-11-19. The exact response page was preserved byte-for-byte and passed the P4.23 validator.

| Official field | Value |
|---|---:|
| Security ID | 8108 |
| Open | 252.10 |
| High | 259.50 |
| Low | 252.10 |
| Close | **258.00** |
| Traded quantity | **9,054** |
| Turnover | NPR 2,332,952.50 |
| Trades | 47 |
| Last updated | 2026-11-19 14:59:54.225031 |
| Upstream board rows | 347 (one page) |
| Validator | `OFFICIAL_CAPTURE_ACCEPTED`, zero quality flags |

Primary-source provenance:
- Official endpoint: `https://www.nepalstock.com/api/nots/nepse-data/today-price?size=500&page=0&businessDate=2026-11-19`
- Retrieval time: 2026-11-26T22:33:29.871784+05:45
- Raw response SHA-256: `303d92756ffbcaa2e6ab5020c29e1eab1b63ed99797bf024914dbb863cbae183`
- Immutable response + validated extraction artifact: [GitHub Actions artifact](https://github.com/jaljala044/nepse-smc-data/actions/runs/45862108316/artifacts/15137973461) (artifact ID 15137973461; ZIP SHA-256 `72266336645ba3191c441cfa66cd493462b44f7a92fcc68db4b968e0d693a6ee`)
- Committed validated row and provenance: [official EOD evidence JSON](official_eod_captures/RHGCL_2026-11-19_nepse_eod.json)

## Final decision

- **Official NEPSE confirms Close 258.00 and Volume 9,054.**
- The SMC raw row (Close 256.00; Volume 4,216) remains unchanged as a preserved source record, but is superseded for the versioned derived OHLCV view.
- The derived RHGCL row uses the official NEPSE EOD values and cites the payload hash above.
- This resolution applies only to RHGCL on 2026-11-19. No other symbol/date conflict is inferred or promoted.
