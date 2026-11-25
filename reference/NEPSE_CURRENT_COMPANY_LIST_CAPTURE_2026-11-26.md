# NEPSE current company-list snapshot and 525-file comparison — 2026-11-26

## Source and scope
- Source: official NEPSE Company list page, https://nepalstock.com.np/company
- Captured: 2026-11-26, through the rendered public browser table.
- Displayed rows: 281.
- Displayed fields: row number, company/security name, symbol, status, sector, instrument label, and company-detail route ID.
- The UI showed 281 rows with status Active and instrument Equity.
- The exact backing XHR endpoint was not captured. This is a rendered page capture, not a raw API payload.
- The numeric value in `/company/detail/{id}` is stored as a company-detail route ID. It is **not accepted as a stable NEPSE security ID**.

## Full historical-file comparison
- OHLCV files in `03_STOCK_CHARTS_OHLCV`: 525.
- Current company-list unique symbols: 278.
- OHLCV filenames with a current company-list symbol match: 278.
- OHLCV filenames without a current company-list symbol match: 247.
- This is a current company-list membership comparison only. An unmatched ticker may be a debt/debenture, mutual fund, promoter/preference class, delisted or renamed instrument, or a data naming issue. No such classification is assigned without evidence.

## Duplicate and identifier anomalies preserved
- `USLB` appears twice with different company-detail route IDs (2774 and 8063).
- `SYPNL` appears three times with the same company-detail route ID (9303).
- Company-detail route ID `2917` is assigned in the table to both `CGH` and `CHDC`.
- Company-detail route ID `9166` is assigned in the table to both `MAKAR` and `BENH`.
- These conflicts mean the rendered company-detail route ID cannot be treated as a globally unique security ID from this capture.

## Canonical-data policy
- Do not populate the official instrument register from this company-list snapshot alone.
- Do not mark the 247 unmatched files as unknown securities; they remain unclassified.
- Do not infer listing/delisting dates, symbol rename dates, or historical active status from the current list.
- Obtain the full NEPSE security-list response with its actual `securityId`, instrument type and lifecycle fields (or equivalent authoritative historical evidence) before promotion.
