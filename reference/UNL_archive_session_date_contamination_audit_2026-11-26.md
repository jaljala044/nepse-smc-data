# UNL archive session-date contamination audit — 2026-11-26

## Scope
Read-only audit of `jaljala044/nepse-history-starter/03_stock_charts_ohlcv/UNL_OHLCV.csv` as fetched from the repository default branch on 2026-11-26. No source file was edited. This is a date/calendar consistency check, not proof of the true execution date for any row.

## Input and baseline
- File header: `Date,Open,High,Low,Close,Volume`.
- Rows: 845.
- Date span: 2024-03-05 through 2026-11-20.
- Duplicate date keys: 0.
- OHLC/volume invariant failures under the basic numeric checks: 0.
- The file has 302 consecutive rows whose OHLCV values exactly repeat the immediately preceding row. Repeated values alone are not proof of duplication, because genuine consecutive sessions can trade at identical values.

## Calendar-rule check
Applied the project’s documented market-week regime:
- Before 2026-04-10: Sunday–Thursday trading; Friday and Saturday are non-session weekdays.
- From 2026-04-10 onward: Monday–Friday trading; Saturday and Sunday are non-session weekdays.
- Saturday remains closed in both regimes.

Result:
- **226 of 845 rows (26.75%) are dated on non-session weekdays under that regime.**
- By calendar year: 2024 = 80; 2025 = 98; 2026 = 48.
- There are no duplicate date keys, so these are distinct dated rows, not repeated keys.
- Many non-session rows exactly copy the immediately preceding row’s OHLCV values. Example pairs include 2024-03-08/09 and 2024-03-15/16. These patterns are consistent with date-forward filling or stale-value carry-forward, but the mechanism is not proven from the CSV alone.

## Interpretation and limitations
1. A date on a scheduled non-session weekday cannot be accepted as an executed NEPSE session without independent evidence that the exchange actually traded on that date.
2. The matching OHLCV values on adjacent rows are a strong quarantine trigger when one date is a non-session date, but are not sufficient to reconstruct the correct source date or delete/shift records automatically.
3. A zero basic OHLC invariant-failure count does not establish trustworthy session dates, authentic volume, complete history, or point-in-time provenance.
4. The alternate `binayabaral/nepal-market-data` UNL history was previously found to share exact values on all 545 overlapping dates with the project archive, suggesting shared upstream lineage; it is not independent confirmation for these rows.
5. ShareHub documents a price-history API with `ALL` coverage, but access requires a licensed Data API account, bearer authentication, server-IP allow-listing and the price-history service on the licence. No credentials or licensed endpoint response were available in this audit. Public documentation alone is not data evidence.
6. Recent third-party pages expose selected recent daily UNL history, but that does not independently resolve the archive’s full 2024–2026 calendar contamination.

## Disposition
- **UNL archive status: QUARANTINE / LOW CONFIDENCE for historical indicator, backtest, training and signal use.**
- Do not ingest the 226 flagged dates as sessions.
- Do not delete, shift, interpolate, or rewrite any raw OHLCV rows.
- Do not splice this history with any alternate archive.
- Preserve the raw file and its current checksum/commit provenance in the project’s immutable source layer when available.
- A corrected dataset requires row-level reconciliation to executed-trade/session evidence or a provider’s point-in-time daily history with documented source dates and independently checked calendar membership.

## Next actions
1. Run the same calendar-aware date audit across every equity OHLCV file, not only UNL.
2. Produce a row-level quarantine register containing symbol, date, weekday, regime, prior/next row values, exact-repeat flag and evidence status.
3. Request/obtain an authorized ShareHub API licence and server allow-listing only through the project owner’s normal procurement path; do not store credentials in Git.
4. Independently compare selected recent UNL dates against a second provider and, where available, executed floorsheet/session evidence.
5. Keep all affected history excluded from canonical/training promotion until resolved.
