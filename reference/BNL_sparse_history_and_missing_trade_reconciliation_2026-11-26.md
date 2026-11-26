# BNL Sparse History and Missing-Trade Reconciliation — 2026-11-26

## Executive finding

BNL is an active equity with very low turnover / infrequent small-lot trades, but the project's archived OHLCV is also missing at least one later executed trade observation. The latest project row is 2026-11-19; two independent third-party views report a 2026-11-23 trade of 10 shares at NPR 14,600. Therefore, BNL cannot be classified as purely no-trade sparsity: it has a **confirmed archive freshness/coverage gap at 2026-11-23**. A further 2026-11-24 trade is reported by one source only and remains provisional.

## Identity and raw archive

- Current snapshot row: `BNL, security ID 195, Bottlers Nepal (Balaju) Limited, status A, snapshot 2026-11-25`.
- Snapshot source SHA-256: `eed3bbb3152e83d4abcb0ee8d03d720c33c63cef`.
- Raw file: `03_stock_charts_ohlcv/BNL_OHLCV.csv`.
- Git blob SHA: `01bd01a6e8242b7c0f07143b2164de981b2b7ab6`.
- 605 rows; latest project row: 2026-11-19, O/H/L/C 14,100 / 14,840 / 14,100 / 14,840, volume 50.
- Raw file was not modified.

## Recent-session reconciliation

| Date | External record | OHLCV / volume | Evidence assessment | Archive status |
|---|---|---|---|---|
| 2026-11-19 | Project archive and external pages | O 14,100; H 14,840; L 14,100; C 14,840; V 50 | Matching observation | Present |
| 2026-11-23 | NepView and Sajilo Trading | O/H/L/C 14,600; V 10 | Two third-party pages agree on close and volume; Sajilo explicitly identifies this as last trade as of 25 Nov | **Missing from project archive** |
| 2026-11-24 | ArthaKendra | O/H/L/C 14,600; V 10 | One third-party history page reports this row; other pages' displayed recent-history lists omit it. Requires source-level confirmation | Missing; provisional candidate |
| 2026-11-25 | Hamroshare and Sajilo Trading | No trades / no volume; carried close 14,600 | Two pages report no trades on 25 Nov | Correctly no executed-trade OHLCV row expected |

The two-source confirmation of 23 November means the project file ending on 19 November is not current through the latest known trade. The 24 November row is not promoted because source agreement is insufficient.

## Historical suspension context

ShareSansar reports NEPSE suspended BNL trading on 17 December 2024 and lifted the suspension on 18 December 2024 after regulatory compliance. The project archive has a 16 December row and next observed row on 23 December. This event explains the 17 December suspension date and may explain a portion of the immediate gap; it does not explain the full 281-equity overlap deficit or every absent date. Do not infer no-trade / suspension for dates beyond the published notice.

## Liquidity and scanner treatment

- Merolagani reports 30-day average volume of 18 shares; ArthaKendra reports average daily volume of 35 shares over 120 trading days. The differing windows/methodologies are not directly comparable, but both indicate very low execution depth.
- Treat BNL as active but **very illiquid**. Exclude from normal BUY eligibility unless execution frequency, turnover, spread and depth meet the scanner's explicit liquidity floor.
- Carried-forward closes on no-trade dates are not fresh signals or executable prices.
- Do not forward-fill OHLCV. Preserve the raw source file; record any accepted repair as a separate versioned derived artifact with source, timestamp, row evidence and review.
- Do not use the experimental AI outlook / forecast figures displayed by third-party pages as project probabilities or backtest evidence.

## Sources

- NepView BNL price history, showing 23 Nov 2026 trade at 14,600, volume 10: https://nepview.com/explore/BNL
- Sajilo Trading BNL, showing 23 Nov trade at 14,600, volume 10 and no trade on 25 Nov: https://trading.sajiloapps.com/company/bnl
- ArthaKendra BNL price history, showing 24 Nov trade at 14,600, volume 10: https://www.arthakendra.com/stock-market/company/BNL/price-history
- Hamroshare BNL, 25 Nov 2026 no-trade status: https://hamroshare.com.np/company/bnl
- Merolagani BNL company details: https://eng.merolagani.com/CompanyDetail.aspx?symbol=BNL
- ShareSansar suspension and release, 17–18 Dec 2024: https://www.sharesansar.com/newsdetail/bottlers-nepal-limited-resumes-securities-trading-following-regulatory-compliance-2024-12-18
- Project OHLCV: `jaljala044/nepse-smc-data/03_stock_charts_ohlcv/BNL_OHLCV.csv`

## Disposition

**Confirmed:** one missing BNL trade observation for 2026-11-23 relative to the current project archive, supported by two third-party sources.  
**Provisional:** 2026-11-24 trade row, one source only.  
**No-trade:** 2026-11-25 supported by two third-party pages.  
**Liquidity:** poor; capital-preservation policy excludes ordinary BUY qualification.  
**Canonical / training:** no promotion and no raw OHLCV mutation pending source provenance and row-level reconciliation.
