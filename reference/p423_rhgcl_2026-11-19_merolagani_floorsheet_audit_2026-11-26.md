# P4.23 — RHGCL 2026-11-19 Merolagani floorsheet cross-check

**Audit date:** 2026-11-26  
**Disposition:** Secondary floorsheet incomplete; canonical OHLCV conflict resolved by official NEPSE EOD capture on 2026-11-26  
**Evidence tier:** Secondary floorsheet archive; useful corroboration, not primary NEPSE evidence

## Source and provenance

- Repository: https://github.com/SamirWagle/Nepse-All-Scraper
- Exact file: `data/floorsheet/floorsheet_2026-11-19.csv`
- File blob SHA: `43263388769de5b8e8e1801533dc3b41c100de99`
- File size: 2,752,514 bytes
- File commit: `c085881d0ee7698989c3f44463750e3f236d88d3` (2026-11-19T21:39:23Z)
- Scraper implementation: `scraper/core/floorsheet.py`, blob `0b2d47bbdd3f2846cae56bc65742096f4cb80c81`
- README identifies the floorsheet source as Merolagani, not NEPSE Official.
- The scraper navigates Merolagani's ASP.NET pagination and extracts rows. It stamps `date=today()` rather than reading the source row's date, and does not persist raw page captures, total-page metadata, or an independently verified expected record count. This limits completeness and provenance confidence.

## Reproducible extraction result

The archived CSV was parsed with quoted-field-aware CSV handling.

| Check | Result |
|---|---:|
| Parsed contract rows | 40,818 |
| Distinct symbols | 346 |
| Unique contract IDs | 40818 |
| Unique sequence numbers | 40818 |
| Sequence maximum | 40836 |
| Missing sequence numbers | 18 |
| Invalid quantity × rate vs amount rows | 0 |
| Total shares in archive | 9,435,392 |
| Total turnover in archive | NPR 3877623296.62 |

Missing sequence numbers: `33000, 34500, 34998, 34999, 35000, 36497, 36498, 36499, 36500, 37499, 37500, 37999, 38000, 39000, 39500, 40000, 40499, 40500`.

The repository's own cross-source parity manifest for the same date reports 40,837 rows, 347 symbols, 9,437,842 shares and NPR 3,877,645,728.62 turnover. This archive has 40,818 rows, 346 symbols, 9,435,392 shares and NPR 3,877,623,296.62 turnover: 19 fewer rows, 2,450 fewer shares and NPR 22,432.00 less turnover. Therefore the archive is not complete enough to settle the full-session total.

## RHGCL reconstruction

| Measure | Result |
|---|---:|
| RHGCL contracts | 47 |
| Shares | 9,054 |
| Turnover | NPR 2332952.50 |
| Open (lowest sequence number) | 258.00 |
| High | 259.50 |
| Low | 252.10 |
| Close (highest sequence number) | 252.10 |

The reconstructed RHGCL OHLCV matches the alternative record: 252.10 / 259.50 / 252.10 / 258.00 / 9,054. It corroborates the 258.00 close and 9,054 volume reported by other secondary records. The local 500-row sample contains two RHGCL contracts (480 shares) matching the same two early contract quantities and prices; this is corroboration, not a complete session capture.

## Canonical conflict — resolved by official NEPSE EOD

- SMC canonical: 252.10 / 259.50 / 252.10 / 256.00 / 4,216.
- Alternative record: 252.10 / 259.50 / 252.10 / 258.00 / 9,054.
- The 47-row Merolagani-derived reconstruction supports the alternative tuple but inherits the source's pagination/completeness limitations.
- No direct NEPSE official EOD record or complete independently verified primary floorsheet has been preserved in this audit.

The Merolagani-derived floorsheet remains an incomplete secondary archive and cannot independently prove full-session completeness. However, the conflict is now resolved by the direct official NEPSE EOD capture for the exact business date.

Official NEPSE row: Open 252.10 / High 259.50 / Low 252.10 / Close 258.00 / Volume 9,054; 47 trades; turnover NPR 2,332,952.50. The capture passed the official evidence validator with zero quality flags. See [official EOD evidence record](official_eod_captures/RHGCL_2026-11-19_nepse_eod.json) and [immutable capture artifact](https://github.com/jaljala044/nepse-smc-data/actions/runs/45862108316/artifacts/15137973461).

**Decision:** promote Close 258.00 and Volume 9,054 in the versioned derived OHLCV only. Preserve the SMC raw tuple unchanged. The floorsheet completeness warning remains attached to this secondary audit; it does not override the authoritative official EOD board.

## Artifact

- Extracted 47 RHGCL contract rows: `reference/p423_rhgcl_2026-11-19_merolagani_floorsheet_rows_2026-11-26.csv`
