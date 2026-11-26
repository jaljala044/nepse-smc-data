# P4.27 — audit of 490 one-day date-shift candidates

Date: 2026-11-26  
Scope: 490 `ALREADY_RECOVERED_DATE_SHIFT` candidates from the original P4.22 recovery artifact.  
Status: row-level raw-source, session-calendar and same-day-page comparison passed; primary NEPSE EOD confirmation remains pending.

## Results

| Check | Result |
|---|---:|
| Candidate rows | 490 |
| 2026-03-01 → 2026-03-02 | 238 |
| 2026-07-24 → 2026-07-25 | 252 |
| Exact tuple match to SMC raw row on following date | 490/490 |
| Exact tuple match to ShareSansar snapshot captured on following date | 490/490 |
| Raw source file hash available | 490/490 |
| Calendar pair: candidate date open-observed → following date closed | 490/490 |
| Rows with unresolved row-level mismatch | 0 |

The comparison covers Open, High, Low, Close and Volume. The builder preserves each original candidate date and records the following raw-file date separately. It does not rewrite raw files or move source rows.

## Session-calendar evidence

The pinned canonical calendar contains:

- 2026-03-01: `verified_open_observed`, based on positive official NEPSE price/volume evidence for security ID 8108 only.
- 2026-03-02: `verified_closed`, listed as Fagu Purnima in the official NEPSE holiday API.
- 2026-07-24: `verified_open_observed`, based on positive official NEPSE price/volume evidence for security ID 8108 only.
- 2026-07-25: `verified_closed`, regular weekly closure under the Monday–Friday schedule.

Important qualification: the positive official trade observation on each candidate date is for security ID 8108, not a market-wide per-security proof. The closure records for the following dates are market/session-level evidence.

## Contemporaneous ShareSansar page captures

The following-day daily-page captures contain all candidate symbols and match all 490 tuples exactly:

| Capture date | Pinned scraper commit | Capture time UTC | Rows in capture | Candidate matches |
|---|---|---|---:|---:|
| 2026-03-02 | e93c9fdd4841003770d76357a1c570562fd82e55 | 11:48:58 | 341 | 238/238 |
| 2026-07-25 | 6d13e28cc7157834114cca241c8d1d1055fe87b7 | 12:12:28 | 353 | 252/252 |

The 2026-03-01 contemporaneous capture contains only 13 symbols and none of the 238 candidate symbols; no 2026-07-24 daily-page capture was found in this archive. Thus the next-day page snapshots corroborate the values, but they do not establish the original trade date independently.

These are ShareSansar secondary captures, not 490 independent exchange records.

## Disposition

All 490 remain classified:

`SECONDARY_CORROBORATED_ONE_DAY_DATE_SHIFT_PRIMARY_PENDING`

The evidence supports the one-day date-label correction in the provisional derived view: candidate dates are open-observed, the following raw dates are closed, and the full OHLCV tuple is identical in raw files and next-day page captures. It does **not** justify changing raw source dates or claiming per-security official confirmation.

- Raw SMC OHLCV files remain unchanged.
- Original external archive files remain unchanged.
- Provisional derived date mapping remains review-only and not scanner-approved.
- Do not use these rows as primary-confirmed training labels until official per-security EOD records or complete date-matched floorsheets are captured.

## Reproducibility

- Builder: `tools/audit_p427_date_shifts.py`
- Regression tests: `tools/tests/test_audit_p427_date_shifts.py`
- CI run: [45865050524](https://github.com/jaljala044/nepse-smc-data/actions/runs/45865050524)
- Matrix: [p427_490_date_shift_audit_2026-11-26.csv](p427_490_date_shift_audit_2026-11-26.csv)
- Artifact: [15140301490](https://github.com/jaljala044/nepse-smc-data/actions/runs/45865050524/artifacts/15140301490)

## Next priority — P4.28: official per-security EOD validation

Capture exact official NEPSE EOD rows for the 490 candidate tuples (281 unique securities across two dates), using validated symbol-to-security-ID mappings and the official history endpoint while the dates remain inside the rolling history window. Validate endpoint provenance, security identity, exact date, one-row uniqueness, OHLCV validity and payload hash. If official evidence cannot be obtained for a symbol/date, retain the secondary-only disposition and UNKNOWN policy.
