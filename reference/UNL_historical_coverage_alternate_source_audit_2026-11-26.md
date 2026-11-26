# UNL Historical Coverage and Alternate-Source Audit — 2026-11-26

## Executive finding

The current project archive for UNL begins 2024-03-05 and ends 2026-11-20 (845 data rows). An alternate public repository contains a longer UNL CSV beginning 2011-03-28 and ending 2026-11-26 (2,018 rows). It is a useful candidate source for historical research, but **must not be merged or promoted**: the alternate file has severe OHLC validation failures, and its 2024+ shared records match the project archive numerically but the source lineage is not independently established.

## Sources inspected

1. Project archive:
   - Repository: https://github.com/jaljala044/nepse-history-starter
   - File: `03_stock_charts_ohlcv/UNL_OHLCV.csv`
   - Current observed rows: 845
   - First/last dates: 2024-03-05 to 2026-11-20
   - README describes a manual, user-reviewed import workflow requiring publisher/source URL and hashes in `historical_imports/`; no source record for this UNL file was established in this audit.
2. Alternate public dataset:
   - Repository: https://github.com/binayabaral/nepal-market-data
   - File: `data/nepse/UNL.csv`
   - CSV schema includes published_date, OHLC, per_change, traded_quantity, traded_amount and status.
   - README says daily data is collected from ShareSansar and historical backfill is performed from that source; repository claims MIT licensing for its project/data. That claim does not independently prove rights to republish source-originated exchange data.
   - Current observed rows: 2,018; first/last dates 2011-03-28 to 2026-11-26.
   - 1,467 rows are earlier than 2024-03-05, spanning 2011-03-28 through 2024-03-03.
3. Secondary historical chart:
   - https://nepsedata.com/stock/UNL/
   - Monthly performance heatmap displays history from 2012-01-03; it is evidence that earlier price history is represented by a third party, not a daily OHLCV source suitable for ingestion.

## Numeric overlap comparison

Compared shared dates using numeric values for Open, High, Low, Close and Volume (mapping alternate `traded_quantity` to Volume):

| Metric | Result |
|---|---:|
| Project archive rows | 845 |
| Alternate dataset rows | 2,018 |
| Shared dates | 545 |
| Exact numeric OHLCV matches on shared dates | 545 / 545 |
| Shared-date mismatches | 0 |
| Project dates absent from alternate file | 300 |
| Alternate dates absent from project file | 1,473 |

The 545/545 exact numeric match demonstrates consistency on overlapping dates, not independent source corroboration. The two datasets may share the same upstream ShareSansar data lineage. The 300 project-only dates and 1,473 alternate-only dates must not be interpreted as missing executions without a symbol-specific session/trade calendar.

## Critical quality finding — alternate OHLC validation

Applied the invariant `High >= max(Open, Low, Close)`, `Low <= min(Open, High, Close)`, finite numeric fields and positive traded quantity:

- 362 of 2,018 alternate rows fail at least one validation rule.
- 361 of the 1,467 pre-2024 rows fail.
- The dominant defect is `Open > High` while High/Low/Close are equal or otherwise below Open. Examples begin on 2011-03-28 (Open 6,000; High 5,880; Low 5,880; Close 5,880) and 2011-03-29 (Open 5,880; High 5,763; Low 5,763; Close 5,763).
- This may reflect a systematic field-mapping or source-record issue, but the cause is not established. Do not repair by swapping fields, carrying values forward, or inferring corrected OHLC.

## Disposition

**Historical source discovered; ingestion rejected pending source-level correction and independent verification.**

- Preserve the alternate CSV as an external candidate reference only; do not copy it into canonical data or training.
- Do not splice it into the existing 2024+ archive despite exact overlap matches.
- Request or obtain an independently documented historical export with valid OHLC invariants, source timestamps/provenance, and permission for project use.
- Reconcile a sample of 2011–2024 rows against another independent source or exchange record before considering any backfill.
- Keep UNL flagged as historical coverage incomplete. Current scanner eligibility may use only validated current-period data, subject to all other release gates; historical backtests spanning before 2024 remain blocked.

## Reproducibility

Observed source URLs:
- https://raw.githubusercontent.com/jaljala044/nepse-history-starter/main/03_stock_charts_ohlcv/UNL_OHLCV.csv
- https://raw.githubusercontent.com/binayabaral/nepal-market-data/main/data/nepse/UNL.csv
- https://raw.githubusercontent.com/binayabaral/nepal-market-data/main/README.md

No raw source file was modified. No rows were inserted, removed, adjusted or synthesized. This report records a point-in-time audit as of 2026-11-26; the public alternate file is daily-updated and may change.
