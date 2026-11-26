# P4.31 — derived OHLCV v3 with 11 official Open corrections

Date: 2026-11-26  
Status: build and OHLCV/source-integrity audit passed.

## Release result

The v3 dataset is built additively from the immutable v2 release. It applies exactly the 11 official Open corrections proven in P4.30.

| Measure | Result |
|---|---:|
| Common-equity securities | 281 |
| Derived OHLCV rows | 246,238 |
| Raw source files verified | 281/281 |
| v2 source files verified | 281/281 |
| v3 output files verified | 281/281 |
| Official Open corrections applied and verified | 11/11 |
| Unapproved v2-to-v3 changes | 0 |
| Raw files modified | 0 |
| v2 files modified | 0 |
| Unverified rows promoted | 0 |

The 11 Open corrections are on MERO, UAIL (two dates), API, RAWA (two dates), SPDL, BGWT, HRL, RADHI and UNHPL. Full row values, security IDs and payload hashes are recorded in the P4.30 matrix and correction ledger.

## Remaining quality flags

After the 11 official Open corrections, the v3 OHLCV invariant audit reports 1,368 remaining historical flags:

| Flag | Remaining rows |
|---|---:|
| OPEN_OUTSIDE_RANGE | 1,314 |
| CLOSE_OUTSIDE_RANGE | 28 |
| HIGH_BELOW_LOW | 22 |
| NONPOSITIVE_PRICE | 4 |
| **Total** | **1,368** |

There are **zero remaining 2026 OHLCV invariant flags** in the audited v3 history. The remaining 1,368 flags are historical rows from 2009–2020 and are not repaired by interpolation, split assumptions or cross-symbol inference.

The largest concentrations remain AHPC (607), SKBBL (381), API (123), MERO (105), SPDL (73), CHL (48) and HIDCL (32). Historical primary-source evidence is still needed before these rows can be corrected or used in signals.

## Preservation and release status

- v2 remains available unchanged as the preceding derived release.
- Raw SMC OHLCV files remain unchanged.
- v3 manifest records raw source and v2 source Git blob hashes, v3 blob hashes, row counts and per-symbol correction counts.
- v3 corrections and provenance ledgers retain all v2 records and append the 11 P4.30 official corrections.
- The full OHLCV audit retains the historical invariant flags. This release is not described as fully session-clean.

## Validation

- Builder: `tools/build_derived_ohlcv_v3.py`
- Auditor: `tools/audit_derived_ohlcv_v3_release.py`
- Tests: `tools/tests/test_build_derived_ohlcv_v3.py`, `tools/tests/test_audit_derived_ohlcv_v3_release2.py`
- Successful CI run: [45870912308](https://github.com/jaljala044/nepse-smc-data/actions/runs/45870912308)
- The run built all 281 securities and passed the v3 integrity audit.
- CI artifact: [derived OHLCV v3 official Open corrections](https://github.com/jaljala044/nepse-smc-data/actions/runs/45870912308/artifacts)

## Next priority — P4.32

Recompute adjacent-repeat and session-calendar diagnostics on v3 (the 11 Open changes can alter adjacent OHLCV equality), retain the existing corporate-action/split review limits, and then start a date-scoped historical anomaly recovery for the largest affected symbols. No historical row should be promoted without exact primary evidence.
