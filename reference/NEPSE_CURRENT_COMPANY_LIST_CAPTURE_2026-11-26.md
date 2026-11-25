# NEPSE current company-list snapshot and 525-file comparison — 2026-11-26

## Source and scope
- Source: official NEPSE Company page, https://nepalstock.com.np/company
- Captured: 2026-11-26, through the rendered public browser table.
- First-pass table: 281 rows, parsed into 278 unique symbols. The parsed rows include duplicate USLB and SYPNL entries and duplicate company-detail route IDs.
- A later structured pass reported 281 unique equity symbols with no duplicates, but its exposed row-level payload contained only the first 20 rows. These capture outputs conflict.
- A separate instrument-filter pass reported 281 active Equity rows and 47 active Mutual Funds (328 total active rows); Preference Shares and Non-Convertible Debentures filters returned 0 rows. Suspended/Delisted rows were not extracted.
- The exact backing XHR endpoint and raw API payload were not captured.
- Numeric `/company/detail/{id}` values are company-detail route IDs, not verified stable NEPSE security IDs.

## Full historical-file comparison
- OHLCV files: 525.
- First-pass current equity unique symbols: 278.
- First-pass OHLCV filenames matching those equity symbols: 278.
- First-pass filenames not matching those equity symbols: 247.
- Structured mutual funds: 47 unique symbols; 46 match OHLCV files; NICEF has no OHLCV file.
- The first-pass comparison is provisional because the later equity capture reported a different unique-symbol count. Do not treat 201 residual unmatched files (after subtracting mutual-fund matches) as unknown securities.

## Duplicate and identifier anomalies
- First-pass extraction reported USLB twice and SYPNL three times.
- It assigned route ID 2917 to both CGH and CHDC, and 9166 to both MAKAR and BENH.
- The later structured pass reported no duplicates, so these are unresolved capture inconsistencies, not confirmed NEPSE duplicates.
- No stable securityId field was captured for equities.

## Canonical-data policy
Do not populate the official instrument register from this company-list snapshot alone. Do not mark unmatched files as unknown, inactive, delisted or renamed. Obtain the complete NEPSE security register with stable IDs and historical lifecycle fields before promotion.
