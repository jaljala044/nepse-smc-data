# NEPSE Equity Weekly Trading Calendar Baseline
**Prepared:** 2026-11-26  
**Purpose:** Base weekday rules for equity OHLCV session validation. This is not yet a complete holiday calendar.

## Weekly schedule regimes

| Effective period | Trading weekdays | Weekly closed days | Evidence |
|---|---|---|---|
| Before 2026-04-06 | Sunday–Thursday | Friday, Saturday | Historical NEPSE schedule; transition confirmed in April 2026 reports |
| From 2026-04-06 onward | Monday–Friday | Saturday, Sunday | NEPSE Board decision/public notice reported 8 April 2026 |

## Approved supporting references

1. ShareSansar, 8 April 2026: reports that NEPSE issued a public notice and its Board confirmed trading Monday through Friday, including Friday, following the change to Saturday/Sunday public holidays.  
   https://www.sharesansar.com/newsdetail/nepal-stock-exchange-opens-monday-to-friday-under-new-government-timings-2026-04-08
2. The Himalayan Times, 8 April 2026: reports the new Monday–Friday schedule was effective from 6 April 2026 and contrasts it with the previous Sunday–Thursday schedule.  
   https://thehimalayantimes.com/business/nepse-shifts-to-mondayfriday-trading-week

## Important limitations

- This file records only the weekly weekday regime.
- Public holidays, regional holidays where applicable, emergency closures, market suspensions, and special exchange notices must be recorded as explicit date exceptions.
- Do not use a generic government/bank/aviation holiday list as a substitute for NEPSE's own market-closure notices.
- Before a date is labelled an open session, seek NEPSE notice or accepted provider evidence (ShareHub, Chukul, ShareSansar, NepseAlpha).
- Do not infer that a closed-day-dated OHLCV row is a valid trade. Keep raw rows and mark them for review.
- Do not remove an exceptional weekend row without checking its source. The pilot identified ADBL 2026-07-25 as one such exception requiring verification.

## Next steps

1. Capture NEPSE holiday/closure notices for the relevant periods.
2. Cross-check each candidate session against dated market index/EOD or floorsheet evidence from accepted providers.
3. Produce a date-level calendar with `date`, `weekday_regime`, `expected_open`, `closure_reason`, `evidence_source`, and `evidence_url`.
4. Use the approved calendar to compute per-symbol eligible-session coverage and missing-session gaps.
