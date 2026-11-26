# P4.42 — 616-date NEPSE session candidate evidence audit

**Audit date:** 2026-11-26  
**Disposition:** evidence audit only; no date is promoted into the canonical session calendar.

## Executive result

The current candidate register contains 616 unique dates from 2024-03-04 through 2026-11-20. It is a useful discovery set, but it is not 616 independently verified exchange sessions.

| Evidence check | Result | Interpretation |
|---|---:|---|
| Candidate dates | 616 unique | All currently labelled `candidate_unverified` |
| Candidate dates in 2024 | 189 | Secondary archive lineage |
| Candidate dates in 2025 | 225 | Secondary archive lineage |
| Candidate dates in 2026 | 202 | Secondary archive lineage |
| Daily NEPSE index files found | 614 / 616 | File existence only; not row-level validation |
| Index files missing | 2 | 2025-04-03 and 2026-11-20 |
| Index files individually checked | 7 | One NEPSE index row per file; not a complete audit |
| Primary positive open-session observations | 225 dates | One sampled security ID, 8108 |
| Candidate dates overlapping those primary observations | 225 / 225 | Primary observations span 2025-11-25 through 2026-11-19 |
| Candidate dates without this primary positive observation | 391 | Remain unverified by this evidence set |
| Holiday API date rows overlapping candidate dates | 0 | Consistent with the candidate EOD archive skipping closure dates; not proof of completeness |

## Pinned source lineage

### Candidate EOD dates

Source artifact in companion scanner repository:
- `data/evidence/candidates/nepse-616-session-date-candidates-2024-2026.csv`
- Git blob: `8affc12783c318a552119844fd6bc70bf837ea53`
- 616 rows, 616 unique dates.
- All 616 records point to `srijankarki07/nepse-data`, revision `e6e6fe77cd3378204c7938e66601cee2339a8b7a`.
- Its recorded lineage is ShareSansar-derived and in the same upstream lineage family as the starter import.

This archive can nominate candidate session dates but cannot independently validate them.

### NEPSE index archive

Source artifact:
- `data/evidence/candidates/nepse-616-session-index-crosscheck-2024-2026.csv`
- Git blob: `b63ff7042277a2ffa5ae2277d4bf7910ed836c1d`
- 614 of 616 expected daily index files exist in `socrateai-official/nepse-open-data`, revision `f602a5b61e68582d28834d16f71151a4bae98d5b`.
- Missing files: 2025-04-03 and 2026-11-20.
- 607 rows are marked `file_exists_row_not_individually_checked`.
- Seven rows are marked `one_NEPSE_index_row_checked`; this is a very small sample, not a full 616-date validation.
- The candidate repository's lineage audit has not established the upstream source/capture method or rights for the SocrateAI dataset.

Therefore, 614 file-presence matches are **not** 614 independent exchange confirmations.

### Primary NEPSE positive observations

Source artifact:
- `data/reference/nepse_primary_observed_open_sessions_2025-2026.csv`
- Git blob: `8ce8bca2e3f1c08b7b86b07f572542a064e86ba0`
- 225 unique dates, 2025-11-25 through 2026-11-19.
- Official endpoint: `/api/nots/market/history/security/8108`.
- Every date is a positive trade observation for sampled security ID 8108, with non-zero trade count and volume.
- All 225 dates are present in the 616-date candidate register.

A positive official trade observation is direct evidence that the exchange was open on that date. It does not establish that all 281 equities were tradable, nor does the current ID prove historical identity before its effective period. The capture is scoped to one sampled security ID and should not be represented as a full-universe calendar.

### Official holiday API

Pinned multi-year audit:
- `data/evidence/acquired/nepse-holiday-api-multiyear-audit-2015-2026.json`
- Git blob: `8c82ae41ae6b0bff4827d3791c4cadfcc8183361`
- 12 annual responses, 499 rows, 498 unique date keys summed within years, all HTTP 200.
- 2018 and 2019 response ranges end early; annual completeness is not established.
- 2020-04-13 has two distinct closure descriptions and must remain a multi-record conflict.
- `instrumentTypeId` and `activeStatus` are null in all records.

The 499 closure rows were checked against the 616 candidate dates; there are zero date overlaps. This is a consistency observation only. It does not prove the holiday endpoint is exhaustive or that every non-holiday date was an open session.

## Required next steps

1. **Primary open-session evidence expansion:** acquire dated official NEPSE price/volume or index-history records for additional years and dates. If the official API only serves a rolling window, preserve the exact endpoint responses and document that historical retrieval limit.
2. **Historical schedule transitions:** obtain and byte-preserve NEPSE notices/circulars establishing changes to weekly trading days, hours and exceptional suspensions. A notice is useful only for its stated effective period.
3. **Index file audit:** investigate the two missing index files and individually parse/validate the 614 present files; first establish SocrateAI's source lineage and rights before using its data as corroboration.
4. **Calendar reconciliation:** combine primary positive observations and primary closure evidence with explicit precedence/conflict rules. Keep unsupported dates `UNKNOWN`.
5. **Regression coverage:** test date uniqueness, closure conflicts, positive-trade proof, source scope, effective schedule boundaries and no weekday-only promotion.

## Safety and impact

- No candidate date was promoted to `verified_open`.
- No closure date was deleted or deduplicated.
- No OHLCV, floorsheet, instrument lifecycle, canonical calendar, training label, score or trading signal changed.
- No win rate, backtest result or signal probability is asserted by this audit.

The 616 dates remain a candidate register. The 225 primary observations are positive proof for their individual dates only. The remaining 391 dates require additional evidence.
