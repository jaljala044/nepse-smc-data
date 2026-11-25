# OHLCV discrepancy reconciliation — 2026-11-19

Review date: 2026-11-26

## Resolution

The user supplied the final OHLCV and floorsheet totals for API and HRL on 2026-11-19. These values are accepted as the project basis, following the same user-finalization rule previously applied to BGWT, MEHL, RAWA, RHGCL, and ULHC.

| Symbol | Open | High | Low | Close | Quantity | Turnover (Rs.) | Calculated VWAP |
|---|---:|---:|---:|---:|---:|---:|---:|
| API | 331.00 | 334.20 | 330.00 | 331.80 | 105,340 | 34,929,701 | 331.59 |
| HRL | 483.00 | 488.00 | 483.90 | 483.90 | 49,184 | 23,836,472 | 484.64 |

### Source and interpretation

- Values above are user-supplied and accepted as final for this project.
- Quantity and turnover are the user's supplied floorsheet totals.
- VWAP is calculated as turnover divided by quantity; it is not substituted for the chart close.
- The existing project OHLCV rows have been updated to the user-finalized OHLCV and volume values.
- The imported-history values are retained as historical comparison evidence; they are not treated as the final values for these records.
- No claim is made that the figures were independently verified against NEPSE.

## Earlier discrepancies now closed

The user-finalized records are:
- API — 2026-11-19
- HRL — 2026-11-19
- BGWT — 2025-07-28
- MEHL — 2025-07-28
- RAWA — 2025-07-28
- RHGCL — 2025-07-28 (including the previously flagged comparison rows)
- ULHC — 2025-07-28

**Remaining unresolved discrepancies in this tracked set: 0.**

## Next action

Resume the exchange-session calendar and instrument-register work tracked in issue #4:
https://github.com/jaljala044/nepse-smc-data/issues/4
