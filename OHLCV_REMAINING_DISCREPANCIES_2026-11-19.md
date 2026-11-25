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

## Floorsheet aggregate totals

The user-finalized aggregate totals for API and HRL are also recorded in `FLOORSHEET_TOTALS_RECONCILIATION_2026-11-19.csv`. The earlier five user-finalized 2025-07-28 totals remain in `FLOORSHEET_TOTALS_RECONCILIATION_2025-07-28.csv`.

## Step disposition

The tracked OHLCV discrepancy reconciliation is complete: all seven flagged symbols are finalized by the user, and both updated OHLCV rows were re-fetched from GitHub after commit. User-supplied values are accepted as project-final but are not represented as independently verified NEPSE records.

## Next step

Proceed with the exchange-session calendar and instrument-register work tracked in issue #4. A partial 2026 official NEPSE holiday-API closure snapshot and its source manifest have been imported under `reference/`; this is not a complete historical calendar and contains no inferred open dates. The instrument register remains pending primary-source capture.
https://github.com/jaljala044/nepse-smc-data/issues/4


## Final read-back correction — 2026-11-26

A final repository read-back identified that the BGWT row for 2025-07-28 still contained the earlier conflicting OHLC values despite the user-finalized disposition above. This was corrected directly in `03_stock_charts_ohlcv/BGWT_OHLCV.csv` and read back successfully as:

`2025-07-28,824.56,870.18,818.77,839.62,14028.0`

The seven target rows were checked again during this review. All seven now match the user-finalized OHLCV values and quantities in the project files. This is a project-level user-authorized reconciliation, not a claim of independent NEPSE historical OHLC verification.
