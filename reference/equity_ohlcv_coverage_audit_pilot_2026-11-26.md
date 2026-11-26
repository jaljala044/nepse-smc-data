# Equity OHLCV Coverage Audit — 10-Symbol Pilot
**Audit date:** 2026-11-26  
**Repository audited:** `jaljala044/nepse-history-starter`  
**Data path:** `03_stock_charts_ohlcv/{SYMBOL}_OHLCV.csv`  
**Universe scope:** Common equities only. Mutual funds, debt instruments, bonds/debentures, and promoter-share classes are excluded.

## Scope and method

This is a pilot audit of 10 equity files, not a completed 281-equity archive audit. The files were read from the repository's `main` branch. For each file the audit counted data rows, earliest/latest date, duplicate dates, basic OHLC consistency failures, zero-volume rows, Saturday-dated rows, and Saturday rows whose complete OHLCV tuple exactly matched the preceding row.

Basic OHLC check: all Open/High/Low/Close/Volume fields must parse as finite numbers; High must be at least Open, Close, and Low; Low must be no greater than Open, Close, and High. This does not validate source accuracy or whether a row represents a real executed trading session.

## Per-symbol results

| Symbol | Rows | First date | Last date | Duplicate dates | Invalid OHLC rows | Zero-volume rows | Saturday rows | Saturday exact carry-forwards |
|---|---:|---|---|---:|---:|---:|---:|---:|
| ACLBSL | 934 | 2024-03-05 | 2026-11-20 | 0 | 0 | 0 | 122 | 121 |
| ADBL | 935 | 2024-03-04 | 2026-11-20 | 0 | 0 | 0 | 122 | 121 |
| AHL | 936 | 2024-03-04 | 2026-11-20 | 0 | 0 | 0 | 122 | 121 |
| AHPC | 936 | 2024-03-04 | 2026-11-20 | 0 | 0 | 0 | 122 | 121 |
| AKJCL | 936 | 2024-03-04 | 2026-11-20 | 0 | 0 | 0 | 122 | 121 |
| API | 935 | 2024-03-04 | 2026-11-20 | 0 | 0 | 0 | 122 | 121 |
| BGWT | 935 | 2024-03-04 | 2026-11-20 | 0 | 0 | 0 | 122 | 121 |
| HRL | 935 | 2024-03-04 | 2026-11-20 | 0 | 0 | 0 | 122 | 121 |
| ULHC | 936 | 2024-03-04 | 2026-11-20 | 0 | 0 | 0 | 122 | 121 |
| YMHL | 97 | 2026-06-22 | 2026-11-20 | 0 | 0 | 0 | 2 | 1 |

## Findings

1. **No duplicate dates** were found in this 10-file sample.
2. **No basic OHLC consistency failures** were found.
3. **No zero-volume rows** were found.
4. The nine established-symbol files each contain 122 Saturday-dated rows. In each file, 121 Saturday rows have an OHLCV tuple identical to the immediately preceding row.
5. YMHL has two Saturday-dated rows, one identical to the immediately preceding row.
6. The repeated Saturday rows are a material warning of calendar-day carry-forward or non-session data. They must not be treated as confirmed executed trading sessions without source evidence.
7. This audit does not yet calculate missing valid trading sessions: that requires a validated NEPSE session calendar, including exceptional closures. It also does not verify every price/volume against ShareHub, Chukul, ShareSansar, or NepseAlpha.

## Recommended next actions

- Build and validate the NEPSE open-session calendar using accepted evidence sources.
- Check the Saturday-dated records against provider chart/floorsheet evidence and determine whether they are synthetic carry-forwards.
- Keep raw source rows immutable; create a separately labelled cleaned/eligible-session view rather than deleting or silently rewriting data.
- Extend this same audit to all 281 provisional equity symbols and both repositories.
- Calculate first/last eligible session, expected-session gaps, per-symbol coverage ratio, and source provenance after the calendar is approved.

## Status

**Pilot completed: 10 symbols inspected.**  
**Full equity archive audit: pending.**  
**No raw OHLCV data was changed by this audit.**

## Evidence and reproducibility

The audited CSVs are publicly available in the repository:

- [ACLBSL](https://github.com/jaljala044/nepse-history-starter/blob/main/03_stock_charts_ohlcv/ACLBSL_OHLCV.csv)
- [ADBL](https://github.com/jaljala044/nepse-history-starter/blob/main/03_stock_charts_ohlcv/ADBL_OHLCV.csv)
- [AHL](https://github.com/jaljala044/nepse-history-starter/blob/main/03_stock_charts_ohlcv/AHL_OHLCV.csv)
- [AHPC](https://github.com/jaljala044/nepse-history-starter/blob/main/03_stock_charts_ohlcv/AHPC_OHLCV.csv)
- [AKJCL](https://github.com/jaljala044/nepse-history-starter/blob/main/03_stock_charts_ohlcv/AKJCL_OHLCV.csv)
- [API](https://github.com/jaljala044/nepse-history-starter/blob/main/03_stock_charts_ohlcv/API_OHLCV.csv)
- [BGWT](https://github.com/jaljala044/nepse-history-starter/blob/main/03_stock_charts_ohlcv/BGWT_OHLCV.csv)
- [HRL](https://github.com/jaljala044/nepse-history-starter/blob/main/03_stock_charts_ohlcv/HRL_OHLCV.csv)
- [ULHC](https://github.com/jaljala044/nepse-history-starter/blob/main/03_stock_charts_ohlcv/ULHC_OHLCV.csv)
- [YMHL](https://github.com/jaljala044/nepse-history-starter/blob/main/03_stock_charts_ohlcv/YMHL_OHLCV.csv)
