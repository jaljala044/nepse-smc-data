# Adjacent-Repeated OHLCV Quality Flags — Pilot

**Coverage:** 14 of 281 provisional common-equity symbols (first 14 symbols in alphabetical order). This is a pilot overlay, not a complete 281-symbol audit.

Each record represents a row whose OHLCV values are numerically identical to the immediately preceding row in that symbol's raw series. The raw and derived OHLCV files are not modified by this overlay.

## Classification

- `adjacent_repeat_on_weekly_closed_day_candidate`: repeated row falls on Friday/Saturday under the pre-2026-04-06 Sunday–Thursday trading-week regime, or Saturday/Sunday under the post-2026-04-06 Monday–Friday regime. This is a candidate forward-fill flag, not proof.
- `adjacent_repeat_on_weekly_open_weekday`: repeated row falls on a weekday in the respective weekly trading regime. It remains suspicious but is not labelled a closure carry-forward.
- `adjacent_identical_ohlcv_unverified`: row is outside the currently supported calendar-regime evidence window (2025-11-25 through 2026-11-20).

## Pilot totals

| Measure | Rows |
|---|---:|
| Adjacent identical OHLCV rows | 3,288 |
| Weekly-closed-day candidates | 688 |
| Weekly-open-weekday repeats | 187 |
| Outside evidence-window / unverified | 2,413 |

The weekly-closed-day classification is based on weekday only and does not yet exclude special holiday closures, exceptional market closures, listing/suspension events, or symbol-specific non-trading days. Therefore no row is removed from the derived dataset.

## Partitions

- `part_01.csv`: first 7 symbols alphabetically
- `part_02.csv`: next 7 symbols alphabetically

## Next work

Extend the exact same row-level classification to the remaining 267 symbols, reconcile each candidate against explicit session closure evidence, and only then consider creating a separately named non-forward-filled dataset. Keep all raw and v1 derived rows intact.
