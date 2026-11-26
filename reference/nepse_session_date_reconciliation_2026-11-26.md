# NEPSE Session-Date Reconciliation — 2026-11-26

## Scope

Task 1 of the five-task equity OHLCV validation queue. This reconciliation compares the repository's positive-trade observation sample against captured 2025 holiday-list dates and the explicit 2026 session-closure calendar. It does not alter raw OHLCV data.

## Inputs reviewed

- `reference/nepse_primary_observed_open_sessions_2025-2026.csv`
- `reference/nepse_session_calendar_2026.csv`
- `reference/nepse_holiday_listing_entries_2014-2025.csv`
- `reference/nepse_holiday_api_coverage_2015-2026.csv`
- `reference/nepse_calendar_evidence_manifest_2026.json`

## Reconciliation results

| Check | Result |
|---|---:|
| Positive-trade observation rows | 225 |
| Unique observed dates | 225 |
| Observation period | 2025-11-25 to 2026-11-19 |
| 2025 observations | 24 |
| 2026 observations | 201 |
| Positive-trade rows with positive trade count and volume | 225 |
| 2026 explicit closure rows | 41 |
| Unique dates in 2026 closure file | 41 |
| 2026 closure status counts | 40 verified_closed; 1 verified_exceptional_closed |
| Observed-date overlap with captured 2025 holiday dates | 0 |
| Observed-date overlap with 2026 closure dates | 0 |

The 2025 holiday comparison is limited to the observed period from 2025-11-25 through 2025-12-31. No observed positive-trade date in that interval appears in the captured 2025 holiday listing.

## Trading-week regime check

The observed dates align with the documented trading-week change effective 2026-04-06:

| Period | Observation count | Weekday distribution |
|---|---:|---|
| Before 2026-04-06 | 80 | Sun 16, Mon 16, Tue 18, Wed 16, Thu 14 |
| From 2026-04-06 | 145 | Mon 29, Tue 29, Wed 31, Thu 30, Fri 26 |

No pre-transition observation falls on Friday or Saturday. No post-transition observation falls on Saturday or Sunday. This is consistent with the earlier Sunday–Thursday regime and the Monday–Friday regime from 2026-04-06.

## Exceptional closure

The 2026 closure calendar contains 2026-09-21 as `verified_exceptional_closed`, with the captured description “Emergengy Market Close”. This date does not overlap the positive-trade observations for security ID 8108.

## Interpretation and limitations

1. The 225 positive-trade observations are from one sampled instrument history (security ID 8108), not a complete market-wide session feed.
2. Positive trade evidence establishes activity for that sampled security on those dates; it does not prove every listed equity traded on every observed date.
3. The absence of an observation on a date is not evidence that the market was closed.
4. A date absent from a holiday list is not automatically an open session.
5. The 2026 closure calendar has 41 explicit closure rows; these are closure evidence, not a complete list of all open sessions.
6. The reconciliation found no observed-date/closure-date conflict in the reviewed sample. This is a consistency result, not proof that the entire 2025–2026 calendar is complete.
7. No raw OHLCV, calendar source capture, or existing evidence file was modified.

## Task 1 outcome

**Completed — sample reconciliation passed with scope limitations recorded.**

The existing evidence is internally consistent for the reviewed sample. Proceed to Task 2: cross-check candidate gaps and exceptional dates against accepted provider evidence (ShareHub, Chukul, ShareSansar, NepseAlpha) and available NEPSE notices. Keep unresolved dates unverified rather than inferring sessions from weekday patterns.

## Repository evidence

- [Positive observed sessions](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_primary_observed_open_sessions_2025-2026.csv)
- [2026 explicit closure calendar](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_session_calendar_2026.csv)
- [2014–2025 holiday listing capture](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_holiday_listing_entries_2014-2025.csv)
- [2015–2026 holiday API coverage](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_holiday_api_coverage_2015-2026.csv)
- [2026 capture manifest](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_calendar_evidence_manifest_2026.json)
