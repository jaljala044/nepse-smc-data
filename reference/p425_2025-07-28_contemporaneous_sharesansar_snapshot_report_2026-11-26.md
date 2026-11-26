# P4.25 — contemporaneous ShareSansar snapshot cross-check (2025-07-28)

Date: 2026-11-26  
Scope: all 86 rows in the 2025-07-28 close-conflict matrix  
Status: secondary-source lineage clarified; no official NEPSE historical record available

## Key finding

A contemporaneous ShareSansar daily-page snapshot was recovered from the OmitNomis scraper archive. It was committed on the same trading date, 2025-07-28T11:33:19Z, by that repository's scheduled scraper. Across all 86 disputed symbols:

- The contemporaneous snapshot Close matches the SMC raw Close in **86/86** rows.
- The contemporaneous snapshot Close matches the later srijankarki backfill Close in **0/86** rows.
- Open, High, Low and Volume match across all three records in **86/86** rows.
- Turnover is retained in the contemporaneous source file; the row-level comparison CSV preserves it.

This indicates the difference is between two ShareSansar capture paths/timepoints, not a broad OHLCV or volume mismatch.

## Source lineage

### Contemporaneous daily-page snapshot

- Repository: OmitNomis/ShareSansarScraper
- File: docs/Data/2025_07_28.csv
- File blob SHA: 28b5edf90ea5ebfe7e419c5162eedd0f30a9ce82
- Commit: 44323da56374af6081e0783e3d65e543f3a5ec34
- Commit time: 2025-07-28T11:33:19Z
- Scraper route: GET https://www.sharesansar.com/today-share-price
- Scraper implementation at pinned source commit reads the daily page table and writes the page's displayed cells to CSV.

The SMC historical import manifest separately records its imported baseline as ShareSansar via ShareSansarScraper, with source workbook combined_excel.xlsx, blob SHA dc9534bd1e38a467452196548f82a20b14a1fedc9a2e64983484d9137386c38c, and price basis "Published OHLC and volume from ShareSansar; Close is the source Close field." The 86 SMC raw rows match the dated daily-page snapshot.

### Later dated backfill

- Repository: srijankarki07/nepse-data
- File: data/daily/2025/2025-07-28.csv
- File blob SHA: 329146bbdb0ef66722933f8aba0542c7e4ec78f8
- Backfill commit: 62ee1cd0f00e312629c32409c7324f5d1d227b3a
- Commit time: 2026-10-01T03:59:43Z
- Repository backfill commit: 688d59c03915dcee73ecad4230d2083a41c61764
- Its scraper uses ShareSansar's dated AJAX route: POST https://www.sharesansar.com/ajaxtodayshareprice with a date parameter and CSRF/session token. Its parser maps the exact Close header.

The two paths are not independent market-data providers. They are two ShareSansar routes: the contemporaneous daily page and a later historical AJAX backfill. The dated route's 86 closes differ from the contemporaneous page snapshot, while the other OHLCV fields remain identical.

## Row-level evidence

See [the 86-row three-way comparison](p425_2025-07-28_contemporaneous_sharesansar_snapshot_comparison_2026-11-26.csv). It records SMC raw, contemporaneous daily-page snapshot, later backfill Close, source file hashes, source commits and row-level match flags.

## Decision

- For the derived historical dataset, retain the SMC raw Close values for these 86 dates because they match the same-day ShareSansar daily-page snapshot.
- Do not apply the later AJAX-backfill Close values from the srijankarki archive to these rows.
- Label the rows SECONDARY_CONTEMPORANEOUS_SNAPSHOT_CORROBORATED, not official-NEPSE-verified.
- The 2025-07-28 official NEPSE EOD record remains unavailable through the rolling 365-day endpoint. The values therefore remain third-party ShareSansar evidence, not primary exchange verification.
- Preserve every raw source file unchanged. No cross-symbol rule or numerical adjustment is applied.

## Next priority — P4.26

Apply the same provenance-first approach to the 109 invalid external candidates: identify each symbol/date, raw and external tuples, source endpoint and file hash, then seek contemporaneous evidence. Keep OHLC-invalid values quarantined unless an individual row can be independently validated.
