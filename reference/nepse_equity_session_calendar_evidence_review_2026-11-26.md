# NEPSE Equity Session Calendar Evidence Inventory Review
**Review date:** 2026-11-26  
**Scope:** Evidence already present in `jaljala044/nepse-smc-data`; equities only for downstream OHLCV coverage.

## Summary

The repository already contains substantial NEPSE calendar evidence. This review inventories it; it does not certify every date in the historical calendar as an open or closed session.

| Evidence asset | Current contents | Review result |
|---|---|---|
| `reference/nepse_primary_observed_open_sessions_2025-2026.csv` | 225 dated positive-trade observations | 225 rows, 225 unique dates; 2025-11-25 through 2026-11-19; zero zero-trade observations |
| `reference/nepse_session_calendar_2026.csv` | 41 explicit closure rows | 40 `verified_closed`, 1 `verified_exceptional_closed`; dates 2026-01-11 through 2026-12-30 |
| `reference/nepse_calendar_evidence_manifest_2026.json` | Raw official NEPSE holiday API capture metadata and date claims | Captured 2026-11-25; HTTP 200; 4,932 bytes; 41 records; SHA-256 recorded |
| `reference/nepse_holiday_listing_entries_2014-2025.csv` | 408 holiday listing entries | All captured years marked `all_pages_captured_for_year`; year 2020 is absent from this listing export |
| `reference/nepse_holiday_api_coverage_2015-2026.csv` | Year-level API capture counts | 2015–2026 represented; every row explicitly classified as holiday evidence, **not a complete session calendar** |

## Positive observed-session evidence

The 225-row positive-trade observation file contains:
- 225 unique dates
- Earliest date: 2025-11-25
- Latest date: 2026-11-19
- Weekday distribution: Sunday 16, Monday 45, Tuesday 47, Wednesday 47, Thursday 44, Friday 26, Saturday 0
- All 225 observations have positive trade counts

The Sunday observations are consistent with the pre-2026-04-06 Sunday–Thursday regime; Friday observations are consistent with the post-2026-04-06 Monday–Friday regime. This is a positive-observation sample tied to the captured security ID 8108, not a guarantee that every open session is represented for every equity.

## Explicit 2026 closure evidence

The 2026 session calendar has 41 explicit closure rows:
- 40 `verified_closed`
- 1 `verified_exceptional_closed`

The exceptional closure is 2026-09-21, described in the source as “Emergengy Market Close”. The official NEPSE holiday API capture metadata records:
- URL: https://nepalstock.com.np/api/nots/holiday/list?year=2026
- Retrieved: 2026-11-25T13:13:17.600880Z
- HTTP status: 200
- Response records: 41
- SHA-256: `dd1777e3c61623048e00dc170d860659b14b8821ffabff8338002ccafdb2ea8f`

The calendar notes correctly treat listed closure dates as explicit closure evidence only; absence from the holiday response is not evidence that a date was open.

## Gaps and controls

1. The 2015–2026 holiday API coverage file is explicitly **not a complete session calendar**. A holiday list alone cannot prove all remaining dates were open.
2. The holiday listing export contains 2014 and 2015–2025 but no 2020 year; the separate API coverage file does contain 2020 API evidence (101 records, 100 unique dates). Keep these capture routes distinct and do not infer missing records.
3. Positive trade observations are only a sampled instrument history and date range. Use them as positive evidence for those dates, not as a universal full-universe calendar without further cross-checks.
4. Calendar rows should preserve evidence source, raw hash, retrieval time, scope, and classification.
5. Use fail-closed classifications: `verified_open_observed`, `verified_closed`, `candidate_open_weekday`, and `unverified`. Do not turn candidate weekdays into confirmed open sessions automatically.
6. Keep the raw OHLCV archive unchanged. Apply date corrections or carry-forward exclusions only in a separate derived dataset with source provenance.

## Next actions

1. Reconcile the existing positive observed-session dates with the explicit 2025/2026 closure captures.
2. Cross-check gaps and exceptional dates with accepted provider evidence (ShareHub, Chukul, ShareSansar, NepseAlpha) and NEPSE notices where available.
3. Build a date-level canonical calendar with explicit status, scope, source, and evidence URL.
4. Only then compute per-symbol expected-session coverage and missing-session gaps for the 281 provisional common-equity inventory.

## Repository evidence links

- [Positive observed open sessions](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_primary_observed_open_sessions_2025-2026.csv)
- [2026 session calendar](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_session_calendar_2026.csv)
- [2026 calendar evidence manifest](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_calendar_evidence_manifest_2026.json)
- [Holiday listing entries 2014–2025](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_holiday_listing_entries_2014-2025.csv)
- [Holiday API coverage 2015–2026](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_holiday_api_coverage_2015-2026.csv)
