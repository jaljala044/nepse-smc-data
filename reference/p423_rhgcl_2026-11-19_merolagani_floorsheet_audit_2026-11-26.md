# P4.23 — RHGCL 2026-11-19 Merolagani floorsheet cross-check

**Audit date:** 2026-11-26  
**Disposition:** `CONFLICT_UNRESOLVED` / `UNKNOWN` for canonical promotion  
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
| Open (highest sequence number; inferred earliest print) | 252.10 |
| High | 259.50 |
| Low | 252.10 |
| Close (lowest sequence number; inferred latest print) | 258.00 |



### Sequence-order interpretation

The file preserves the Merolagani floorsheet display sequence, where smaller `sn` values appear first. For the daily OHLC reconstruction, that display order is reverse chronological: the highest `sn` is treated as the earliest print (open), and the lowest `sn` as the latest print (close). This direction is consistent with the independently displayed daily close of NPR 258.00 and the full 47-print price range. The CSV has no per-trade timestamps, so sequence direction remains an inferred ordering convention corroborated by the daily close, not a primary timestamp proof.

The reconstructed RHGCL OHLCV matches the alternative record: 252.10 / 259.50 / 252.10 / 258.00 / 9,054. It corroborates the 258.00 close and 9,054 volume reported by other secondary records. The local 500-row sample contains two RHGCL contracts (480 shares) matching the same two early contract quantities and prices; this is corroboration, not a complete session capture.

## Canonical conflict remains unresolved

- SMC canonical: 252.10 / 259.50 / 252.10 / 256.00 / 4,216.
- Alternative record: 252.10 / 259.50 / 252.10 / 258.00 / 9,054.
- The 47-row Merolagani-derived reconstruction supports the alternative tuple but inherits the source's pagination/completeness limitations.
- No direct NEPSE official EOD record or complete independently verified primary floorsheet has been preserved in this audit.

**Decision:** retain both source tuples unchanged; keep RHGCL `UNKNOWN` / `CONFLICT_UNRESOLVED`. Do not promote 258.00 or alter production OHLCV on this evidence alone.

## Artifact

- Extracted 47 RHGCL contract rows: `reference/p423_rhgcl_2026-11-19_merolagani_floorsheet_rows_2026-11-26.csv`
