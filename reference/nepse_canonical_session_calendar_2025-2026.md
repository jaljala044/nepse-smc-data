# Canonical NEPSE Session Calendar — 2025-11-25 to 2026-12-30

## Purpose

Task 3 of the five-task common-equity validation queue. This is an evidence-scoped date calendar for the period covered by the current observed-session sample and 2026 closure capture. It does not claim to be a complete historical exchange calendar or a per-equity session guarantee.

## Output

- CSV: `reference/nepse_canonical_session_calendar_2025-2026.csv`
- Rows: 401 calendar dates, one row per date, inclusive.
- First date: 2025-11-25
- Last date: 2026-12-30
- Date keys are unique and chronological.
- Raw OHLCV files and source captures were not modified.

## Status counts

| Status | Rows | Meaning |
|---|---:|---|
| `verified_open_observed` | 225 | Positive trade observation for sampled security ID 8108 only |
| `verified_closed` | 150 | Explicit holiday/exception closure evidence or weekly closure under the documented schedule |
| `candidate_open_weekday` | 26 | Weekday with no direct positive-trade observation or explicit listed closure |
| `unverified` | 0 | Reserved for dates where even the broad classification cannot be established |

## Classification rules

1. Positive trade rows take precedence and are scoped to `security_id_8108_only`; they are not market-wide claims.
2. 2025 listed holiday dates in the covered period are marked `verified_closed`, with the holiday-list capture run ID and source URL.
3. 2026 explicit closure dates are marked `verified_closed`, retaining the original closure status and raw evidence hash in the record fields/notes. The exceptional 2026-09-21 closure is distinguished by `reason=exceptional_market_suspension`.
4. Regular weekly closure dates are marked `verified_closed` with `scope=market_weekly_schedule` and the relevant provider schedule source:
   - Before 2026-04-06: Friday and Saturday closed; Sunday–Thursday schedule.
   - From 2026-04-06: Saturday and Sunday closed; Monday–Friday schedule.
5. Weekdays without direct observed trade evidence or an explicit listed closure remain `candidate_open_weekday`. This includes dates after the sampled history ends on 2026-11-19.
6. No candidate weekday is promoted to a confirmed open session based only on weekday logic.

## Why there are no `unverified` rows in this bounded file

Every date in this particular interval can be assigned to one of the following without overclaiming: positive observed trade, explicit/weekly closure, or candidate weekday. The `unverified` category remains part of the schema for dates outside the evidenced weekly-schedule period or for unresolved exceptions. The absence of unverified rows does not mean the candidate weekdays are confirmed sessions.

## Evidence sources

- Positive observations: [sampled security history manifest](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_primary_observed_open_sessions_2025-2026.csv)
- 2026 explicit closures: [2026 session calendar](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_session_calendar_2026.csv) and [capture manifest](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_calendar_evidence_manifest_2026.json)
- 2025 holiday capture: [2014–2025 holiday listing entries](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_holiday_listing_entries_2014-2025.csv)
- Weekly schedule change: [ShareSansar, 2026-04-05](https://www.sharesansar.com/newsdetail/nepse-to-open-for-trading-on-fridays-board-approves-new-5-day-schedule-2026-04-05) and [ShareSansar, 2026-04-08](https://www.sharesansar.com/newsdetail/nepal-stock-exchange-opens-monday-to-friday-under-new-government-timings-2026-04-08)
- Exceptional closure: [ShareSansar, 2026-09-21](https://www.sharesansar.com/index.php/newsdetail/market-to-remain-closed-today-due-to-data-center-issue-2026-09-21)

## Limitations

- The observed-open evidence is one sampled instrument, not a full-universe trade calendar.
- The 2025 holiday-list capture covers all captured pages for the year, but the canonical file only includes dates in the bounded interval.
- The 2026 holiday API is explicit closure evidence; it is not itself a complete open-session calendar.
- The calendar should be extended only when new date-level evidence is captured. Do not backfill or infer missing trading sessions from OHLCV carry-forward rows.

## Task 3 outcome

**Completed — canonical date-level file created with evidence scope and conservative candidate classification.**

Next: Task 4, compute per-symbol coverage against this calendar. That calculation must use only `verified_open_observed` as direct open-date evidence for now, and clearly report that it is not a complete expected-session denominator. Do not treat `candidate_open_weekday` dates as confirmed sessions.
