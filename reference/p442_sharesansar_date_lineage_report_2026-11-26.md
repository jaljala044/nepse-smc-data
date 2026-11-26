# P4.42 — NMLBBL/SMPDA source-date lineage audit

**Audit date:** 2026-11-26  
**Scope:** read-only audit of 162 canonical-only symbol/date rows in the 2025-11-26 through 2026-11-26 window.  
**Primary comparison:** pinned official NEPSE per-security EOD captures from P4.36. The official endpoint supplies High/Low/Close/Volume, not Open.

## Result

**Cause supported**

All 162 canonical-only rows (81 NMLBBL, 81 SMPDA) are present in the pinned upstream ShareSansar daily CSV for the same date label, and all 162 source OHLCV tuples match the raw archive exactly. Every source HLCV+volume tuple matches exactly one official NEPSE EOD row on a different date.

The date on these rows is therefore the **scrape/archive date**, not a verified NEPSE business date. The repeated OHLCV values are source snapshots carried under later scrape-date labels; they must not be treated as additional trading sessions.

| Metric | NMLBBL | SMPDA | Total |
|---|---:|---:|---:|
| Canonical-only rows | 81 | 81 | 162 |
| Upstream daily source row found | 81 | 81 | 162 |
| Source OHLCV exactly matches raw | 81 | 81 | 162 |
| Source HLCV+volume matches official EOD on another date | 81 | 81 | 162 |
| Ambiguous official tuple matches | 0 | 0 | 0 |
| Unmatched official tuple matches | 0 | 0 | 0 |
| Duplicate canonical dates | 0 | 0 | 0 |

**Offset histogram per symbol** (canonical scrape-date label minus matched official business date):

| Offset | Rows per symbol | Rows total |
|---:|---:|---:|
| +1 day | 37 | 74 |
| +2 days | 31 | 62 |
| +3 days | 9 | 18 |
| +4 days | 3 | 6 |
| +5 days | 1 | 2 |
| **Total** | **81** | **162** |

The complete row-level matrix records each raw tuple, the unique official match date, offset, upstream daily-file path and Git blob SHA, source row values, and exact-match flags:
[`p442_sharesansar_date_lineage_matrix_2026-11-26.csv`](p442_sharesansar_date_lineage_matrix_2026-11-26.csv).

## Source provenance and mechanism

1. The import manifest in `jaljala044/nepse-history-starter` pins the upstream workbook to [ShareSansarScraper commit `d5949bd628d6b5ca9ebb2b4a15e001a434c6732c`](https://github.com/OmitNomis/ShareSansarScraper/tree/d5949bd628d6b5ca9ebb2b4a15e001a434c6732c). The manifest records workbook SHA-256 `dc9534bd1e38a467452196548f82a20b14a1fedc9a2e64983484d9137386c38c`, describes the price basis as published OHLCV from ShareSansar, and records 937 archived date sheets.
2. The two imported raw files are byte-identical across `nepse-history-starter` and this repository (matching Git blob SHAs). The v1 files are also identical to raw. The v2 and v3 files are identical to each other; each resolves two exact-date cases, leaving 79 offset rows per symbol.
3. All 81 source daily CSVs exist at the pinned ShareSansarScraper commit. The source CSV header has no `Date` column. The date label is the daily file name (`YYYY_MM_DD.csv)); the combined workbook is organized as one worksheet per daily file.
4. The scraper implementation at the 2025-11-28 file-creation revision [`1e1f14317cd778ce5c1a9cd7d379521836a00988`](https://github.com/OmitNomis/ShareSansarScraper/commit/1e1f14317cd778ce5c1a9cd7d379521836a00988) names each file using `datetime.now()` and has no duplicate-session check. It therefore records the scrape date as the file date, even when the ShareSansar page is still showing the previous session.
5. A duplicate guard was added later in [commit `2a5a24d379d964ecca8ef576b023487904ca48c9`](https://github.com/OmitNomis/ShareSansarScraper/commit/2a5a24d379d964ecca8ef576b023487904ca48c9), dated 2026-06-29. It compares all row fields except serial number, not just OHLCV. A change in a non-price field can still make a stale price table appear different and cause it to be written under the current scrape date. The file date is still assigned from `datetime.now()`.
6. The downstream import manifest points to the pinned workbook; the imported NMLBBL/SMPDA raw files have the same Git blob SHAs as the copies in `nepse-history-starter`. No downstream date correction is performed in the OHLCV CSV files.

### Direct source-row example: 2025-11-27 through 2025-11-30

The pinned upstream daily files show:

- On 2025-11-27, NMLBBL OHLCV was 654.10 / 677.00 / 654.10 / 670.00, volume 27,865; SMPDA was 900.70 / 934.80 / 900.70 / 923.00, volume 13,661.
- The 2025-11-28 file contains those same OHLCV+volume tuples but is named for 2025-11-28. Its non-price `Conf.` field differs from the 2025-11-27 file (43.76 for NMLBBL; 42.46 for SMPDA).
- The 2025-11-29 file has the same full-file Git blob SHA as the 2025-11-28 file, so it is a byte-identical repeat under another date label.
- The 2025-11-30 file contains new OHLCV values.

The old scraper code explains the date label: it writes the current scrape date as the file name and, at that revision, did not suppress duplicate snapshots. This is direct evidence that the archive date can differ from the underlying NEPSE session date.

## Raw-to-derived lineage

| Symbol | Raw and v1 Git blob SHA | v2 and v3 Git blob SHA | Raw/v1 offset rows | v2/v3 offset rows |
|---|---|---|---:|---:|
| NMLBBL | `8dd19774b8409d0d67c94f9976fc079a5518d770` | `09f95bb4d0af6d71f688bbfdfcef88f7bdb5a083` | 81 | 79 |
| SMPDA | `044d6f823b0d93c64c0906edfe00e284945fbc6f` | `4bed4eb73363d7f3c2bfa6f5a9cebcc8ca07926e` | 81 | 79 |

Raw/v1 offset histogram per symbol is 37 / 31 / 9 / 3 / 1 for offsets +1 through +5. v2/v3 is 35 / 31 / 9 / 3 / 1. No v2/v3 rows were promoted based solely on tuple matching; this audit only records the existing derived-file state.

## Related cross-sector check

The in-flight P4.37 stratified audit samples 24 equities across 12 sectors. Its corrected report records 1,455/1,455 canonical-only rows with matching official HLCV+volume tuples on other dates; aggregate offsets are +1: 664, +2: 556, +3: 163, +4: 54, +5: 18. It also retains three exact-date value mismatches (AHPC 2026-07-17, CFCL 2026-11-18, HDL 2026-07-17) as unresolved. This is a purposive sample, not a full-universe estimate.

## Disposition and safeguards

- **Root cause classification:** upstream scrape-date labeling is supported by the pinned source files and scraper implementation. The 162 row-level source matches are recorded in the matrix.
- **Not a trade-date correction:** do not relabel the rows automatically. The official tuple match establishes a value/date correspondence, not a contract-level execution record or a complete official floorsheet.
- **No canonical edits:** raw, v1, v2, v3 and scanner inputs were not changed by this audit.
- **Lifecycle remains UNKNOWN:** NMLBBL and SMPDA `valid_from` remain UNKNOWN; no NO_TRADE assertion is made.
- **No OHLCV values, dates, scanner eligibility, scores, or trading decisions were changed.**
- The test suite checks the 162-row matrix, unique offsets, upstream row matches, and Git blob hashes of the raw files to guard against accidental mutation.
