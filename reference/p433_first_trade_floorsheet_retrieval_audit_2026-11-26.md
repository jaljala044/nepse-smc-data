# P4.33 — NMLBBL and SMPDA first-trade floorsheet reconstruction

**Audit date:** 2026-11-26  
**Evidence branch:** `p433-first-trade-floorsheet-capture`  
**Capture workflow:** https://github.com/jaljala044/nepse-smc-data/actions/runs/45875627906  
**Source-tree capture:** `reference/p433_floorsheets/huggingface_repo_tree.json`

## Objective

Test the candidate first-positive-volume dates against the immediately preceding candidate NEPSE sessions:

| Symbol | Candidate date | Prior session checked |
|---|---|---|
| NMLBBL | 2024-05-19 | 2024-05-16 |
| SMPDA | 2024-08-18 | 2024-08-14 |

A candidate-day positive contract plus a complete prior-session floorsheet with no target contracts is necessary evidence for a first-trade boundary. Absence from an incomplete archive is never `NO_TRADE`.

## Source discovery and capture

The Hugging Face dataset repository tree API returned HTTP 200 and 998 file entries. The actual date objects are gzip files (`.csv.gz`); the earlier first attempt against the uncompressed `.csv` path returned 404. The corrected capture retrieved all four immutable gzip objects.

Each compressed payload SHA-256 matches the LFS SHA-256 declared in the repository tree, and compressed byte counts match the tree metadata.

| Symbol | Date | Compressed bytes | LFS SHA-256 verified | Parsed rows | Target rows | Target shares | Target turnover (NPR) |
|---|---|---:|---|---:|---:|---:|---:|
| NMLBBL | 2024-05-19 | 1,167,345 | Yes | 74,991 | 15 | 864 | 557,461.60 |
| NMLBBL | 2024-05-16 | 903,408 | Yes | 57,218 | 0 | 0 | 0.00 |
| SMPDA | 2024-08-18 | 4,145,349 | Yes | 300,918 | 192 | 5,314 | 6,175,193.80 |
| SMPDA | 2024-08-14 | 3,333,535 | Yes | 244,019 | 0 | 0 | 0.00 |

Raw compressed files and decompressed CSVs are preserved under `reference/p433_floorsheets/`, with SHA-256 and retrieval details in `capture_report.json`.

## OHLCV cross-check

The captured target-symbol quantities match the existing OHLCV volumes exactly on both candidate dates:

| Symbol | Date | OHLCV O/H/L/C | OHLCV volume | Floorsheet target shares | Result |
|---|---|---|---:|---:|---|
| NMLBBL | 2024-05-19 | 599.60 / 646.60 / 599.60 / 646.60 | 864 | 864 | Exact volume match |
| SMPDA | 2024-08-18 | 1,078.10 / 1,162.70 / 1,078.10 / 1,162.70 | 5,314 | 5,314 | Exact volume match |

The OHLCV source files are `03_stock_charts_ohlcv/NMLBBL_OHLCV.csv` and `03_stock_charts_ohlcv/SMPDA_OHLCV.csv`. The prior-session archive files contain market-wide rows but zero target-symbol rows; the OHLCV files also have no target rows on those prior dates.

## Contract identity caveat

The source schema contains both `contract_no` and `id`. On the SMPDA candidate/prior files, `contract_no` values are reused across different symbols, while the row `id` values are unique. Therefore a global uniqueness check on `contract_no` would falsely classify cross-symbol reuse as duplicate trades. The validator now distinguishes:
- duplicate contract numbers within the same symbol;
- contract-number reuse across different symbols;
- duplicate row IDs;
- duplicate full rows.

The `id` is a unique archive row identifier, but its semantics as an exchange contract identifier have not been independently proven. This schema ambiguity remains a source-quality warning. No transaction-identity claim should rely on `contract_no` alone.

## What this supports

- The third-party archive contains positive NMLBBL rows on 2024-05-19, and their total quantity matches the OHLCV volume.
- The third-party archive contains positive SMPDA rows on 2024-08-18, and their total quantity matches the OHLCV volume.
- The two immediately preceding candidate-session files contain no rows for the respective symbols.
- All four compressed files pass byte-count and LFS SHA-256 checks against the Hugging Face repository tree.
- The rows pass the implemented date, numeric, and amount-arithmetic checks, subject to the contract-number identity caveat recorded above.

## What this does not yet prove

The source is a third-party dataset that describes itself as NEPSE floorsheet data. It is not a direct NEPSE primary-source capture. The dataset card currently reports a dataset-generation parsing error for a malformed contract-number value. The repository tree and LFS hashes prove which third-party objects were downloaded, not that every exchange contract was captured.

No upstream NEPSE `totalElements`, page count, complete-pagination receipt, official session totals, or independently verified complete-session control total was retrieved for these four dates. Thus zero target rows on the prior dates cannot yet establish that the securities had no trades.

## Lifecycle disposition

| Symbol | Candidate first trade | Prior-date result in third-party archive | Lifecycle `valid_from` |
|---|---|---|---|
| NMLBBL | 2024-05-19 (positive rows; OHLCV volume matches) | 2024-05-16 has zero target rows | **UNKNOWN — primary/full-session completeness pending** |
| SMPDA | 2024-08-18 (positive rows; OHLCV volume matches) | 2024-08-14 has zero target rows | **UNKNOWN — primary/full-session completeness pending** |

Do not promote either lifecycle date yet. Do not label the prior dates `NO_TRADE` from this archive alone. No canonical OHLCV, lifecycle `valid_from`, calendar status, training label, or scanner score was changed.

## Next evidence requirement

Obtain official NEPSE date-specific floorsheets or an independently controlled complete-session capture for all four dates, including upstream pagination totals and full-page retrieval logs. Reconcile the official contract rows to these third-party files and same-date OHLCV totals. Only then can the first-trade boundary be promoted.

## Reproducibility

- Capture code: `tools/capture_p433_first_trade_floorsheets.py`
- Repository-tree discovery: `tools/discover_p433_hf_dataset_objects.py`
- Regression tests: `tools/tests/test_capture_p433_first_trade_floorsheets.py`
- Workflow: `.github/workflows/p433-first-trade-floorsheet-capture.yml`
- The first corrected capture run retrieved all four files and verified the LFS checksums. Subsequent CI runs test the refined per-symbol contract identity diagnostics and commit the immutable artifacts.
