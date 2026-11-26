# P4.26 — 109 invalid external candidate audit

Date: 2026-11-26  
Scope: the 109 rows in the missing-equity recovery queue classified QUARANTINE_INVALID_EXTERNAL_OHLCV.  
Status: contemporaneous secondary snapshot comparison complete; no row promoted or repaired.

## Findings

- Recovery queue: 109 candidates across four verified-open sessions.
- By date: 2026-04-24: 15; 2026-04-27: 18; 2026-04-28: 21; 2026-04-29: 55.
- Invalidity: 88 OPEN_ABOVE_HIGH and 21 OPEN_BELOW_LOW, matching the existing queue audit; no high<low or close-outside-range cases in this 109-row subset.
- All 109 rows were found in the same-day ShareSansar daily-page snapshot.
- The snapshot OHLCV tuple matches the invalid external tuple in 109/109 rows.
- Therefore the inconsistency is present in the contemporaneous ShareSansar display snapshot itself; it is not introduced only by the later dated-AJAX backfill parser.

## Source provenance

- Later dated archive: srijankarki07/nepse-data, commit 688d59c03915dcee73ecad4230d2083a41c61764, daily files data/daily/2026/2026-04-24.csv, 2026-04-27.csv, 2026-04-28.csv, 2026-04-29.csv.
- Contemporaneous daily-page archive: OmitNomis/ShareSansarScraper, commit d5949bd628d6b5ca9ebb2b4a15e001a434c6732c, docs/Data/2026_04_24.csv, 2026_04_27.csv, 2026_04_28.csv, 2026_04_29.csv.
- The two sources are both ShareSansar capture paths, not independent market-data providers. Exact file blob hashes are included per row in the matrix.

## Decision

- Keep all 109 rows quarantined as `UNKNOWN_INVALID_OHLCV_SOURCE_CORROBORATED`.
- Do not repair Open/High/Low or infer which field is wrong. The same-day secondary snapshot reproduces the invalid tuple, but cannot establish the correct exchange OHLC.
- No raw source values changed; zero rows inserted; no scanner/training promotion.
- A complete official NEPSE EOD payload or a complete, date-matched floorsheet plus independently validated OHLC reconstruction is required for row-level resolution.

## Next priority — P4.27

Trace the 88 OPEN_ABOVE_HIGH and 21 OPEN_BELOW_LOW cases to original NEPSE trade/floorsheet records. Group by symbol and exact date; where complete official evidence cannot be obtained, preserve UNKNOWN. Also review the 490 date-shift recoveries against the exact exchange calendar and capture timestamps before any canonical promotion.
