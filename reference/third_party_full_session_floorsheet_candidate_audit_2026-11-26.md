# Third-party full-session floorsheet candidate audit — 2026-11-26

## Scope and source

Inspected `socrateai-official/nepse-open-data`, specifically `floorsheet/floorsheet_2026-11-20.csv`, its repository README and LICENSE.

- Repository: https://github.com/socrateai-official/nepse-open-data
- Raw file: https://github.com/socrateai-official/nepse-open-data/blob/main/floorsheet/floorsheet_2026-11-20.csv
- Git blob SHA: `6f74994849641296e2a16cad22fb555b08955c35`
- File size: 2,335,392 bytes
- Source repository commit: `cfa92493e93211c7019a5cd0b2cbe7d400d9c4e3` (2026-11-24)
- Repository README describes the folder as daily raw trade data; it does not document the exact capture mechanism, upstream NEPSE pagination totals, raw response hashes, or a per-date completeness manifest.
- Repository LICENSE is MIT. That does not independently establish rights to redistribute underlying exchange-origin data commercially.

This is a third-party public archive candidate, not an authenticated NEPSE-origin raw response. Do not promote it to authoritative source status based only on the repository description.

## File-level validation (2026-11-20)

Parsed 39,966 contract rows.

| Check | Result |
|---|---:|
| Rows | 39,966 |
| Distinct symbols | 352 |
| Duplicate transaction IDs | 0 |
| Rows with date other than 2026-11-20 | 0 |
| Non-positive quantity/rate | 0 |
| Amount identity failures where abs(quantity × rate − amount) > NPR 0.01 | 0 |
| Total shares | 10,602,468 |
| Total turnover | NPR 3,887,563,470.82 |

These checks establish internal consistency, not full-day completeness. No independent upstream `totalElements`/page count or exchange-issued day total was present in the repository metadata examined.

## Cross-check against the current data repository

Compared the third-party floorsheet's aggregate quantities with the existing five current-equity OHLCV files for the same date.

| Symbol | Floorsheet contracts | Floorsheet shares | Existing OHLCV volume | Result |
|---|---:|---:|---:|---|
| NESDO | 22 | 1,521 | 1,521 | MATCH |
| SYPNL | 367 | 32,947 | 32,947 | MATCH |
| ULBSL | 24 | 504 | 504 | MATCH |
| USLB | 26 | 1,595 | 1,595 | MATCH |
| YMHL | 169 | 5,951 | 5,951 | MATCH |

The five-symbol cross-check covers 608 contracts and 42,518 shares. It is positive independent corroboration for these five symbol/date quantities only. It does not establish completeness for every security or date.

## Comparison with the existing 500-row extract

The existing `02_floorsheet_daily/floorsheet_2026-11-20.csv` contains 500 rows and has a different schema/transaction-ID representation. No exact match was found between its rows and the third-party file using symbol, buyer, seller, quantity and rate. This is a source-level discrepancy requiring provenance investigation; do not merge the 500 rows into the candidate file or treat them as a verified subset.

## Decision

- Candidate classification: `THIRD_PARTY_FULL_SESSION_CANDIDATE`, not `VERIFIED_COMPLETE`.
- Positive trade evidence can be used cautiously for rows that pass symbol/date/contract validation and independent OHLCV reconciliation.
- Absence of a symbol from this candidate file must remain `UNKNOWN` until full-day completeness is independently evidenced.
- Do not write this file into canonical floorsheet storage, do not infer `NO_TRADE`, and do not use it for broker-footprint scoring yet.
- Next validation: obtain source capture metadata/upstream total for 2026-11-20, investigate the 500-row extract mismatch, then repeat the five-symbol and broader equity-universe quantity reconciliation across additional dates.

## Reproducibility references

- Third-party floorsheet Git blob: `6f74994849641296e2a16cad22fb555b08955c35`
- Third-party EOD board Git blob used for inspection only: `33784c60c509be30812cd2c8004276271fc0df8a`
- Existing local floorsheet sample Git blob: `0ca3de49d855b240ddf568fa95ce5999e4603c40`
- Existing five-symbol OHLCV blobs are recorded in the five-symbol reconciliation report dated 2026-11-26.


## Adapter implementation and CI

PR #12 added a schema adapter for the inspected third-party column names (`transaction`, `symbol`, `buyer`, `seller`, `quantity`, `rate`, `amount`, `date`). It also parses common display suffixes (K, lakh, crore, M, B) with precision-aware rounding tolerance and rejects rows where a numeric amount fails quantity × rate validation. Invalid rows cannot establish positive `TRADED` evidence.

- PR: https://github.com/jaljala044/nepse-smc-data/pull/12
- Merged commit: `91cf082b53cb2ed3564d06c85cc08a7964a5eaee`
- CI run: https://github.com/jaljala044/nepse-smc-data/actions/runs/45839623070
- Result: success; 16 tests ran and passed (`Ran 16 tests`, `OK`).

The adapter enables parsing the candidate format; it does not upgrade the candidate's completeness classification. `NO_TRADE` remains blocked without independently verifiable per-date upstream totals and pagination evidence.


## Additional provenance investigation — independent capture pipeline lead (2026-11-26)

Investigated the public NEPSE ingestion pipeline at https://github.com/ANKITSANJYAL/nepse-pipeline and its published dataset at https://huggingface.co/datasets/AnkitSanjyal/nepse-market-data.

### What the pipeline source establishes

The public floorsheet collector describes and implements a materially stronger capture design than the SocrateAI CSV archive:

- Fetches page 0 and reads upstream totalElements / page metadata.
- Performs full pagination at session close rather than relying on a sample.
- Persists raw page payloads to a bronze layer before parsing.
- Upserts by contract ID and checks held rows against the upstream total.
- Re-sweeps incomplete sessions.
- Quality checks include non-zero rows, uniqueness of contract IDs, required fields, quantity × rate = amount, positive quantity/rate, trade-time/date match and symbol breadth.
- The published workflow runs after close and publishes the warehouse to Hugging Face.

This is a documented and code-inspected completeness method. It is NOT evidence that the SocrateAI 39,966-row file was produced by this pipeline. The SocrateAI repository tree contains only the daily CSV archive, README, LICENSE and an empty meta/.gitkeep; no capture workflow, raw response archive or per-date completeness manifest was found.

### Dataset coverage and the 2026-11-20 lead

The Hugging Face dataset card describes floorsheet coverage from 2026-08-19, with a stated gap from 2026-08-26 through 2026-11-18. Thus 2026-11-20 is outside the documented gap and is a high-priority candidate date for independent comparison.

However, the public page inspected in this pass did not expose a date-specific 2026-11-20 floorsheet row count, contract IDs, upstream totalElements, or downloadable raw bronze response evidence. The dataset page's overall row count and general coverage statement are not sufficient to certify that date. Direct retrieval of the dataset's file/API listing was unavailable in this execution environment, so no contract-level comparison with the 39,966-row SocrateAI CSV or the existing 500-row extract is claimed.

### Revised conclusion

- The independent pipeline gives us a concrete, reproducible capture methodology and a second archive worth pursuing.
- The exact 2026-11-20 completeness reconciliation remains NOT YET PERFORMED.
- The 500-row extract mismatch remains unresolved.
- Do not relabel the SocrateAI candidate as verified complete, infer NO_TRADE from absences, or promote it to canonical broker-flow/training data.
- Immediate next action: retrieve the Hugging Face floorsheet partition for 2026-11-20 and compare contract IDs and normalized rows against both local files; require the date's upstream totalElements and page-level bronze evidence before certifying completeness.

Evidence links:
- Pipeline floorsheet capture implementation: https://github.com/ANKITSANJYAL/nepse-pipeline/blob/main/src/nepse_pipeline/jobs/floorsheet.py
- Pipeline quality gate: https://github.com/ANKITSANJYAL/nepse-pipeline/blob/main/src/nepse_pipeline/quality.py
- Capture workflow: https://github.com/ANKITSANJYAL/nepse-pipeline/blob/main/.github/workflows/capture.yml
- Published dataset and declared coverage: https://huggingface.co/datasets/AnkitSanjyal/nepse-market-data


## Date-specific independent archive located — retrieval pending (2026-11-26)

A live Hugging Face repository tree query for `AnkitSanjyal/nepse-market-data` returned a concrete file under `floorsheet/business_date=2026-11-20/part-0.parquet`:

- Dataset repository: https://huggingface.co/datasets/AnkitSanjyal/nepse-market-data
- Partition path: `floorsheet/business_date=2026-11-20/part-0.parquet`
- Reported file size: 840,136 bytes
- Hugging Face tree entry OID: `0f58264637283ce959ed54837fd92518a5534cfa`
- LFS object SHA-256: `7f52d0004418a7aa82a5930e84438968022a14e3acf94ac9e3e51c431ccbc480`

This resolves the earlier uncertainty about whether a 2026-11-20 floorsheet partition is present in that repository: the file is present in its public tree. It does NOT yet establish its row count, schema, upstream totalElements, contract-ID uniqueness, row-level overlap, or source independence from the SocrateAI CSV. The published dataset viewer exposes a separate default tabular configuration (1-minute bars), not this floorsheet parquet partition, so the viewer's generic row API cannot be used as a substitute for reading the contract file.

Direct binary retrieval/decoding was not completed in this environment. A browser retrieval attempt could not start because the external browser service wallet is out of funds; no retry was made. Next is to retrieve this exact parquet object through an available binary-capable route, inspect its schema and rows, then compare contract IDs/normalized fields against the 39,966-row SocrateAI CSV and 500-row local extract. Until then the file is classified `INDEPENDENT_ARCHIVE_PARTITION_LOCATED_NOT_RECONCILED`.


## Strong independent upstream-count reconciliation — 2026-11-20 (2026-11-26 follow-up)

Retrieved the actual GitHub Actions job log for the independent `ANKITSANJYAL/nepse-pipeline` capture run on 2026-11-20, rather than relying only on the dataset card or README.

### Run evidence

- Workflow run: https://github.com/ANKITSANJYAL/nepse-pipeline/actions/runs/44748903787
- Job: `capture`, job ID `136331336130`; completed SUCCESS, 2026-11-20 13:57:36–14:03:04 UTC.
- Capture commit: `87e68b8fd43c929a715b1b747a0ad7a799abb92f`.
- Exact collector log: `floorsheet_sweep date=2026-11-20 upstream=39966 held=0 pages=80/80 mode=full`.
- Exact completion log: `floorsheet_done date=2026-11-20 pages=80 parsed=39966 held=39966/39966 rejected=0 empty_pages=none`.
- Collector log: `floorsheet_complete after 1 full sweep(s)`.
- Finalization log: `floorsheet_finalized date=2026-11-20 rows=39966 parquet=.../floorsheet/business_date=2026-11-20/part-0.parquet`.

### Independent quality gate output (all PASS)

- 39,966 contracts; held count equals upstream `totalElements` exactly.
- 0 duplicate contract IDs.
- 0 nulls in required symbol/rate/quantity fields.
- 0 quantity × rate/amount identity failures.
- 0 non-positive price or quantity rows.
- 0 trade-time/business-date mismatches.
- 352 distinct symbols.
- EOD companion checks: 352 securities, 0 duplicate symbols, 0 high<low bars, 4 flagged rows within the bounded threshold, and 352 vs trailing median 348 (1% drift).

The SocrateAI CSV candidate previously parsed in this audit also has 39,966 rows, 352 symbols, zero duplicate transaction IDs, all dates 2026-11-20, zero nonpositive quantity/rate rows and zero amount identity failures. Its independently computed totals are 10,602,468 shares and NPR 3,887,563,470.82 turnover. The exact row count and symbol breadth now match the separate pipeline's upstream-total reconciliation. However, **contract-ID/row-level comparison between the two published files has not been completed**, so equality of contents is not asserted.

### Provenance limitation discovered in the same run

The job's `Archive raw responses (private)` step ran, but the log explicitly states `HF_BRONZE_REPO not set - raw responses not archived this run`. The public parquet was published successfully, and the run log preserves the upstream count and quality-gate output, but the original page payloads were not retained in the configured private bronze repository for this run. This weakens replayable source provenance.

### Revised status and safe use

- Upgrade the 2026-11-20 file from `THIRD_PARTY_FULL_SESSION_CANDIDATE` to `UPSTREAM_COUNT_RECONCILED_THIRD_PARTY_CAPTURE` for date-level completeness: independent live-capture log shows 80/80 pages, held=upstream_total=39,966, no rejected/empty pages and all floorsheet quality checks passing; SocrateAI file has the same 39,966 rows and 352 symbols.
- This is strong independent completeness corroboration, **not** raw-page replay proof and **not** contract-level identity proof.
- Do not yet call the two files identical, use this to certify every individual symbol's absence, or promote broker attribution/manipulation analysis. For NO_TRADE on a symbol, first complete contract-level cross-source comparison or recover the upstream private bronze page archive, plus verified open-session evidence.
- Positive contract evidence in the SocrateAI file remains usable as third-party observed-trade evidence with its source label and confidence limitation; absence remains UNKNOWN.
- The 500-row local extract mismatch remains unresolved. It appears to be a distinct/partial extract, not the 39,966-row full-session candidate; do not merge it.

Evidence:
- Run: https://github.com/ANKITSANJYAL/nepse-pipeline/actions/runs/44748903787
- Collector implementation: https://github.com/ANKITSANJYAL/nepse-pipeline/blob/87e68b8fd43c929a715b1b747a0ad7a799abb92f/src/nepse_pipeline/jobs/floorsheet.py
- Quality gate implementation: https://github.com/ANKITSANJYAL/nepse-pipeline/blob/87e68b8fd43c929a715b1b747a0ad7a799abb92f/src/nepse_pipeline/quality.py


## Contract-level reconciliation completed — 2026-11-20 (2026-11-26)

A GitHub Actions audit in this repository downloaded the exact Hugging Face Parquet partition and the SocrateAI CSV, then compared normalized trade multisets. This is now contract-level evidence, not merely matching totals.

### Independent Parquet ↔ SocrateAI result

- CI run: https://github.com/jaljala044/nepse-smc-data/actions/runs/45843030655 (job 139989397910; SUCCESS).
- Independent Parquet SHA-256: `7f52d0004418a7aa82a5930e84438968022a14e3acf94ac9e3e51c431ccbc480` (matches Hugging Face LFS object OID).
- SocrateAI CSV SHA-256: `abafc3b8eaa8d2b9b884e9f2df974deb267485d4476f2a4e953d6324787fc43d`.
- Both sources: 39,966 rows, 39,966 valid normalized rows, 0 invalid rows, 352 distinct symbols, 10,602,468 shares, NPR 3,887,563,470.82 turnover.
- Exact normalized trade multiset comparison on date, symbol, buyer, seller, quantity, rate and amount: **39,966 matched; 0 Parquet-only; 0 CSV-only; exact_multiset_match=true**.
- This proves the SocrateAI CSV content is an exact normalized row-for-row multiset copy of the independent Parquet partition. Combined with the independent collector log (upstream totalElements=39,966; 80/80 pages; 39,966/39,966 held; 0 rejected; no empty pages; all quality checks PASS), the 2026-11-20 full-session file is upgraded to **VERIFIED_COMPLETE_BY_INDEPENDENT_UPSTREAM_CAPTURE**.

### 500-row local extract discrepancy explained

- The local extract contains 500 rows / 158 symbols, not a 500-row full-session capture.
- Identity-only comparison (date, symbol, buyer, seller, quantity and rate, excluding amount): **500/500 local rows match records in the complete Parquet**; 39,466 full-session rows are additional; 0 local identity rows are unmatched.
- Amount equality is weaker because local amounts are abbreviated (`K`, `Lac.`) and rounded. Of the 500 identity matches, 210 amounts are exact; 46 differ by <= NPR 1; 138 by <= NPR 10; 21 by <= NPR 100; 85 by > NPR 100. These are lossy display amounts, not evidence of different trades. The local file is a partial extract and must not be used to infer symbol absence or full-session completeness.
- The previous exact-key comparison that counted only 210 matches was too strict for this abbreviated amount column; identity matching resolves the apparent 290-row discrepancy.

### UNL result on 2026-11-20

The complete, independently corroborated file contains **4 UNL contracts, 50 shares, NPR 2,408,700 turnover**. The four normalized records are:

| Buyer member ID | Seller member ID | Quantity | Rate (NPR) | Amount (NPR) |
|---:|---:|---:|---:|---:|
| 48 | 6 | 10 | 48,390 | 483,900 |
| 48 | 6 | 10 | 48,480 | 484,800 |
| 28 | 35 | 20 | 48,000 | 960,000 |
| 20 | 35 | 10 | 48,000 | 480,000 |

**Decision for UNL, 2026-11-20: TRADED.** This resolves the date-specific status. It does not establish UNL's status on 2026-11-26 or any other date; those dates require their own complete session evidence. The 500-row local partial extract's absence of UNL is not contradictory evidence.

### Remaining provenance caveat and scope

The successful 2026-11-20 pipeline job logged `HF_BRONZE_REPO not set - raw responses not archived this run`. Therefore raw page-by-page replay evidence is unavailable, even though the independent upstream total, full page sweep, quality report and exact published-file comparison all agree. Retain this caveat in provenance.

This resolves **one date**, not the full 281-equity historical completeness project. Apply `TRADED` for symbols with validated positive rows on this date. For symbols absent from the verified full-session file, `NO_TRADE` can be considered only after confirming the security was active/listed and the session was open for that date. Do not generalize this result to other dates, and do not enable global canonical promotion or model training.

### Machine-readable evidence

See `reference/floorsheet_source_verification_2026-11-20.json` for source hashes, counts, status and UNL contracts.
