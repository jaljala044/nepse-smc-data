# Seven stock-date ShareHub evidence audit

Audit date: 2026-11-26  
Evidence files: `NEPSE_Floorsheet_Evidence.xlsx` and `NEPSE_Chart_Evidence.pdf`  
Source: ShareHub, as documented in the supplied evidence package.

## Seven stock-date records

| Date | Symbol | Open | High | Low | Close | Shares | Turnover (NPR) | Trades | Pages |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025-07-28 | BGWT | 940.00 | 992.00 | 933.40 | 957.17 | 14,028 | 13,256,345.00 | 194 | 2 |
| 2025-07-28 | MEHL | 471.10 | 480.50 | 460.00 | 475.63 | 29,753 | 14,008,898.10 | 333 | 4 |
| 2025-07-28 | RAWA | 796.00 | 811.00 | 780.30 | 796.90 | 3,165 | 2,515,662.50 | 74 | 1 |
| 2025-07-28 | RHGCL | 346.70 | 362.00 | 341.40 | 357.05 | 296,715 | 103,872,614.40 | 1,030 | 11 |
| 2025-07-28 | ULHC | 509.00 | 515.00 | 495.00 | 510.75 | 32,288 | 16,273,342.10 | 300 | 3 |
| 2026-11-19 | API | 331.00 | 334.20 | 330.00 | 331.80 | 105,340 | 34,929,701.30 | 442 | 5 |
| 2026-11-19 | HRL | 483.00 | 488.00 | 480.00 | 483.90 | 49,184 | 23,836,472.40 | 420 | 5 |

## Independent arithmetic checks from the supplied workbook

- 2,793 trade rows across seven stock-date pairs.
- 2,793 unique contract IDs; zero duplicate IDs.
- All 2,793 contract amounts equal shares multiplied by rate to two decimal places.
- All 31 page-log entries reconcile to the recorded row count and first/last contract IDs when accounting for opposite sort directions: page log newest-first, full-contract worksheet oldest-first.
- July five-stock totals independently recomputed: 375,949 shares, NPR 149,926,862.10 turnover, 1,931 trades, 21 pages.
- July closing-window VWAP (14:45–15:00 NPT) rounds to the published close for each of the five symbols.
- Seven trades are flagged outside the published daily range in the workbook and remain included in the contract totals. BGWT's July 28 below-low trade is 1 share at NPR 925.00.

## Corrections and repository alignment

The five July 28 OHLCV rows are now aligned in both `nepse-smc-data` and `nepse-history-starter`.

The supplied chart evidence also confirms API and HRL for 2026-11-19. API already matched in both repositories. HRL's low was inconsistent: `nepse-smc-data` had 483.90 while `nepse-history-starter` and the supplied evidence had 480.00. Corrected the SMC row to:
`2026-11-19,483.0,488.0,480.0,483.9,49184.0`
and read it back after commit.

## Limitations

This is an independent arithmetic and internal-consistency audit of the user's supplied ShareHub workbook/PDF, not an independent re-download of the ShareHub records and not official NEPSE raw-source verification. Preserve the source label as ShareHub/user-supplied capture/arithmetic-reconciled. Do not label these rows official NEPSE verified.
