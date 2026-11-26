# Equity OHLCV Coverage Audit — 10-Symbol Pilot
**Audit date:** 2026-11-26  
**Repository audited:** `jaljala044/nepse-history-starter`  
**Data path:** `03_stock_charts_ohlcv/{SYMBOL}_OHLCV.csv`  
**Universe scope:** Common equities only. Mutual funds, debt instruments, bonds/debentures, and promoter-share classes are excluded.

## Scope and method

This is a pilot audit of 10 equity files, not a completed 281-equity archive audit. The files were read from the repository's `main` branch. For each file the audit counted data rows, earliest/latest date, duplicate dates, basic OHLC consistency failures, zero-volume rows, and dates falling on the weekly closed days under the applicable NEPSE schedule.

Weekly schedule regimes applied:
- Before 2026-04-06: Sunday–Thursday trading; Friday and Saturday closed.
- From 2026-04-06: Monday–Friday trading; Saturday and Sunday closed.

The schedule transition is reported by ShareSansar as based on a NEPSE Board decision and NEPSE public notice, and by The Himalayan Times as effective 6 April 2026. See the [ShareSansar report, 8 April 2026](https://www.sharesansar.com/newsdetail/nepal-stock-exchange-opens-monday-to-friday-under-new-government-timings-2026-04-08) and [The Himalayan Times report, 8 April 2026](https://thehimalayantimes.com/business/nepse-shifts-to-mondayfriday-trading-week).

Basic OHLC check: all Open/High/Low/Close/Volume fields must parse as finite numbers; High must be at least Open, Close, and Low; Low must be no greater than Open, Close, and High. An exact carry-forward means all five OHLCV values match the immediately preceding row. This is a screening indicator, not proof of source fabrication.

## Per-symbol results

| Symbol | Rows | First date | Last date | Duplicate dates | Invalid OHLC rows | Zero-volume rows |
|---|---:|---|---|---:|---:|---:|
| ACLBSL | 934 | 2024-03-05 | 2026-11-20 | 0 | 0 | 0 |
| ADBL | 935 | 2024-03-04 | 2026-11-20 | 0 | 0 | 0 |
| AHL | 936 | 2024-03-04 | 2026-11-20 | 0 | 0 | 0 |
| AHPC | 936 | 2024-03-04 | 2026-11-20 | 0 | 0 | 0 |
| AKJCL | 936 | 2024-03-04 | 2026-11-20 | 0 | 0 | 0 |
| API | 935 | 2024-03-04 | 2026-11-20 | 0 | 0 | 0 |
| BGWT | 935 | 2024-03-04 | 2026-11-20 | 0 | 0 | 0 |
| HRL | 935 | 2024-03-04 | 2026-11-20 | 0 | 0 | 0 |
| ULHC | 936 | 2024-03-04 | 2026-11-20 | 0 | 0 | 0 |
| YMHL | 97 | 2026-06-22 | 2026-11-20 | 0 | 0 | 0 |

## Weekly closed-day row findings

| Symbol | Pre-2026-04-06 closed-day rows (Fri/Sat) | Exact carry-forwards | Post-2026-04-06 closed-day rows (Sat/Sun) | Exact carry-forwards |
|---|---:|---:|---:|---:|
| ACLBSL | 218 | 218 | 25 | 24 |
| ADBL | 218 | 218 | 25 | 24 |
| AHL | 218 | 218 | 25 | 24 |
| AHPC | 218 | 218 | 25 | 24 |
| AKJCL | 218 | 218 | 25 | 24 |
| API | 218 | 218 | 25 | 24 |
| BGWT | 218 | 218 | 25 | 24 |
| HRL | 218 | 218 | 25 | 24 |
| ULHC | 218 | 218 | 25 | 24 |
| YMHL | 0 | 0 | 3 | 2 |

## Findings and interpretation

1. No duplicate dates, basic OHLC consistency failures, or zero-volume rows were found in this 10-file sample.
2. Each of the nine established-symbol files has 218 rows dated on pre-transition weekly closed days (Friday/Saturday); **all 218 exactly repeat the preceding row's OHLCV**.
3. Each of those nine files has 25 rows dated on post-transition weekly closed days (Saturday/Sunday); 24 exactly repeat the preceding row.
4. YMHL has three post-transition closed-day rows, two exact carry-forwards.
5. One notable exception is ADBL on 2026-07-25 (Saturday): its OHLCV differs from the preceding row, which is dated 2026-07-23. This requires source-level verification; do not classify it as a valid session or delete it based on weekday alone.
6. These patterns strongly indicate that the archive contains calendar-day forward-filled rows on weekly closed days. They must not be counted as confirmed trading sessions unless corroborated by accepted provider evidence.
7. The weekday regime is only the base calendar. Public holidays, special closures, and one-off exchange notices still need a date-by-date exception calendar before expected-session gaps or coverage ratios can be calculated.
8. This pilot does not yet validate all OHLCV rows against ShareHub, Chukul, ShareSansar, or NepseAlpha.

## Recommended next actions

- Build the holiday/special-closure exception list from NEPSE notices and accepted provider evidence.
- Verify the non-carry-forward closed-day exceptions, starting with ADBL 2026-07-25, against provider chart/floorsheet evidence.
- Keep raw source rows immutable; create a separately labelled eligible-session view rather than deleting or silently rewriting data.
- Extend this audit to all 281 provisional equity symbols and both repositories.
- Calculate first/last eligible session, expected-session gaps, per-symbol coverage ratio, and source provenance only after the calendar is approved.

## Status

**Pilot completed: 10 symbols inspected.**  
**Weekly schedule baseline established; holiday exception calendar pending.**  
**Full equity archive audit: pending.**  
**No raw OHLCV data was changed by this audit.**

## Evidence and reproducibility

- [ACLBSL CSV](https://github.com/jaljala044/nepse-history-starter/blob/main/03_stock_charts_ohlcv/ACLBSL_OHLCV.csv)
- [ADBL CSV](https://github.com/jaljala044/nepse-history-starter/blob/main/03_stock_charts_ohlcv/ADBL_OHLCV.csv)
- [AHL CSV](https://github.com/jaljala044/nepse-history-starter/blob/main/03_stock_charts_ohlcv/AHL_OHLCV.csv)
- [AHPC CSV](https://github.com/jaljala044/nepse-history-starter/blob/main/03_stock_charts_ohlcv/AHPC_OHLCV.csv)
- [AKJCL CSV](https://github.com/jaljala044/nepse-history-starter/blob/main/03_stock_charts_ohlcv/AKJCL_OHLCV.csv)
- [API CSV](https://github.com/jaljala044/nepse-history-starter/blob/main/03_stock_charts_ohlcv/API_OHLCV.csv)
- [BGWT CSV](https://github.com/jaljala044/nepse-history-starter/blob/main/03_stock_charts_ohlcv/BGWT_OHLCV.csv)
- [HRL CSV](https://github.com/jaljala044/nepse-history-starter/blob/main/03_stock_charts_ohlcv/HRL_OHLCV.csv)
- [ULHC CSV](https://github.com/jaljala044/nepse-history-starter/blob/main/03_stock_charts_ohlcv/ULHC_OHLCV.csv)
- [YMHL CSV](https://github.com/jaljala044/nepse-history-starter/blob/main/03_stock_charts_ohlcv/YMHL_OHLCV.csv)
