# P4.43 — uncovered repeated-OHLCV symbol/date lineage gap

Date: 2026-11-27  
Pinned source commit: `56362fb4f65b91fdcca8f50b50e53ad80e703649`

## Result

This pass compares the global consecutive-identical-OHLCV finding set against the strict equity security/date source-lineage table by symbol.

| Measure | Count |
|---|---:|
| Symbols with consecutive repeated-tuple findings | 462 |
| Symbols represented in strict security/date lineage table | 253 |
| Symbols absent from that table | **209** |
| Consecutive repeated-tuple pair findings on covered symbols | 71,166 |
| Consecutive repeated-tuple pair findings on uncovered symbols | **23,377** |
| Total consecutive repeated-tuple pair findings | 94,543 |

The 209 uncovered symbols span 209 source OHLCV files and 23,377 unique symbol/date pair keys, from 2024-03-06 through 2026-11-20.

## Reconciliation note

The repeat-review table contains 456 of the 462 global repeat-finding symbols. Six symbols — `MMFDB`, `NFSPO`, `NIFRAP`, `NLBBL`, `NRICP`, and `SFCLP` — appear in the global consecutive-repeat findings but not in the repeat-review table. They account for part of the 23,377 uncovered pair findings and were explicitly retained in this coverage gap output rather than silently omitted.

## Row-level output

The detailed companion crosswalk contains all 23,377 pair findings with symbol/date, pinned source path/blob SHA/commit, row references, and explicit `HOLD_UNKNOWN_NO_INFERENCE` disposition. A 209-symbol summary CSV and the detailed pair crosswalk are preserved as companion outputs.

Machine summary: `P443_UNCOVERED_REPEAT_SYMBOL_LINEAGE_GAP_2026-11-27.json`.

Detailed crosswalk SHA-256: `02bfac1e92101d2615220492797abdbeabcc10834563900d5584a9b670940503`

## Current-equity manifest cross-check (prioritization only)

Compared the 209 symbols with the pinned 281-row third-party active-equity manifest from `nepse-elite-ai-scanner-pro` at commit `470dcf63c6f5b74e01a0aa5a238a485f594e3e95` (blob `56bdb41c7307870ad755ceb24fc32b5340fee137`). Three symbols — `NESDO`, `ULBSL`, and `YMHL` — appear in that current manifest. The other 206 do not appear in this current active-equity snapshot. This is not an official historical instrument master: non-matches do not prove that a symbol is non-equity, inactive, delisted, or an alias. No instrument-class or lifecycle disposition was assigned.

## Interpretation and limits

This is a **coverage-gap reconciliation**, not an independent date-shift adjudication. Absence from the strict equity security/date source-lineage table does not prove that no official or third-party evidence exists elsewhere. It also does not establish that any repeated OHLCV tuple is erroneous, that the dates were closed, or that a security traded.

No instrument class, historical security identity, open/closed session, execution, price, or date was inferred. Every row remains HOLD/UNKNOWN. No OHLCV value was changed, deleted, shifted, deduplicated, corrected, or promoted.

## Next evidence requirement

For these 209 symbols, the next valid step is an effective-dated security-ID/instrument-class mapping and source-backed per-security date evidence (official EOD history or complete date-matched floorsheets with verified symbol identity and coverage). Until that evidence is available, the 23,377 pair findings remain unresolved.
