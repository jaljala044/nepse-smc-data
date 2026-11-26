# BENH Listing and First-Trade Validation — 2026-11-26

## Finding

BENH's 7.11% observed-date overlap is explained primarily by its late-2026 listing/trading commencement, not by a two-year OHLCV archive gap.

- ShareSansar reports NEPSE listed 10,400,000 BENH IPO shares on 2026-10-13 and regular trading would commence on 2026-10-14; first-transaction opening range NPR 91.27–273.81.
- The project archive starts BENH OHLCV on 2026-10-15.
- ArthaKendra and Sun Securities show first executed OHLCV row on 2026-10-15: O 273, H 313.9, L 273, C 313.9, volume 90.
- Therefore the 2025-11-25 to 2026-11-20 reference-calendar dates before BENH's listing/trading start are structurally out of scope for BENH. The first listed trading day 2026-10-14 should be checked for whether an execution occurred; no evidence in the reviewed pages establishes a trade on that date.

## Evidence / source links

- ShareSansar listing notice: https://www.sharesansar.com/index.php/eventdetail/listing-ipo-share-of-beni-hydropower-project-limited-benh-2026-10-13
- Merolagani announcement: https://eng.merolagani.com/NewsDetail.aspx?newsID=131801
- ArthaKendra price history: https://www.arthakendra.com/stock-market/company/BENH/price-history
- Sun Securities price history: https://sunsecurities.com/company/BENH/price-history
- Project file: `jaljala044/nepse-smc-data/03_stock_charts_ohlcv/BENH_OHLCV.csv`

## Disposition

- Reclassify BENH from unexplained low overlap to **late-listing / short trading history**.
- Do not count dates before first trading commencement in its expected-session denominator.
- Retain 2026-10-14 as a one-session first-trade verification question; the first confirmed executed row in the reviewed archive/provider histories is 2026-10-15.
- No OHLCV mutation or canonical/training promotion.
