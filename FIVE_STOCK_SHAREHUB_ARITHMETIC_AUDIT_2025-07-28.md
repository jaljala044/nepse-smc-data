# Independent arithmetic audit of supplied ShareHub evidence — 2025-07-28

Audit performed: 2026-11-26  
Input: user-supplied `NEPSE_Floorsheet_Evidence.xlsx` and `NEPSE_Chart_Evidence.pdf`  
Repositories: `jaljala044/nepse-smc-data`, `jaljala044/nepse-history-starter`

## Scope and evidence status

This audit independently recalculates arithmetic and internal consistency from the supplied workbook. It does not independently retrieve the ShareHub pages or NEPSE raw records. Accordingly, the result is **ShareHub evidence reconciled from the user's supplied capture**, not official NEPSE verification.

## Recomputed July totals

| Symbol | Open | High | Low | Close | Shares | Turnover (NPR) | Trades | Pages | Closing-window VWAP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BGWT | 940.00 | 992.00 | 933.40 | 957.17 | 14,028 | 13,256,345.00 | 194 | 2 | 957.17 |
| MEHL | 471.10 | 480.50 | 460.00 | 475.63 | 29,753 | 14,008,898.10 | 333 | 4 | 475.63 |
| RAWA | 796.00 | 811.00 | 780.30 | 796.90 | 3,165 | 2,515,662.50 | 74 | 1 | 796.90 |
| RHGCL | 346.70 | 362.00 | 341.40 | 357.05 | 296,715 | 103,872,614.40 | 1,030 | 11 | 357.05 |
| ULHC | 509.00 | 515.00 | 495.00 | 510.75 | 32,288 | 16,273,342.10 | 300 | 3 | 510.75 |
| **Total** | | | | | **375,949** | **149,926,862.10** | **1,931** | **21** | |

## Checks executed

1. Read all 2,793 contract rows across the seven stock-date pairs in the workbook.
2. All 2,793 contract IDs are unique; no duplicate IDs were found.
3. For every contract in all seven stock-date pairs, `shares × rate = amount` to two decimal places; zero mismatches.
4. For the five July symbols, independently recomputed quantity, turnover, trade count, and distinct page count. Every result matches the workbook's daily summary and published totals.
5. All 21 July page-log entries have the stated row count and first/last contract IDs when compared in the workbook's chronological row order (the page log records newest-first, while the full-contract sheet is oldest-first).
6. All five OHLC tuples pass the logical range constraint `low ≤ open, close ≤ high`.
7. Independently recalculated VWAP from trades between 14:45:00 and 15:00:00 Nepal time. Rounded to two decimals, it equals the published close for all five stocks.
8. Found one July trade outside the published daily range: BGWT contract `2025072801025823`, 1 share at NPR 925.00, below the published low of NPR 933.40. It is retained in volume and turnover; it is not silently removed.

## Cross-repository correction

The five 2025-07-28 OHLCV rows were aligned in both repositories:
- `jaljala044/nepse-smc-data/03_stock_charts_ohlcv/{BGWT,MEHL,RAWA,RHGCL,ULHC}_OHLCV.csv`
- `jaljala044/nepse-history-starter/03_stock_charts_ohlcv/{BGWT,MEHL,RAWA,RHGCL,ULHC}_OHLCV.csv`

Each file was read back from the default branch after the write. Both repositories now contain the same five confirmed OHLC and volume values (formatting differs only).

## Disposition

**Closed subtask:** five-stock ShareHub chart/floorsheet arithmetic reconciliation and cross-repository consistency.

**Still not proven:** the workbook's page captures were not independently re-downloaded from ShareHub during this audit; no official NEPSE raw contract feed or official historical daily-price response was obtained. The workbook's statement that contract records were compared to another archive is source documentation, not an independent comparison performed in this audit.

**Canonical source label:** `ShareHub / user-supplied capture / arithmetic-reconciled`.  
**Do not label:** `official NEPSE verified`.

The broader Issue #4 requirements (complete historical NEPSE session calendar and effective-dated official instrument master) remain open and must not be closed on the strength of this five-stock subtask.
