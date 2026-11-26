# NEPSE reference-data validation stage — status refresh, 2026-11-26

## Added validation code

- `nepse_reference_validation.py`
- `test_nepse_reference_validation.py`

The validator enforces evidence-first calendar status, date uniqueness, explicit provenance for verified statuses, instrument symbol coverage, stable security IDs, non-overlapping effective-dated symbol mappings, and inclusive validity boundaries.

The stable security-ID guard was subsequently hardened and merged in PR #64. It rejects zero, negative, nonnumeric and decimal IDs. The PR's reference-data test checks completed successfully. This validates identifier shape; it does not prove that an ID is historically correct or that a full effective-dated instrument master exists.

## Current evidence status

### Historical holiday API captures — acquired, not a complete calendar

The earlier statement that no multi-year captures existed is superseded.

The companion scanner repository now preserves the official NEPSE holiday API response bytes for all years 2015–2026:
- Source endpoint: `https://nepalstock.com.np/api/nots/holiday/list?year={year}`
- Immutable capture commit: `39747bd2ade2bdb59ef7665f454bcbc04b3060df`
- 12 annual requests; HTTP 200 for all years
- 499 source records; 498 unique date keys summed within year; one duplicate-date row (2020-04-13, with two distinct closure descriptions)
- 2018 response ends 2018-11-09 and 2019 response ends 2019-10-30; annual completeness is not established
- All records have null `instrumentTypeId` and `activeStatus`; security scope is not established from those fields

The SMC data repository mirrors the year-level capture counts, source hashes and immutable source-file links in:
- `reference/nepse_holiday_api_coverage_2015-2026.csv`
- `reference/nepse_official_holiday_api_capture_mirror_2015_2026.json`

The raw response bytes remain in the companion scanner repository at the pinned commit above. The multi-year captures are closure evidence only. They must not be converted into verified-open dates or promoted as a complete historical session calendar.

### Current bounded calendar

`reference/nepse_canonical_session_calendar_2025-2026.csv` contains 401 dates from 2025-11-25 through 2026-12-30:
- 225 `verified_open_observed` dates, scoped to a sampled security ID 8108 only
- 150 `verified_closed` dates, using explicit closure or documented weekly schedule evidence
- 26 `candidate_open_weekday` dates
- 0 `unverified` dates in this bounded file

Candidate weekdays are not confirmed open sessions. The positive observations are not a full-universe guarantee. The calendar is a bounded evidence view, not a complete historical exchange-session register.

### Current equity identity snapshot

The 281-symbol equity candidate set has a current-snapshot match of 281/281 against the dated 2026-11-25 security-ID snapshot. This is an as-of identity crosswalk only. It does not establish historical predecessor IDs, effective-dated symbol continuity, or `valid_from` for the full universe. Nine of 281 lifecycle starts have recorded evidence in the current crosswalk; 272 remain unknown. No lifecycle date is inferred from the earliest OHLCV row.

## Remaining blockers

1. Obtain and preserve original NEPSE notices/records that establish the historical weekly schedule transitions and verify their effective dates. Secondary corroboration is not a substitute for immutable primary notice capture.
2. Resolve annual completeness and scope for the 2015–2026 holiday API payloads; specifically investigate truncated-looking 2018/2019 ranges and the two distinct 2020-04-13 closure reasons.
3. Establish actual open sessions using date-level positive exchange trading observations or complete, validated market/floorsheet records. Do not infer open sessions from weekdays or absence from the holiday API.
4. Obtain an authoritative effective-dated instrument/security master with stable security IDs, symbol/name history, instrument type and listing/delisting/suspension boundaries. The current security-list snapshot is not a historical master.
5. Reconcile all 281 equities against the evidence-backed calendar and instrument lifecycle intervals, keeping ambiguous records quarantined.

## Safeguards

- No weekday-only promotion to `verified_open`.
- No `NO_TRADE` inference from missing or incomplete floorsheets.
- No lifecycle `valid_from` inferred from first OHLCV file row.
- No current security ID backfilled onto predecessor symbols.
- No canonical OHLCV promotion, training eligibility or BUY eligibility from unverified reference data.

## Disposition

**Validation framework and multi-year holiday capture acquisition are in place. Historical calendar and effective-dated instrument-master acceptance remain OPEN.** This status refresh corrects the earlier stale evidence inventory; it does not claim completion of issue #4.
