# Five-stock evidence reconciliation — 2025-07-28

**Symbols:** BGWT, MEHL, RAWA, RHGCL, ULHC  
**Controlling evidence:** user-supplied `NEPSE_Floorsheet_Evidence.xlsx` and `NEPSE_Chart_Evidence.pdf`.  
**Source identity:** ShareHub daily price history and ShareHub floorsheet, as documented in the supplied PDF. These are third-party ShareHub records, not official NEPSE raw files.

## 1. Corrected canonical OHLCV and floorsheet totals

| Symbol | Open | High | Low | Close | Volume (shares) | Turnover (NPR) | Trades | Pages |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| BGWT | 940.00 | 992.00 | 933.40 | 957.17 | 14,028 | 13,256,345.00 | 194 | 2 |
| MEHL | 471.10 | 480.50 | 460.00 | 475.63 | 29,753 | 14,008,898.10 | 333 | 4 |
| RAWA | 796.00 | 811.00 | 780.30 | 796.90 | 3,165 | 2,515,662.50 | 74 | 1 |
| RHGCL | 346.70 | 362.00 | 341.40 | 357.05 | 296,715 | 103,872,614.40 | 1,030 | 11 |
| ULHC | 509.00 | 515.00 | 495.00 | 510.75 | 32,288 | 16,273,342.10 | 300 | 3 |

The five rows sum to **375,949 shares**, **NPR 149,926,862.10 turnover**, and **1,931 trades** across **21 floorsheet pages**.

## 2. Verification notes

- The workbook contains the individual contract rows, page boundaries and five-minute bars for API and HRL. The supplied evidence summary states that 31 ShareHub pages yielded 2,793 distinct contract IDs across the seven stock-date records in the evidence package.
- Contract-level amount is calculated as quantity multiplied by contract rate; turnover is summed from individual contract amounts to two decimal places.
- The floorsheet footer rounds turnover to whole rupees. This explains sub-rupee differences against rounded displays in other sources.
- The 14:45–15:00 Nepal-time volume-weighted price rounds to the published close for each of the five July stocks.
- One BGWT contract traded at NPR 925.00, below the published daily low of NPR 933.40. It remains included in the contract total and is flagged as an out-of-range print, not silently discarded.
- The chart screenshots are on PDF pages 4–8. The five-stock summary and reconciliation notes are on PDF page 1; the intraday trade plots are on PDF page 2.

## 3. Superseded values and correction

The prior BGWT OHLCV row in `03_stock_charts_ohlcv/BGWT_OHLCV.csv` was:
`2025-07-28,824.56,870.18,818.77,839.62,14028.0`

It is superseded by the supplied ShareHub chart evidence:
`2025-07-28,940.00,992.00,933.40,957.17,14028.0`

The previously recorded Merolagani/Nepse Alpha source comparison and the old claim that BGWT/ULHC chart values were unresolved are superseded for this five-stock task by the newer, directly supplied ShareHub evidence package. Do not mix the obsolete values into the canonical time series.

## 4. Data provenance and limits

| Component | Status |
|---|---|
| ShareHub daily OHLC for five stocks | Confirmed by supplied chart screenshots and summary |
| ShareHub floorsheet volume and turnover | Reconciled to supplied contract workbook |
| Trade count and page counts | Supplied workbook/PDF summary |
| Intraday closing-window VWAP check | Reported as passing in supplied evidence |
| Official NEPSE raw-source confirmation | Not established by these ShareHub files |

**Canonical project decision:** use the five OHLCV and floorsheet totals in Section 1 for 2025-07-28. Set their source to ShareHub and verification status to `user_supplied_evidence_reconciled`. Retain the BGWT NPR 925.00 print as an explicit range exception. Do not label these records official-NEPSE-verified.
