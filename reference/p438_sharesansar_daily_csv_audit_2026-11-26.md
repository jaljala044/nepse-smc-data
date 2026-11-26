# P4.38 — ShareSansar full-market daily CSV triangulation

**Audit date:** 2026-11-26  
**CI run:** https://github.com/jaljala044/nepse-smc-data/actions/runs/45880171127  
**Pinned provider repository:** https://github.com/OmitNomis/ShareSansarScraper  
**Pinned source commit:** `524442d518d2f2705ade0680c9d2e3f90738e3d6`

## Source provenance

The pinned ShareSansarScraper README states that a Scrapy spider captures the ShareSansar “today's share price” table on trading days, writes one CSV per day, and skips a day when the market was closed (to avoid duplicate prior-session tables). It also states the archive begins in March 2024.

This is a secondary provider archive sourced from ShareSansar's published daily market table. It is not a direct NEPSE primary record. The README and all four CSV files were downloaded from the pinned upstream commit. Their byte counts and Git blob SHA-1 values match the pinned repository tree; SHA-256 values are preserved in `capture_report.json`.

## Four exact-date daily tables

| Date | Market-table rows | Unique symbols | Duplicate symbols | Sequence check | Target symbol | Target rows |
|---|---:|---:|---:|---|---|---:|
| 2024-05-16 | 315 | 315 | 0 | Pass | NMLBBL | 0 |
| 2024-05-19 | 323 | 323 | 0 | Pass | NMLBBL | 1 |
| 2024-08-14 | 332 | 332 | 0 | Pass | SMPDA | 0 |
| 2024-08-18 | 330 | 330 | 0 | Pass | SMPDA | 1 |

The prior-date CSVs are not empty: they contain 315 and 332 other market rows respectively. Their source archive files exist on dates that the pinned README's scraper policy treats as trading sessions, and neither target symbol appears in its prior-date market table.

This is stronger than a missing row in a per-symbol history file, but remains secondary-provider evidence.

## Candidate-day parity against floorsheet and canonical snapshot

| Field | NMLBBL · 2024-05-19 | SMPDA · 2024-08-18 |
|---|---:|---:|
| Open | 599.60 | 1,078.10 |
| High | 646.60 | 1,162.70 |
| Low | 599.60 | 1,078.10 |
| Close | 646.60 | 1,162.70 |
| Volume | 864 | 5,314 |
| Turnover (NPR) | 557,461.60 | 6,175,193.80 |
| ShareSansar transaction count | 15 | 192 |
| P4.33 floorsheet rows | 15 | 192 |
| P4.33 floorsheet shares | 864 | 5,314 |
| Candidate OHLCV volume | 864 | 5,314 |

All candidate OHLC, volume, turnover, and transaction-count fields match the P4.33 third-party floorsheet reconstruction and the existing canonical daily OHLCV snapshot.

### SMPDA contract-number caveat

The P4.33 floorsheet archive has 192 SMPDA rows and 192 unique row IDs, but only 177 distinct `contract_no` values (15 excess repeated occurrences). The ShareSansar daily table independently reports 192 transactions and the exact same total shares and turnover.

This aggregate parity supports the 192-row transaction count, but it does not explain the `contract_no` field semantics. Do not claim that `contract_no` is a unique contract key until its schema is independently established.

## Per-symbol history index consistency

The same pinned archive publishes derived per-symbol history JSON generated from the daily CSVs:
- NMLBBL: 863 rows; first date 2024-05-19; last date 2026-11-25.
- SMPDA: 772 rows; first date 2024-08-18; last date 2026-11-25.

Both first dates match the candidate dates. These history JSON files are derived from the daily CSV archive, so they are an internal consistency check, not an independent provider.

## Evidence classification

| Claim | Evidence | Confidence |
|---|---|---|
| Candidate-day OHLCV values | ShareSansar daily CSV, P4.33 floorsheet archive, canonical snapshot | High secondary corroboration |
| Candidate-day share volume and turnover | Exact cross-source totals | High secondary corroboration |
| Candidate-day transaction count | ShareSansar `Trans.` equals P4.33 target row count | High secondary corroboration |
| Target absent on prior session | Target absent in a non-empty full-market daily CSV; scraper says closed days are skipped | Medium secondary corroboration |
| Primary NEPSE first-trade proof | Historical official floorsheet/EOD APIs rejected or did not return 2024 data | Not established |

## Disposition

- NMLBBL first-trade candidate: **2024-05-19 — secondary-source corroborated**.
- SMPDA first-trade candidate: **2024-08-18 — secondary-source corroborated**.
- Prior sessions: NMLBBL 2024-05-16 and SMPDA 2024-08-14 have no target row in both the P4.33 third-party floorsheet archive and the pinned ShareSansar daily market tables.
- Primary-source confirmation remains unavailable. Keep lifecycle `valid_from` **UNKNOWN**; do not convert the secondary no-row evidence into a primary `NO_TRADE` assertion.
- No canonical OHLCV, lifecycle dates, trading-calendar states, training labels, or scanner scores were changed.

## Reproducibility

- Capture script: `tools/capture_p438_sharesansar_daily_csv.py`
- Regression tests: `tools/tests/test_capture_p438_sharesansar_daily_csv.py`
- Workflow: `.github/workflows/p438-sharesansar-daily-crosscheck.yml`
- Raw source files, derived history indexes, SHA-256 checksums, Git blob SHA-1 values, and structured results are preserved under `reference/p438_sharesansar_daily_csv/`.

## Next priority — P4.39

Attempt one more independent provider cross-check (Merolagani or NepseAlpha) for the same four dates, prioritizing exact daily OHLCV and transaction counts. If the provider's historical data cannot be retrieved reliably, document the limitation and close the secondary triangulation with the current two-source corroboration while retaining primary UNKNOWN.
