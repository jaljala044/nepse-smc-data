# UNL public-source recovery investigation — 2026-11-26

## Executive decision

UNL remains QUARANTINED for full historical OHLCV, historical indicators, backtests and training. ShareHub credentials are not available, so the recovery path is public-source-only.

This investigation adds an important provenance finding: the 2,016-row srijankarki07 UNL archive is explicitly scraped from ShareSansar, not from NEPSE directly. It is therefore not an independent source from other ShareSansar-derived archives. Its current raw file also has 360 basic OHLCV invariant failures on a fresh retrieval.

No raw project data was changed, repaired, spliced, deleted or promoted.

## 1. Public source candidates and what they actually prove

### A. srijankarki07/nepse-data — retrieved and inspected
- Raw file: https://raw.githubusercontent.com/srijankarki07/nepse-data/main/data/series/UNL.csv
- Observed rows: 2,016
- Date span: 2011-03-28 to 2026-11-26
- Duplicate date keys: 0
- Basic OHLCV invariant failures on this retrieval: 360
- Consecutive exact-value repeats: 12
- The dominant observed invariant failure is Open > High. Example 2011-03-28: Open 6,000; High 5,880; Low 5,880; Close 5,880; Volume 120.
- Its README explicitly states that the data is scraped from ShareSansar, which republishes NEPSE end-of-day figures; it is not obtained from NEPSE directly.
- README also says ShareSansar permits reading rather than republishing, and acknowledges that publishing the archive is a judgement rather than a settled right.
- Disposition: useful discrepancy/coverage reference only. Not independent corroboration, not canonical, and not eligible for OHLCV ingestion.

The current 360-failure count differs from the earlier 362 count in a prior audit. This is a live repository file and may have changed; retain retrieval date and raw-file hash in any future reproducible capture. Do not silently overwrite historical audit counts.

### B. Saroj Rana archive — partial independent-lineage candidate
- Raw file: https://raw.githubusercontent.com/sarojrana/nepse-data/main/data/UNL_2000-01-01_2021-12-31.csv
- 1,029 rows, 2010-05-18 to 2021-12-29.
- Has transaction count, shares, turnover, max, min and close; it does not have open.
- README points to NEPSE stockwise prices as source, but the original capture chain is not independently proven and no licence is declared.
- Existing comparison found 998 overlapping dates with the ShareSansar-derived series, 968 exact matches across five comparable fields and 30 non-identical rows; 31 Saroj-only dates remain unverified.
- Disposition: retain as a separate corroboration candidate for comparable fields only. Do not infer open, splice, or promote.

### C. Hugging Face AnkitSanjyal/nepse-market-data — authoritative recent-window route
- Dataset page: https://huggingface.co/datasets/AnkitSanjyal/nepse-market-data
- Dataset card distinguishes:
  - eod_price: NEPSE's own end-of-day board, described as authoritative but limited by NEPSE to a rolling 365-day history.
  - floorsheet: NEPSE executed-contract data, described as accumulating from 2026-08-19, with a stated gap from 2026-08-26 through 2026-11-18.
  - eod_history_ext: ShareSansar-derived long history, not independent of ShareSansar.
- The dataset card says the two daily tables are deliberately not merged and reports 75,671 overlapping rows with 100% volume match and 99.98% close match across the market. This is a provider's stated validation, not a UNL-specific result independently reproduced here.
- No UNL-specific authoritative Parquet rows were downloaded or independently validated during this task.
- Disposition: highest-priority public route for recent official EOD and any available floorsheet records. Need acquire the UNL rows and preserve exact partition/revision, retrieval time, hash and schema before promotion.

### D. Current floorsheet aggregations
- NEPSE Quant UNL broker page reports 25 Nov 2026: 310 shares and Rs 1.48 crore; it attributes this to NEPSE floorsheet and provides a 20-session summary.
- NEPSE Quant's 25 Nov floorsheet page shows a UNL contract of 300 shares at Rs 47,800.
- Other public daily quote pages independently display 25 Nov OHLCV: O 47,800; H 47,800; L/C 47,500.10; volume 310.
- These are public secondary renderings of exchange records, not raw signed NEPSE responses captured by this project. They support a targeted cross-check but do not substitute for immutable primary evidence.
- Punji reports 26 Nov close Rs 47,500.10, volume 40. No second UNL-specific 26 Nov daily bar or complete contract-level UNL floorsheet payload was acquired in this task; keep that row unconfirmed pending the authoritative EOD dataset.

## 2. Current-period cross-check

| Session | Public observation | Status |
|---|---|---|
| 25 Nov 2026 | O 47,800; H 47,800; L/C 47,500.10; volume 310; turnover about Rs 1.48 crore; 2 trades | Multi-provider agreement; exchange-origin attribution reported, raw primary payload not captured |
| 26 Nov 2026 | Punji: O/C 47,500.10; H 47,750; L 47,500.10; volume 40 | Single-provider UNL observation in this audit; needs official EOD/floorsheet confirmation |

Do not collapse the two dates into one observation. Do not carry the 25 Nov close forward to 26 Nov as an inferred bar.

## 3. Corporate action: official notice located

Official NEPSE-hosted PDF:
https://www.nepalstock.com/api/nots/security/fetchFiles?fileLocation=rita_listing%2F2026-11-02%2FUnilever+Nepal+Limited+Dividend+Declaration+2026_1793590006438.pdf

The notice is dated 30 October 2026 and states:
- Recommended cash dividend: NPR 1,540 per equity share.
- Book closure wording: 9th to 23rd Mangsir 2083, stated in the notice as 25 November to 9 December 2026.
- It is a cash dividend, not a bonus issue.

The official company notice is stronger than provider summary labels that show only 25 November. Record the stated period verbatim and obtain the final NEPSE/issuer entitlement notice before deriving the last cum-dividend trading session or applying any total-return adjustment. Do not mechanically rewrite raw prices. Cash dividends are not a bonus-share ratio and must not be treated as share-count changes.

## 4. Session-date and repeat issue

The earlier 845-row project archive audit found:
- 226/845 rows on non-session weekdays under the documented Sunday–Thursday regime through 5 April 2026 and Monday–Friday regime from 10 April 2026.
- 302 consecutive rows repeat the preceding row's entire OHLCV values.
- 0 duplicate date keys and 0 basic numeric invariant failures in that project file.

The new long archive's provenance states that ShareSansar sometimes serves the previous day's table under the requested date, and its scraper rejects such responses by comparing table contents. This is an important source-level warning and makes direct row/date reconciliation essential. It does not prove that every repeated row in the project archive is false or that every flagged weekday is invalid.

No date may be shifted, removed or inserted based solely on weekday or repeated-price logic. Validate against actual NEPSE EOD session dates and executed contracts where available.

## 5. Public-only recovery plan

1. Retrieve UNL eod_price rows from the Hugging Face dataset's NEPSE-authoritative rolling-365-day partition, including the full schema and dataset revision.
2. Retrieve all available UNL floorsheet contracts from the official-source partition. Explicitly record the documented gap 2026-08-26 to 2026-11-18; never interpret missing floorsheet rows in that interval as zero trades.
3. Reconcile 25 and 26 Nov 2026 UNL daily bars to the authoritative EOD rows and aggregate contracts independently (sum quantity and amount; derive min/max/weighted average; compare close only under the documented exchange close definition).
4. Use public Saroj archive only to corroborate max/min/close/volume/turnover for 2010–2021; obtain open from another valid source or leave it unavailable.
5. Create a row-level exception ledger for the 30 overlapping disagreements and 31 Saroj-only dates; resolve only against official EOD/floorsheet/session evidence.
6. Reconcile 226 suspicious project archive dates and 302 repeated rows against the exchange-authoritative recent dataset wherever coverage overlaps. For older dates, seek archived NEPSE or issuer/exchange records; where no primary evidence exists, keep the row quarantined.
7. Validate all corporate actions and raw/adjusted price semantics; keep raw source rows immutable.
8. Complete rights/provenance review before any storage or redistribution of third-party data.
9. Promote in two gates: (a) recent validated current-period UNL bars, (b) independently validated long historical series. Passing gate (a) does not pass gate (b).

## 6. Final disposition

- ShareHub API: not available; no longer a dependency for this recovery path.
- srijankarki07 long archive: REJECT for canonical ingestion; ShareSansar lineage and current OHLCV invariant failures.
- Saroj archive: PARTIAL CORROBORATION candidate; no open field, 30 discrepancies, 31 unique dates, licence/provenance unresolved.
- Hugging Face NEPSE-authoritative EOD/floorsheet: PRIORITY acquisition target; UNL-specific data not yet acquired in this task.
- 25 Nov 2026 bar: multi-provider corroborated secondary observation; raw authoritative capture pending.
- 26 Nov 2026 bar: Punji-only observation in this task; authoritative confirmation pending.
- Corporate action: official issuer notice hosted on NEPSE located; final entitlement/session interpretation pending.
- UNL full historical OHLCV: QUARANTINE / LOW CONFIDENCE.
- No raw data modified, no historical splicing, no synthetic rows, no training/backtest promotion.
