# ShareSansar Source Corroboration of OHLC Invariant Flags — 2026-11-26

## Purpose

The 281-equity structural audit identified 1,329 rows in the SMC repository where reported OHLC fields violate the mathematical invariant:

- High >= max(Open, Low, Close)
- Low <= min(Open, High, Close)

This evidence review tests whether these values were introduced by the repository or are already present in the accepted upstream source archive.

## Source

The comparison source is [shawinCreates/Nepse-Market-Data](https://github.com/shawinCreates/Nepse-Market-Data), whose README states that its date-stamped daily-price CSV files are scraped from ShareSansar's NEPSE daily price data and include per-stock OHLCV. The source file links are recorded row by row in the accompanying CSV.

## Results

**13 out of 13 sampled rows match exactly** between the SMC raw OHLCV file and the ShareSansar-derived daily-price archive, including Open, High, Low, Close and Volume.

Sampled symbols: AHPC, SKBBL, API, MERO, SPDL, CHL, HIDCL, RADHI, RAWA, UAIL, UNHPL, BGWT and HRL.

Examples:
- SKBBL, 2013-10-09: Open 605, High 665, Low 617, Close 665, Volume 16,506.
- API, 2015-11-18: Open 0, High 307, Low 301, Close 307, Volume 52.
- MERO, 2016-09-05: Open 0, High 392, Low 392, Close 392, Volume 10.
- SPDL, 2017-05-17: Open 246, High 265, Low 250.92, Close 265, Volume 40.
- RAWA, 2026-04-27: Open 648.7, High 645, Low 625, Close 630, Volume 3,747.

The complete 13-row comparison is in `reference/shareSansar_source_corroboration_ohlc_flags_2026-11-26.csv`.

## Interpretation

1. The 13 sampled OHLC invariant violations are **source-corroborated**, not discrepancies created by the SMC repository. The same five OHLCV values appear in the ShareSansar-derived archive.
2. This does not prove all 1,329 flagged rows are correct. It establishes that the invariant failures cannot be blindly "fixed" by editing SMC data and that at least a meaningful sample is inherited from the provider's published values.
3. A zero Open may represent a source-reported missing/zero field, not a tradable zero price. Do not replace it with previous close or any guessed value.
4. A provider-reported High below Open or Low above Open remains mathematically inconsistent. Preserve the raw values and tag them as `source_reported_ohlc_invariant_violation` until a separate source with stronger row-level evidence resolves the discrepancy.
5. The ShareSansar archive is a secondary scrape/mirror, not an exchange-origin source. It corroborates the provider publication, but is not independent proof of actual trades.

## Decision

- Keep all raw files unchanged.
- Do not auto-correct the 1,329 SMC OHLC invariant flags.
- Record source corroboration and row-level URLs in the evidence CSV.
- Treat these rows as provider-reported anomalies for quality gating.
- Continue resolving the 23 divergent repository pairs separately; matching source values on selected dates does not establish that either full history is canonical.

## Links

- [13-row evidence CSV](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/shareSansar_source_corroboration_ohlc_flags_2026-11-26.csv)
- [ShareSansar-derived archive README and source description](https://github.com/shawinCreates/Nepse-Market-Data/blob/main/README.md)
- [ShareSansar AHPC company page](https://www.sharesansar.com/company/ahpc)
