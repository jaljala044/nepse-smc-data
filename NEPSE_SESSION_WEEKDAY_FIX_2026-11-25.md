# NEPSE weekday-candidate helper correction — 2026-11-25

## Work completed

Inspected `nepse_session_date.py` in this repository and compared its fixed Saturday/Sunday exclusion with the project's documented NEPSE schedule regimes in the scanner repository's `docs/NEPSE_SESSION_CALENDAR_AND_INTEGRITY_GATE.md`.

The old helper used one fixed weekend rule and therefore did not reflect the documented regime change effective 6 April 2026 (Monday-Friday candidate sessions). It also could not represent the temporary 2022 schedule changes.

Updated `nepse_session_date.py` to select candidate weekdays by date:

- Through 2022-05-14: Sunday-Thursday regular-session candidates.
- 2022-05-15 through 2022-06-14: Monday-Friday candidates.
- 2022-06-15 through 2022-09-16: Sunday-Friday candidates.
- 2022-09-17 through 2026-04-05: Sunday-Thursday candidates.
- From 2026-04-06: Monday-Friday candidates.

Added `test_nepse_session_date.py` with six unit tests covering the regime boundaries and weekend rollbacks.

## Validation

- The first GitHub Actions run (run **45491866079**) executed all six tests and found one incorrect expected value in the test for 2022-09-17: Friday 2022-09-16 was still a candidate under the temporary Sunday-Friday regime ending 2022-09-16. The implementation's result was consistent with the documented boundary; the test expectation was corrected from 2022-09-15 to 2022-09-16.
- The corrected test was committed in `f40bfe6cdf7e77a4c35e264c3e58f0a07bb9886f`. GitHub Actions rerun **45492038013 completed successfully**. All six unit tests passed.
- The helper is only a weekday-candidate function. It does not know exchange holidays, emergency suspensions, or exceptional sessions and must not be used as proof that NEPSE actually traded on a date.
- The canonical session calendar remains evidence-based and fail-closed as described in the scanner repository. Primary dated NEPSE notices/equivalent exchange evidence are still required.

## Commits

- Helper correction: `b73f8a5e09821f4722dc83790e75dfc052f432eb`
- Initial unit tests: `8767258bef04a03aaf1980024edd0cbbcadf533b`
- Corrected boundary expectation: `f40bfe6cdf7e77a4c35e264c3e58f0a07bb9886f`

## Next actions

1. Review all consumers of `effective_nepse_session_date` and ensure they treat its output as a weekday candidate only.
2. Continue primary-source session-calendar evidence collection; do not infer holidays or trading sessions from weekday rules.
3. Resume the highest-priority remaining historical-data integrity task after this helper correction.
