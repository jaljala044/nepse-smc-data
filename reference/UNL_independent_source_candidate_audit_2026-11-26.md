# UNL independent-source candidate audit — 2026-11-26

## Decision

UNL remains **QUARANTINED** for historical indicators, backtests, model training and signal generation. This investigation found a useful older candidate archive with apparent source lineage distinct from the ShareSansar-derived archive, but it is not a complete OHLCV series and has unresolved field discrepancies. No data was ingested into canonical storage and no raw project data was changed.

## Candidate A — Saroj Rana NEPSE archive

- Repository: https://github.com/sarojrana/nepse-data
- File: https://github.com/sarojrana/nepse-data/blob/main/data/UNL_2000-01-01_2021-12-31.csv
- Raw file: https://raw.githubusercontent.com/sarojrana/nepse-data/main/data/UNL_2000-01-01_2021-12-31.csv
- Git blob SHA: `b3f80b16215dd12a20fd9236a2ece171bd16f1d2`
- File size: 61,887 bytes
- Repository README describes the collection as NEPSE trading data and links the NEPSE stockwise-prices page as its source. This is a maintainer-declared provenance statement, not an independently audited capture chain.
- Schema: serial number, date, transaction count, traded shares, traded amount, maximum price, minimum price, close price. **There is no open-price field.** Therefore it cannot independently supply complete OHLCV.
- Retrieved rows: 1,029
- Date range: 2010-05-18 through 2021-12-29
- Date keys: unique in the parsed file
- Date order: newest first
- Licence: repository has no declared licence; redistribution/ingestion rights remain unverified.

### Reconciliation against srijankarki07 UNL archive

The newer archive is ShareSansar-lineage according to its project documentation. The Saroj Rana README instead points to NEPSE's stockwise-price page. These are **apparently different source lineages**, but the provenance of the older capture has not been independently proven.

Comparison was performed on shared date keys, using:
- Saroj `Max. Price` vs newer `high`
- Saroj `Min. Price` vs newer `low`
- Saroj `Close Price` vs newer `close`
- Saroj `Total Traded Shares` vs newer `volume`
- Saroj `Total Traded Amount` vs newer `turnover`

Results:
- Shared dates: 998
- Saroj-only dates: 31
- Newer-archive-only dates: 1,018
- Exact field matches across all five comparable fields: 968 / 998
- High matches: 977 / 998
- Low matches: 987 / 998
- Close matches: 992 / 998
- Volume matches: 998 / 998
- Turnover matches: 997 / 998

The 30 non-identical overlap rows are not silently reconciled. Most discrepancies are in max/min prices; six have close-price disagreement, and one has a turnover disagreement. Examples include:
- 2018-08-08 and 2018-06-24: Saroj price fields are zero despite non-zero traded shares and amount.
- 2018-01-23: Saroj max/min/close fields are zero despite 848 traded shares and non-zero traded amount.
- 2019-09-17: Saroj max/min/close all differ from the newer archive.
- 2014-06-18 and 2014-06-17: close-price discrepancies.

The 31 Saroj-only dates are not proof of missing executed sessions in the newer archive. They are candidate records for follow-up, not automatic additions. They include 27 dates before 2011-03-28 and four later dates (2011-06-20, 2013-03-03, 2016-09-04 and 2019-06-27).

### What this source can and cannot support

Potential use after further validation:
- corroborating historical transaction count, traded shares, traded amount, high, low and close on selected dates;
- identifying candidate historical dates absent from the newer archive;
- supporting a source-discrepancy queue.

Not permitted:
- deriving open from a previous close or any other field;
- treating the 31 unique dates as confirmed exchange sessions without a primary calendar/floorsheet check;
- choosing one side of a disagreement without primary evidence;
- splicing this data into the existing series;
- promoting it to OHLCV, indicators, training or backtests.

## Candidate B — Hugging Face AnkitSanjyal/nepse-market-data

- Dataset: https://huggingface.co/datasets/AnkitSanjyal/nepse-market-data
- Published dataset description reports `eod_history_ext` at symbol-by-day grain, 1995-07-20 to present, with ShareSansar as the source.
- The same description distinguishes a richer `eod_price` table sourced from NEPSE but only for a rolling 365-day window, and NEPSE floorsheet contracts from 2026-08-19 onward with a stated gap from 2026-08-26 to 2026-11-18.
- The long-history table is therefore **not independent corroboration** of the existing ShareSansar-lineage archive. The short rolling official EOD and floorsheet tables may help validate recent sessions, but they cannot resolve the pre-2024 history.
- No UNL-specific Parquet partition was retrieved or validated in this investigation. Do not ingest based solely on the dataset landing-page description.

## Candidate C — NEPSE Analysis

- UNL chart: https://nepseanalysis.com/chart/UNL
- Public chart description says its settled daily bars reach back to 2012 and identifies them as NEPSE settled daily bars.
- The site's general source statement says prices, indices and corporate actions come from NEPSE and other public market-data sources. This does not, by itself, prove the complete per-symbol chart series is directly sourced from NEPSE.
- No downloadable raw UNL series or machine-readable source payload was captured here. Treat as a **reconciliation target**, not an acquired dataset.

## Candidate D — NEPSEData

- UNL page: https://nepsedata.com/stock/UNL/
- Public page exposes a monthly return heatmap from 2012-01-03 through 2026-11-26, but this is not daily OHLCV. The page's visible heatmap cannot validate daily opens, highs, lows, volumes or exact session dates.
- No full daily raw series was acquired. Candidate remains unvalidated for OHLCV recovery.

## Candidate E — Merolagani

- UNL company page: https://www.merolagani.com/CompanyDetail.aspx?symbol=UNL
- Public company page exposes company statistics and navigation to price history/floorsheet. The public datewise floorsheet page exposes executed contracts for a selected date, but a complete UNL historical extraction was not obtained.
- It remains a possible source for spot checks of selected recent and historical sessions, subject to access, coverage and capture validation. A company profile or recent quote is not a historical OHLCV archive.

## Recovery disposition and next gates

| Gate | Status |
|---|---|
| Locate free alternative historical sources | Complete (candidate discovery) |
| Retrieve another older UNL archive | Complete (Saroj file retrieved for analysis) |
| Verify date uniqueness in Saroj file | Passed (1,029 unique date keys) |
| Confirm complete OHLCV schema | Failed — open is absent |
| Cross-source comparable-field reconciliation | Partial — 998 overlaps, 968 exact across five comparable fields |
| Resolve 30 field-discrepant overlap rows | Pending primary evidence |
| Validate 31 Saroj-only dates as executed sessions | Pending |
| Independent floorsheet verification | Pending |
| Corporate-action / adjusted-price validation | Pending |
| Rights/licence review | Pending |
| Canonical database promotion | Blocked |

### Required next actions

1. Acquire primary NEPSE/authorized floorsheet or settled EOD evidence for a stratified sample of Saroj/newer-archive overlap dates, including every disputed date where possible.
2. Verify the 31 Saroj-only dates against the exchange session calendar and executed records before treating them as missing archive coverage.
3. Seek a lawful source that provides the missing open field; do not infer it.
4. Reconcile corporate actions and raw-versus-adjusted price basis before comparing long-run prices.
5. Preserve source payloads, source revision/blob identifiers, retrieval timestamps, hashes and validation outputs before any future ingestion.
6. Keep UNL outside historical backtests/training until all promotion gates pass. This remains a non-blocking exclusion for development on eligible ordinary equities.

## Evidence and method notes

This report records a programmatic CSV comparison of the two public repository files. Numeric comparisons used exact numeric equality after parsing decimal strings as numbers; no rounding tolerance was applied. It is a source-reconciliation result, not proof of exchange execution or data ownership.

The previously committed 2,016-row srijankarki07 archive audit remains applicable: 1,646 preliminary rows passed basic numeric/OHLC/volume plus weekday checks; 370 failed at least one of those checks; 545 dates overlapped the project archive and all 545 matched its OHLCV exactly. Its source identifies ShareSansar lineage, so that match is not independent confirmation.
