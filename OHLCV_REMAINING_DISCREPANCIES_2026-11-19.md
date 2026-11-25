# Remaining OHLCV discrepancies after user-finalized records

Review date: 2026-11-26

## Scope

Compared the existing `nepse-smc-data/03_stock_charts_ohlcv` histories against the imported `nepse-history-starter/03_stock_charts_ohlcv` histories on shared trading dates, using numeric field comparisons (not string formatting).

The user has explicitly accepted their own data as final for the 2025-07-28 records for BGWT, MEHL, RAWA, RHGCL, and ULHC. Those five symbols are excluded from this remaining-discrepancy queue, regardless of earlier A/B/C source conflicts.

## Remaining unresolved symbols

| Symbol | Date | Existing OHLCV (O,H,L,C,Volume) | Imported OHLCV (O,H,L,C,Volume) | Difference |
|---|---|---|---|---|
| API | 2026-11-19 | 331, 334.2, 330.2, 333, 26717 | 331, 334.2, 330, 331.8, 105340 | Low, close, volume |
| HRL | 2026-11-19 | 483, 488, 480, 486, 18817 | 483, 488, 480, 483.9, 49184 | Close, volume |

## Result

- Remaining symbols requiring review: **2** (API, HRL).
- Remaining differing symbol-date rows: **2**, both dated 2026-11-19.
- User-finalized symbols excluded: BGWT, MEHL, RAWA, RHGCL, ULHC.
- No values have been silently overwritten. Both versions are preserved pending a decision on the correct source/price basis.

## Next action

Resolve API and HRL for 2026-11-19 by inspecting the source records and provenance for that date. Do not change either OHLCV file until the source basis is established. Then resume the exchange-session calendar and instrument-register work tracked in issue #4.
