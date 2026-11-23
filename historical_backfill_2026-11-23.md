# Historical backfill through November 20, 2026

The backfill uses [nepse-history-starter at 6ce90be](https://github.com/jaljala044/nepse-history-starter/tree/6ce90bef6889497203bbf5cc68dc6246947638a5).

- Added 500 stock history files with 279,007 OHLCV bars covering March 4, 2024 through November 20, 2026. Each file passed unique date, cutoff, OHLC, and nonnegative integer volume checks.
- Added scanner inputs with 195 market summaries, 138 benchmark records, 1,558 sector records, 105 index OHLC records, 1,390 index close records and 41 daily broker summaries. Each broker summary balances buyer and seller quantities and values by stock. See [source coverage and exceptions](scanner_inputs/README.md).
- Kept the 25 existing ticker histories. Eight of 14,856 overlapping rows differ in at least one OHLCV field. Dates missing from these existing files still require a price-basis review before merging.

| Existing file | Shared dates | Different OHLCV rows |
| --- | ---: | ---: |
| AHPC_OHLCV.csv | 613 | 0 |
| API_OHLCV.csv | 612 | 1 |
| BGWT_OHLCV.csv | 612 | 1 |
| CHL_OHLCV.csv | 614 | 0 |
| HDHPC_OHLCV.csv | 613 | 0 |
| HIDCL_OHLCV.csv | 613 | 0 |
| HLI_OHLCV.csv | 613 | 0 |
| HRL_OHLCV.csv | 612 | 1 |
| KDBY_OHLCV.csv | 608 | 0 |
| KEF_OHLCV.csv | 606 | 0 |
| MEHL_OHLCV.csv | 613 | 1 |
| MEL_OHLCV.csv | 613 | 0 |
| MERO_OHLCV.csv | 612 | 0 |
| NIFRA_OHLCV.csv | 614 | 0 |
| NRIC_OHLCV.csv | 614 | 0 |
| RADHI_OHLCV.csv | 613 | 0 |
| RAWA_OHLCV.csv | 611 | 1 |
| RHGCL_OHLCV.csv | 613 | 2 |
| SKBBL_OHLCV.csv | 613 | 0 |
| SMJC_OHLCV.csv | 613 | 0 |
| SOHL_OHLCV.csv | 160 | 0 |
| SPDL_OHLCV.csv | 613 | 0 |
| UAIL_OHLCV.csv | 611 | 0 |
| ULHC_OHLCV.csv | 614 | 1 |
| UNHPL_OHLCV.csv | 613 | 0 |
