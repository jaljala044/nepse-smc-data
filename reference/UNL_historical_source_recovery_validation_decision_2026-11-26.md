# UNL historical source recovery — validation decision (2026-11-26)

## Decision
**No clean, independently validated historical source is currently eligible for canonical backfill.** Two public candidate archives were retrieved and compared with the project's current UNL file. Both provide longer date coverage, but each fails critical acceptance conditions. No rows were imported, rewritten, repaired, or spliced.

## Project baseline
- Repository: https://github.com/jaljala044/nepse-history-starter
- File: `03_stock_charts_ohlcv/UNL_OHLCV.csv`
- Rows: 845; span: 2024-03-05 to 2026-11-20
- Source blob SHA: `107d1ef058992cfd1b8b4a88db9f6304edf22932`

## Candidate A — srijankarki07/nepse-data
- File: https://github.com/srijankarki07/nepse-data/blob/main/data/series/UNL.csv
- Rows: 2016; span: 2011-03-28 to 2026-11-26
- Source blob SHA: `83b1eb2c1af38f4661d14c6dd0a3f30c863e5d54`
- Shared dates with project baseline: 545
- Exact numeric OHLCV matches on shared dates: 545/545
- Candidate-only dates: 1471
- Project-only dates: 300
- Basic OHLC/volume invalid rows: 360
- Example invalid rows: 2011-03-28 O=6000 H=5880 L=5880 C=5880 V=120; 2011-03-29 O=5880 H=5763 L=5763 C=5763 V=60; 2011-04-04 O=5763 H=5648 L=5648 C=5648 V=100
- Dominant defect: Open exceeds High, which violates the OHLC envelope. Do not swap fields or infer corrections.

## Candidate B — binayabaral/nepal-market-data
- File: https://github.com/binayabaral/nepal-market-data/blob/main/data/nepse/UNL.csv
- Rows: 2,018; span: 2011-03-28 to 2026-11-26
- Prior audit recorded 362 OHLC validation failures, including pre-2024 failures. Its 545 overlapping project dates matched numerically, but shared upstream lineage is not excluded; this is consistency, not independent corroboration.
- Repository README describes ShareSansar collection/backfill. This does not establish independent provenance from Candidate A or the exchange.

## Acceptance criteria not met
1. Valid OHLC envelope for every accepted row.
2. Independently documented source lineage and point-in-time provenance.
3. Session-date reconciliation against actual NEPSE sessions/trades.
4. Rights/terms for project storage and use established.
5. Independent validation of a sample of historical dates against exchange/floorsheet or another genuinely independent provider.

## Safe disposition
- Preserve both candidates as external, read-only evidence.
- Keep UNL historical backfill quarantined; do not use these candidate rows for historical indicators, backtests or model training.
- Existing project baseline remains unchanged; its separate session-date contamination audit remains in force.
- Request an authorized provider export (e.g. licensed ShareHub ALL-history endpoint) through the project owner's procurement/account process. Public endpoint documentation is not a data response; no credentials were available here.
- If an authorized export is obtained, validate raw schema, timestamps, corporate actions, OHLC envelope, volume/turnover arithmetic, session dates and overlap before proposing a reviewed import.

## Reproducibility
This report is a read-only point-in-time comparison on 2026-11-26. Candidate CSVs are mutable public GitHub files; the blob SHAs above identify the exact retrieved versions. No raw project data was modified.
