# P4.30 — derived OHLCV v2 integrity gate

Date: 2026-11-26  
Status: `INTEGRITY_CHECKED_WITH_RETAINED_FLAGS`  
Dataset: [derived OHLCV v2 release](derived_ohlcv_v2_release_2026-11-26.md)

## Verified structure and provenance

| Check | Result |
|---|---:|
| Symbols audited | 281 |
| Derived rows | 246,238 |
| Raw source Git blob hashes verified | 281/281 |
| Official NEPSE provenance rows verified in v2 | 599/599 |
| Duplicate-date flags | 0 |
| Date-order flags | 0 |
| Raw source files modified | 0 |
| Automatic repairs/deletions | 0 |

The 599 official rows still match the v2 derived rows exactly. The correction ledger remains consistent: 490 Date changes, 109 Row insertions, 109 Open corrections, 3 new Close corrections, plus the earlier RHGCL Close and Volume corrections.

## OHLCV invariant audit

There are **1,329 unique invalid symbol/date rows** across 13 symbols, represented by 1,379 individual invariant flags (50 additional reasons overlap rows already flagged).

| Invariant reason | Flag count |
|---|---:|
| Open outside High–Low range | 1,325 |
| Close outside High–Low range | 28 |
| High below Low | 22 |
| Nonpositive price | 4 |

Largest concentrations are AHPC 607, SKBBL 381, API 123, MERO 105, SPDL 73, CHL 48 and HIDCL 32. Remaining flagged symbols: RADHI 2, RAWA 2, UAIL 2, UNHPL 2, BGWT 1 and HRL 1.

These rows are not interpolated or silently repaired. They must be excluded from technical indicators until individual primary evidence validates them. The 1,329 unique rows are not equivalent to 1,329 independent data-source conflicts.

## Adjacent repeated OHLCV audit

There are **71,806 adjacent identical OHLCV rows** across 256 symbols:

| Classification | Rows | Disposition |
|---|---:|---|
| Verified closed-session repeat candidates | 18,910 | Exclude from regular-session indicators; retain raw evidence |
| Outside calendar evidence window | 52,891 | UNKNOWN; do not infer session status |
| Open-session repeat review | 5 | UNKNOWN pending per-security floorsheet |

The five open-session repeat pairs all have volume 10 and identical adjacent OHLCV:

| Symbol | Previous row | Repeated row |
|---|---|---|
| BNL | 2026-11-13 | 2026-11-17 |
| BNT | 2026-06-29 | 2026-07-01 |
| ENL | 2026-08-25 | 2026-08-26 |
| UNL | 2026-08-24 | 2026-08-27 |
| UNL | 2026-09-28 | 2026-09-29 |

The calendar's positive open observations are based on a sampled security, not proof that each of these symbols traded. In particular, **UNL remains UNKNOWN** until its exact official floorsheet records are reconciled. Do not classify these repeats as NO_TRADE or delete them.

## Calendar coverage

The current canonical calendar covers 2025-11-25 through 2026-12-30. It produced 185,643 calendar flags: 18,910 rows on verified closed dates and 166,733 rows outside the calendar evidence window. Outside-window rows remain UNKNOWN.

The regular equity schedule represented in this calendar is Sunday–Thursday before 2026-04-06, with Friday/Saturday closed; from 2026-04-06, Monday–Friday with Saturday/Sunday closed. The 2022 six-day Friday schedule was a temporary exception and is not evidence that Fridays were regular sessions throughout 2025–early 2026. The April 2026 NEPSE schedule notice describes the prior regular schedule as Sunday–Thursday; see [NEPSE's 2026 schedule notice as reported by Ratopati](https://english.ratopati.com/story/57946/stock-market-now-trades-from-monday-to-friday) and the [2022 temporary six-day announcement](https://english.khabarhub.com/2022/13/257305/).

The calendar is not a full per-security trade calendar. A market-wide candidate weekday or a sampled-security observation must not be promoted to a specific symbol's trade proof.

## Corporate-action coverage

- Current corporate_actions.csv contains 3 event records across 3 symbols.
- 278/281 symbols have no action record in this partial file. Absence is not evidence that no bonus, rights, split or dividend action occurred.
- One NLIC split proposal is recorded, but its effective date is not verified; no split factor is applied.
- V2 is a raw/unadjusted EOD series. Long-horizon return, RS and moving-average calculations must not assume complete corporate-action adjustment.

## Scanner gate

- T+2/swing: conditional use of individually valid, sufficiently liquid bars only; repeated rows require source-aware filtering.
- Positional/investment: not ready for adjusted-return metrics until corporate-action history and price basis are validated.
- Invalid OHLCV rows: exclude from indicators and retain UNKNOWN until primary evidence.
- Open-session repeats: UNKNOWN pending exact symbol/date floorsheet checks.

## Reproducibility

- Audit: `tools/audit_derived_ohlcv_v2.py`
- Tests: `tools/tests/test_audit_derived_ohlcv_v2.py`
- CI run: [45868691178](https://github.com/jaljala044/nepse-smc-data/actions/runs/45868691178)
- Full audit artifact: [15141173903](https://github.com/jaljala044/nepse-smc-data/actions/runs/45868691178/artifacts/15141173903)
- Artifact SHA-256: `8087fc00c32e585e66bda3bca33302bda4d52917953147fef3344e776ce356d9`

## Next priority — P4.31

Capture complete official NEPSE company floorsheets for both dates in each of the five open-session repeat pairs. Reconcile contract counts, quantities and rates to the EOD rows. Keep any missing, incomplete or mismatching pair UNKNOWN. Then extend calendar evidence and corporate-action coverage without inferring missing sessions or action factors.
