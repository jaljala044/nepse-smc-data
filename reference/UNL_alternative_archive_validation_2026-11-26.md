# UNL alternative archive validation — 2026-11-26

Source: https://github.com/srijankarki07/nepse-data/blob/main/data/series/UNL.csv
Source blob SHA: 83b1eb2c1af38f4661d14c6dd0a3f30c863e5d54

Retrieved 2,016 rows, 2011-03-28 through 2026-11-26. No duplicate date keys. 360 rows fail finite numeric/OHLC/volume invariants; 11 fail project weekday regime; combined failures 370 (one overlap). 1,646 pass these preliminary checks, including 1,055 of 1,424 pre-2024 rows. Compared to history-starter UNL_OHLCV.csv: 545 overlapping dates, all 545 exact numeric OHLCV matches. Source identifies ShareSansar lineage; not independent corroboration. Weekday checks are not holiday or executed-session verification. No adjustment, licensing or redistribution rights verified. No raw source copied into project or canonical data changed.

Disposition: historical recovery remains OPEN; UNL remains QUARANTINED for historical signals/backtests/training. Recommend non-blocking exclusion from eligible scanner universe while preserving instrument in market/watchlist. Do not repair old open values by assuming previous close or shift dates. Investigate independent executed floorsheet or licensed settled candle history before promotion. This report documents preliminary validation only, not runtime enforcement.
