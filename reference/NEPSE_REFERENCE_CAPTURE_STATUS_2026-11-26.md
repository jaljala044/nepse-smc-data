# NEPSE reference capture status — 2026-11-26

## 1. Official current company / security page

Source page: https://nepalstock.com.np/company

A rendered browser capture exposed these filters:
- Status: Active (A), Suspended (S), Delisted (D).
- Instrument: Equity, All Instrument, Mutual Funds, Non-Convertible Debentures, Preference Shares.
- Page-size choices included up to 500.

A structured follow-up capture reported:
- Active Equity: 281 rows, 281 unique symbols, no duplicates reported.
- Active Mutual Funds: 47 rows, 47 unique symbols, no duplicates reported.
- All active instruments: 328 rows.
- Preference Shares filter: 0 rows returned.
- Non-Convertible Debentures filter: 0 rows returned.
- The Suspended and Delisted filters were available but their result rows were not extracted.

The 47 mutual-fund rows are included in `nepse_current_mutual_fund_snapshot_2026-11-26.csv`. Forty-six have matching OHLCV files; NICEF does not.

### Important extraction consistency issue
A separate first-pass equity-table report contained 281 rendered rows but parsed to 278 unique symbols, with repeated USLB and SYPNL rows and repeated detail-route IDs. A later structured pass reported 281 unique symbols and zero duplicates, but its row-level payload exposed only the first 20 equity rows. These outputs conflict. Therefore the 281 equity row count is a reported UI count, not a fully verified row-level export. The first-pass comparison file is retained as provisional evidence only.

The numeric `/company/detail/{id}` route value is not proven to be a globally unique, stable security ID. The detail page uses a company profile for equities; a mutual-fund detail route appears scheme-specific. No raw `securityId` field or official full security-register response was captured. The guessed API route is not used as evidence. The direct public API probe returned HTTP 401 without the authenticated request flow.

## 2. Historical symbol reconciliation

The repository tree contains 525 `*_OHLCV.csv` files under `03_STOCK_CHARTS_OHLCV`.

Provisional cross-check:
- First-pass equity list: 278 unique parsed symbols; 278 OHLCV filename matches.
- Mutual funds: 47 unique active symbols; 46 OHLCV filename matches; NICEF has no OHLCV file.
- First-pass equity unmatched: 247 files. Of those, 46 match the current mutual-fund list, leaving 201 not present in either captured list.
- Because the first-pass and second-pass equity captures conflict, do not treat 278/247/201 as final. Do not label unmatched symbols as unknown, inactive, renamed or delisted without the missing instrument/status history.

The 525-row cross-check file records the provisional equity match and structured mutual-fund match separately.

## 3. Duplicate, inactive and renamed security review

Confirmed:
- The OHLCV file paths are unique in the Git tree.
- The first-pass NEPSE equity table extraction contains repeated USLB and SYPNL rows and duplicate detail-route IDs; the second structured pass contradicts those findings. These are capture anomalies requiring a raw API/export check, not confirmed exchange duplicates.
- 47 mutual-fund symbols are unique in the structured filter result.

Not yet established:
- Full suspended and delisted security lists.
- Historical security IDs and instrument types for all 525 filenames.
- Effective dates for symbol changes, mergers, delistings, or re-listings.
- Whether the 201 OHLCV names absent from the captured equity/mutual-fund lists are debentures, promoter/preference classes, expired funds, delisted equities, renamed instruments, or source naming variants.

## 4. Historical exchange calendar

The official NEPSE Holiday Listing page supports year selection from 2007 through 2027 and paginated rows. Complete all-page captures currently available in `nepse_holiday_listing_entries_2014-2025.csv`:
- 2025: 46 rows / 5 pages
- 2024: 37 / 4
- 2023: 37 / 4
- 2022: 36 / 4
- 2021: 25 / 3
- 2019: 22 / 3
- 2018: 29 / 3
- 2017: 38 / 4
- 2016: 33 / 4
- 2015: 54 / 6
- 2014: 51 / 6

Total: 408 holiday-list rows across 11 fully captured years.

Partial / missing:
- 2020: partial; approximately 101 rows / 11 pages reported, but not every page was fully captured.
- 2013: partial; 20 rows extracted from a 30-page table; remaining pages not captured.
- 2012: page 1 was briefly viewed; full count and all rows not captured.
- 2011: not captured.
- 2026: a separate official holiday API snapshot already exists in the repository (41 records); this is not a full open-session calendar.

Holiday-list entries are stored exactly as captured. Descriptions such as `for settlement`, `market closed until next decision`, `Emergency Holiday`, `As Per NEPSE Board`, and `Public holiday` remain raw labels. They are not automatically converted into `verified_closed` because the listing does not expose an explicit exchange-closure boolean or session-scope field.

No open dates are inferred from weekdays alone. Existing session-regime code is candidate logic; the full historical exchange calendar remains incomplete.

## 5. Validation and canonical promotion

PR #5: https://github.com/jaljala044/nepse-smc-data/pull/5

The validator was hardened to:
- reject overlapping stable security-ID claims across different symbols;
- reject duplicate/overlapping register rows for one stable ID;
- allow non-overlapping symbol renames that retain the same stable ID;
- require `valid_from` on instrument mappings.

GitHub Actions run 3 completed successfully. The workflow ran **19 unit tests**, all passing.

Canonical promotion must remain blocked until the official register is complete, every historical symbol is mapped to one evidenced security identity, lifecycle dates are verified, and every data date has explicit exchange-session evidence.
