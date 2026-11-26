# Five-symbol OHLCV archive reconciliation — 2026-11-26

## Finding: files are present

A direct path and content check confirms that all five symbols previously reported as missing from the current-company-list comparison have OHLCV files in `03_stock_charts_ohlcv/`:

| Symbol | Rows | First archive row | Last archive row | First positive-volume row | Adjacent identical rows | Rows on dates classified verified closed |
|---|---:|---|---|---|---:|---:|
| NESDO | 934 | 2024-03-04 | 2026-11-20 | 2024-03-04 | 320 | 81 |
| SYPNL | 290 | 2025-12-10 | 2026-11-20 | 2025-12-10 | 74 | 76 |
| ULBSL | 932 | 2024-03-04 | 2026-11-20 | 2024-03-04 | 318 | 81 |
| USLB | 935 | 2024-03-04 | 2026-11-20 | 2024-03-04 | 320 | 81 |
| YMHL | 97 | 2026-06-22 | 2026-11-20 | 2026-06-22 | 2 | 3 |

All five files parsed with the expected Date/Open/High/Low/Close/Volume columns. This targeted audit found zero duplicate dates and zero invalid OHLC bounds in these five files. Every row had positive volume. These checks do not prove that every row is an actual exchange execution.

## Why the earlier comparison said “missing”

The comparison artifact `nepse_ohlcv_current_company_list_comparison_2026-11-26.csv` is a comparison against a rendered current-company-list capture, not an OHLCV file inventory. It marked NESDO, ULBSL and YMHL as not matched to that particular capture; it marked SYPNL and USLB as multiple company-list rows. It did not establish that the OHLCV files were absent.

The current dated security-ID crosswalk in the scanner repository separately matches all 281 current equity candidates to the 2026-11-25 security-ID snapshot. Do not infer identity failure from the older rendered-list comparison. The multiple-row cases require identity cross-check, not arbitrary row selection.

## Calendar and repeated-row warning

The 2025–2026 calendar file classifies 81 rows for NESDO, 76 for SYPNL, 81 for ULBSL, 81 for USLB and 3 for YMHL on dates marked `verified_closed`. The same five files contain 320, 74, 318, 320 and 2 adjacent identical OHLCV rows respectively.

This is a material reconciliation warning. Identical adjacent rows may be carried-forward values, but this cannot be assumed without row provenance. Rows on verified-closed dates must be checked against raw exchange trading dates and floorsheets before they can be accepted as trades. The calendar is partial and includes only a bounded date range; rows classified `outside_calendar` are not thereby confirmed trading sessions.

## Source hashes

- NESDO: `819aa845808ac0858a12ea40ede468522d554487`
- SYPNL: `6dfe35738490e61584917bdea7f9279097a52ce9`
- ULBSL: `09477e42bf43823cc8f6a693b1fe3b2e4672ab4e`
- USLB: `3c4cf350bc93613be176ec94087cc5e0bcb10cb4`
- YMHL: `c0c07256039452e31486897d0084d22358df57c4`

## Disposition

- OHLCV file presence for these five: confirmed.
- Row integrity for these five: preliminary checks passed for schema, duplicate dates and OHLC bounds.
- Actual execution/trade validity: not established.
- Calendar coverage: insufficient for full-session completeness.
- Canonical promotion and model training: not allowed.
- Corrected conclusion: the earlier five-file “missing” claim is withdrawn; the outstanding problem is calendar, identity-source reconciliation and repeated-row/trade provenance.
