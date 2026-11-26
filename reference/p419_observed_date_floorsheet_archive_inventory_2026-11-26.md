# P4.19 — observed-date floorsheet archive inventory

**Audit date:** 2026-11-26

## Result

A pinned Git-tree inventory of `socrateai-official/nepse-open-data` was compared against all dates classified `verified_open_observed` in the project's current canonical date file.

- Positive-observation dates checked: **226**
- Matching daily floorsheet paths found: **226**
- Missing archive paths: **0**
- Source repository: `socrateai-official/nepse-open-data`
- Source commit pinned in the manifest: `70324524df83eaa7c2964441ad4026d6ab00cc7e`
- Date range: 2025-11-25 through 2026-11-20

The manifest is `reference/p419_observed_date_floorsheet_archive_inventory_2026-11-26.csv`. Each row records the observed date, calendar evidence scope, source repository and commit, exact path, Git blob object ID and file size.

## Important interpretation

This is a **repository file-presence inventory**, not a content-validation or completeness result.

- Git blob IDs are Git object identifiers, not SHA-256 hashes of downloaded file bytes.
- A file existing in a public repository does not prove it contains every contract from the NEPSE session.
- For 225 dates, the positive-open evidence is scoped to security ID 8108. It establishes that the market traded, not that all 281 equities were eligible or expected to trade.
- 2026-11-20 has additional independent full-pagination capture and exact Parquet/CSV contract-multiset parity, but its raw bronze page payloads were not archived.
- No absence from a daily candidate file may be used to label an equity `NO_TRADE` until that date's full-session completeness and totals are independently verified.

## Next validation stage

Download each pinned daily file, preserve its raw SHA-256 and retrieval metadata, validate schema, contract ID uniqueness, date consistency, positive quantities/rates, amount identities and market totals. Seek independent source/capture evidence before using missing symbol rows as no-trade evidence.
