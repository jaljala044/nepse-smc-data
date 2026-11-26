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
