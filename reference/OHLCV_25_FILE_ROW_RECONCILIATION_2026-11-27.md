# P4.44 — 25-file cross-repository OHLCV row reconciliation

**Audit date:** 2026-11-27  
**Mode:** read-only evidence comparison; no source CSV, canonical row, or scanner input was modified.  
**Branch:** `audit/ohlcv-row-reconciliation-2026-11-27`

## Source snapshots

- `jaljala044/nepse-smc-data` main commit: `54fbed963830dd9f064332770309f1ffda5ebe42` (2026-11-26T22:00:12Z).
- `jaljala044/nepse-history-starter` main commit: `dfbf96f0322459b2910fe9c3edb4bd2b26efae2c` (2026-11-26T16:02:59Z).
- Compared path in both repositories: `03_stock_charts_ohlcv/*_OHLCV.csv`.
- The history-starter import manifest pins the upstream workbook to [ShareSansarScraper commit d5949bd](https://github.com/OmitNomis/ShareSansarScraper/tree/d5949bd628d6b5ca9ebb2b4a15e001a434c6732c), source SHA-256 `dc9534bd1e38a467452196548f82a20b14a1fedc9a2e64983484d9137386c38c`, and describes the price basis as published ShareSansar OHLCV. This is provenance, not proof of independent lineage or redistribution rights.

## Repository and row comparison

| Check | Result |
|---|---:|
| OHLCV CSV files in SMC | 525 |
| OHLCV CSV files in history-starter | 525 |
| Matching filenames | 525/525 |
| Identical Git blob IDs | 500 |
| Different Git blob IDs | 25 |
| Rows in the 25 SMC files | 35,705 |
| Rows in the 25 history files | 22,625 |
| Common symbol/date rows compared numerically | 14,856 |
| Numerically identical common rows | 14,855 |
| Common-date numerical conflict rows | 1 |
| SMC-only symbol/date keys | 20,849 |
| History-only symbol/date keys | 7,769 |
| Duplicate dates in either side of these 25 files | 0 |

The comparison used the Date key and numeric Open/High/Low/Close/Volume values. Numeric formatting differences (for example `256` versus `256.00`) were normalized numerically. A differing Git blob is not treated as a price conflict by itself.

### Sole numerical difference: RHGCL, 2026-11-19

The raw SMC row is `252.1,259.5,252.1,256.0,4216.0`; the history-starter row is `252.10,259.50,252.10,258.00,9054`.

**This conflict is resolved for the derived view by primary NEPSE evidence.** The preserved official capture at `reference/official_eod_captures/RHGCL_2026-11-19_nepse_eod.json` records security ID 8108, HTTP 200, one page, 347 upstream rows, zero quality flags, Close 258.00 and traded quantity 9,054. Its raw response SHA-256 is `303d92756ffbcaa2e6ab5020c29e1eab1b63ed99797bf024914dbb863cbae183`.

The [derived OHLCV v2 release](https://github.com/jaljala044/nepse-smc-data/blob/derived/ohlcv-v2-official-eod/reference/derived_ohlcv_v2_release_2026-11-26.md) is at commit `4255cc293a347857ac77c04a947beb784203062f`. I fetched its RHGCL file and verified the derived row is `2026-11-19,252.1,259.5,252.1,258.0,9054.0`. The raw SMC file remains unchanged at Close 256.00 / Volume 4,216, as required for source preservation. Do not describe this as an unresolved value choice in the derived v2 dataset.

The older cross-repository snapshot and master archive still say this RHGCL item is unresolved; this addendum supersedes that status for the derived v2 view while preserving the historical raw observation.

The broader v2 release is still **not full-session clean**: its P4.30 audit retains 1,329 unique invalid OHLCV rows and 71,806 adjacent repeated rows across 281 symbols. This single RHGCL correction does not make the full derived dataset production-ready.

## History-side date-label and carry-forward risk

Across the 25 history-starter files:

| Check | Result |
|---|---:|
| Friday/Saturday-dated rows | 6,250 |
| Weekend rows exactly matching the immediately preceding file row's OHLCV | 5,578 (89.25%) |
| Weekend rows exactly matching the immediately following file row's OHLCV | 3,523 |
| All adjacent identical OHLCV row pairs | 7,703 |

These are **suspected calendar-day carry-forward / scrape-date-label records**, not proven synthetic rows. Do not treat them as additional exchange sessions or use them in indicators/backtests until a dated NEPSE session calendar and symbol-specific evidence establish their business dates. P4.42 already documents that the same pinned ShareSansarScraper lineage can label stale OHLCV with the scrape date rather than the underlying NEPSE business date for NMLBBL/SMPDA; see [P4.42 source-date lineage report](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/p442_sharesansar_date_lineage_report_2026-11-26.md).

## Importer quarantine evidence

The pinned history-starter import manifest records 303,438 source rows, 301,632 imported rows, 1,806 flagged rows, and zero identical duplicates. Of those flagged rows, **17 belong to these 25 symbols** (MERO 3, UAIL 4, API 1, RAWA 2, KEF 1, SPDL 1, BGWT 1, HRL 1, KDBY 1, RADHI 1, UNHPL 1). All 17 are flagged as `OHLC prices outside a positive high–low range` in `historical_imports/sharesansar_2026-11-20_flagged_rows.csv`, dated 2026-04-24 through 2026-04-29. Keep these in the existing quarantine artifact; do not repair by guessing.

## Disposition

- **Verified:** 525/525 filenames in both repositories; 500 identical blobs; 25 differing blobs; 25/25 pairs parsed; zero duplicate dates in these 25 files; 14,856 common date rows numerically compared; one numerical mismatch identified.
- **Resolved for derived v2:** RHGCL 2026-11-19 uses official NEPSE Close 258.00 and Volume 9,054 in the versioned derived v2 branch; the raw SMC row remains preserved.
- **Partial / unverified:** 20,849 SMC-only and 7,769 history-only symbol/date keys have not been reconciled to the full official session calendar. History-side weekend/carry-forward rows remain suspect pending date-lineage checks.
- **Quarantined:** the 17 selected invalid-OHLC source observations remain in the history import's flagged-row artifact.
- **Not established:** membership of these 25 symbols in the target 281 active equities / 47 mutual funds. The 525-file inventory is not the approved universe. No non-convertible debenture, suspended, or delisted classification is inferred here.
- **Not accessed:** the user's >1-GB Google Drive ZIP and the candidate 763-MB floorsheet archive. No content from either was read or imported.
- **No training, scanner, backtest, or trading-signal eligibility was changed.** No live-data credentials, broker identities, or independent source access were assumed.

## Exact checks performed

1. Fetched the recursive Git trees for both pinned repository commits; compared the 525 OHLCV filenames and Git blob IDs.
2. Fetched both sides of all 25 different-hash CSV pairs (50 files); parsed Date/Open/High/Low/Close/Volume; compared numeric values by common date; counted date keys unique to each side and duplicate dates.
3. Fetched the history-starter ShareSansar import manifest and its flagged-row CSV; checked the 25 per-symbol manifest row counts and isolated the 17 selected flagged observations.
4. Fetched the official RHGCL EOD extraction record and the versioned derived-v2 RHGCL CSV row; verified the derived row matches the official extraction while the raw SMC row is unchanged.
5. No CI suite was run: this was a read-only audit/report task, not an application-code change. No raw CSV was edited or copied.

## Next bounded task

Build a **symbol/date quarantine matrix** for the 7,769 history-only keys, starting with the 6,250 Friday/Saturday rows and 5,578 weekend carry-forward candidates. Match only against verified NEPSE session evidence; use per-security floorsheets where needed. In parallel, preserve the 17 invalid source observations and reconcile the dated 2026-04-24 to 2026-04-29 anomalies. The 281 + 47 active instrument roster remains a separate primary-source gate.
