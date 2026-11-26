# P4.33 — NMLBBL and SMPDA first-trade floorsheet reconstruction

**Audit date:** 2026-11-26  
**Evidence branch:** `p433-first-trade-floorsheet-capture`  
**Capture workflow:** https://github.com/jaljala044/nepse-smc-data/actions/runs/45875627906  
**Source-tree capture:** `reference/p433_floorsheets/huggingface_repo_tree.json`

## Objective

Test candidate first-positive-volume dates against immediately preceding candidate NEPSE sessions:

| Symbol | Candidate date | Prior session checked |
|---|---|---|
| NMLBBL | 2024-05-19 | 2024-05-16 |
| SMPDA | 2024-08-18 | 2024-08-14 |

A candidate-day positive contract plus a complete prior-session floorsheet with no target contracts is necessary evidence for a first-trade boundary. Absence from an incomplete archive is never `NO_TRADE`.

## Source discovery and capture

The Hugging Face dataset repository tree API returned HTTP 200 and 998 file entries. The actual date objects are gzip files (`.csv.gz`); an initial attempt against the uncompressed `.csv` path returned 404. The corrected capture retrieved all four immutable gzip objects.

Each compressed payload SHA-256 matches the LFS SHA-256 declared in the repository tree, and compressed byte counts match the tree metadata.

| Symbol | Date | Compressed bytes | LFS SHA-256 verified | Parsed rows | Target rows | Target shares | Target turnover (NPR) |
|---|---|---:|---|---:|---:|---:|---:|
| NMLBBL | 2024-05-19 | 1,167,345 | Yes | 74,991 | 15 | 864 | 557,461.60 |
| NMLBBL | 2024-05-16 | 903,408 | Yes | 57,218 | 0 | 0 | 0.00 |
| SMPDA | 2024-08-18 | 4,145,349 | Yes | 300,918 | 192 | 5,314 | 6,175,193.80 |
| SMPDA | 2024-08-14 | 3,333,535 | Yes | 244,019 | 0 | 0 | 0.00 |

The immutable compressed source files are preserved under `reference/p433_floorsheets/`; decompression is performed in memory for validation to avoid committing redundant copies. SHA-256 and retrieval details are in `capture_report.json`.

## OHLCV cross-check

The captured target-symbol quantities match the existing OHLCV volumes exactly on both candidate dates:

| Symbol | Date | OHLCV O/H/L/C | OHLCV volume | Floorsheet target shares | Result |
|---|---|---|---:|---:|---|
| NMLBBL | 2024-05-19 | 599.60 / 646.60 / 599.60 / 646.60 | 864 | 864 | Exact volume match |
| SMPDA | 2024-08-18 | 1,078.10 / 1,162.70 / 1,078.10 / 1,162.70 | 5,314 | 5,314 | Exact volume match |

The prior-session archive files contain market-wide rows but zero target-symbol rows. The OHLCV files also have no target rows on those prior dates.

## Contract identity and source-quality caveat

The source schema contains both `contract_no` and `id`. The archive's `id` values are unique row identifiers across the four files, and no exact full-row duplicates were found. However, `contract_no` is reused many times within the same symbol on the two SMPDA dates:
- SMPDA 2024-08-18: 300,918 rows, 30,093 unique `contract_no` values, 142,724 excess repeated values within symbol. The 192 SMPDA target rows themselves contain 177 distinct `contract_no` values (15 excess repeated values), while all 192 archive row `id` values are unique.
- SMPDA 2024-08-14: 244,019 rows, 24,404 unique `contract_no` values, 119,389 excess repeated values within symbol. The target-symbol count is zero.
- NMLBBL files have no repeated `contract_no` values.

This is a major schema/identity anomaly. The row `id` is unique but its semantics as an exchange contract identifier have not been independently established. Do not treat the 192 SMPDA rows as 192 independently verified exchange contracts: only 177 distinct `contract_no` values are present for the target symbol, and the third-party row `id` semantics are not independently established. The target-symbol quantities nevertheless match the corresponding OHLCV volumes exactly.

## What this supports

- The third-party archive contains positive NMLBBL rows on 2024-05-19, totaling 864 shares.
- The third-party archive contains positive SMPDA rows on 2024-08-18, totaling 5,314 shares.
- Both candidate-day share totals exactly match the existing same-date OHLCV volumes.
- The two immediately preceding candidate-session files contain no rows for the respective symbols.
- All four compressed files pass byte-count and LFS SHA-256 checks against the Hugging Face repository tree.
- Date fields and quantity/rate/amount arithmetic passed the implemented checks. Contract identity remains unresolved for the SMPDA source files.

## What this does not prove

The source is a third-party dataset that describes itself as NEPSE floorsheet data. It is not a direct NEPSE primary-source capture. The dataset card currently reports a dataset-generation parsing error for a malformed contract-number value. The repository tree and LFS hashes prove which third-party objects were downloaded, not that every exchange contract was captured.

No upstream NEPSE `totalElements`, page count, complete-pagination receipt, official session totals, or independently verified complete-session control total was retrieved for these four dates. Thus zero target rows on the prior dates cannot establish that the securities had no trades.

## Lifecycle disposition

| Symbol | Candidate first trade | Prior-date result in third-party archive | Lifecycle `valid_from` |
|---|---|---|---|
| NMLBBL | 2024-05-19 (positive rows; OHLCV volume matches) | 2024-05-16 has zero target rows | **UNKNOWN — primary/full-session completeness pending** |
| SMPDA | 2024-08-18 (positive rows; OHLCV volume matches) | 2024-08-14 has zero target rows | **UNKNOWN — primary/full-session completeness pending** |

Do not promote either lifecycle date yet. Do not label the prior dates `NO_TRADE` from this archive alone. No canonical OHLCV, lifecycle `valid_from`, calendar status, training label, or scanner score was changed.

## Next evidence requirement

Obtain official NEPSE date-specific floorsheets or an independently controlled complete-session capture for all four dates, including upstream pagination totals and full-page retrieval logs. Reconcile official contract rows to these third-party files and same-date OHLCV totals. Investigate the SMPDA `contract_no` repetition against the original source schema. Only then can either first-trade boundary be promoted.

## Reproducibility

- Capture code: `tools/capture_p433_first_trade_floorsheets.py`
- Repository-tree discovery: `tools/discover_p433_hf_dataset_objects.py`
- Regression tests: `tools/tests/test_capture_p433_first_trade_floorsheets.py`
- Workflow: `.github/workflows/p433-first-trade-floorsheet-capture.yml`
- Captured compressed and decompressed source files plus the report are committed in this branch.
