# NEPSE Provider Date Cross-Check — 2026-11-26

## Scope

Task 2 of the five-task equity OHLCV validation queue. This is a targeted cross-check of exceptional and schedule-change dates against accepted secondary market sources. It is not a full re-verification of all 41 dates in the 2026 holiday capture.

## Confirmed dates and findings

| Date(s) | Calendar interpretation | Provider evidence | Outcome |
|---|---|---|---|
| 2026-03-04, 2026-03-05, 2026-03-06 | Election-related market closures | ShareSansar reported the government-declared public holidays and stated NEPSE would remain closed; regular trading was to resume Monday, 2026-03-09 | Cross-checked |
| 2026-03-08 | International Women's Day closure | Same ShareSansar report explicitly includes the additional public holiday and NEPSE closure | Cross-checked |
| 2026-04-05 / effective 2026-04-06 | Transition from Sunday–Thursday to Monday–Friday trading | ShareSansar reported NEPSE's board decision to include Friday and the updated Monday–Friday schedule | Cross-checked |
| 2026-09-21 | Exceptional market-wide closure | ShareSansar, Merolagani, Kathmandu Post and Nepal News report the suspension due to Data Hub technical problems affecting broker systems | Strongly cross-checked |
| 2026-09-22 | Trading resumed after the exceptional closure | ShareSansar and Merolagani reported that trading resumed after the Data Hub issue was resolved | Cross-checked |

## Key evidence URLs

1. ShareSansar — election and International Women's Day closure (2026-03-04):
   https://www.sharesansar.com/newsdetail/nepse-to-remain-closed-for-four-days-amid-election-and-international-womens-day-holidays-2026-03-04
2. ShareSansar — Friday trading / Monday–Friday schedule decision (2026-04-05):
   https://www.sharesansar.com/newsdetail/nepse-to-open-for-trading-on-fridays-board-approves-new-5-day-schedule-2026-04-05
3. ShareSansar — updated Monday–Friday schedule (2026-04-08):
   https://www.sharesansar.com/newsdetail/nepal-stock-exchange-opens-monday-to-friday-under-new-government-timings-2026-04-08
4. ShareSansar — 2026-09-21 closure due to Data Hub issue:
   https://www.sharesansar.com/index.php/newsdetail/market-to-remain-closed-today-due-to-data-center-issue-2026-09-21
5. Merolagani — NEPSE to remain closed on 2026-09-21:
   https://www.merolagani.com/NewsDetail.aspx?newsID=131011
6. Kathmandu Post — NEPSE closed after data centre outage (2026-09-21):
   https://kathmandupost.com/money/2026/09/21/nepse-closed-after-data-centre-outage-disrupts-trading
7. Nepal News — trading suspended due to technical glitch (2026-09-21):
   https://english.nepalnews.com/s/business/nepse-trading-suspended-today-due-to-technical-glitch/
8. ShareSansar — trading resumes after Data Hub issue (2026-09-22):
   https://www.sharesansar.com/newsdetail/nepse-resumes-trading-after-data-hub-technical-issue-resolved-2026-09-22
9. Merolagani — trading resumes after Data Hub technical glitch (2026-09-22):
   https://eng.merolagani.com/NewsDetail.aspx?newsID=131050

## Important interpretation

- The 2026-09-21 row in the existing calendar is correctly treated as an exceptional market-wide closure. The captured holiday API description “Emergengy Market Close” is imprecise; provider reporting explains the operational cause as a Data Hub technical failure affecting 72 broker members.
- The 2026-09-22 date is a positive trading/resumption day according to provider reporting. It should not be marked closed.
- The March 4–6 and March 8 closures are public-holiday closures, not missing OHLCV dates.
- The trading-week regime change is supported by provider reporting. Do not apply the new Monday–Friday regime retroactively before its effective date.
- This targeted review does not establish the completeness of the full 2026 holiday list. Other dates remain supported only by their captured calendar evidence until individually cross-checked.

## Task 2 outcome

**Completed — targeted provider cross-checks support the identified holiday block, trading-week transition, exceptional closure, and next-day resumption.**

Proceed to Task 3: build the canonical date-level session calendar with explicit evidence-backed status. Do not infer open dates from weekday rules alone.

## Related repository evidence

- [2026 session calendar](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_session_calendar_2026.csv)
- [2026 calendar evidence manifest](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_calendar_evidence_manifest_2026.json)
- [Session-date reconciliation](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_session_date_reconciliation_2026-11-26.md)
