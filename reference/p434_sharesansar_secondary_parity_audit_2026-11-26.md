# P4.34 — secondary historical OHLCV parity audit

Date: 2026-11-26  
Status: 1,368 flagged rows compared to a pinned ShareSansar-derived archive; no row promoted or repaired.

## Source and provenance

Compared the flagged v3 history with per-symbol series in `srijankarki07/nepse-data`, pinned to commit `688d59c03915dcee73ecad4230d2083a41c61764`.

The archive's README states that its data is scraped from ShareSansar and that the data itself is not covered by the repository's MIT code licence. It also documents source-history limitations and refused ambiguous dates. The audit therefore fetched the series in memory, verified each Git blob SHA, emitted comparison metadata only, and did not store or redistribute the raw third-party series.

## Results

| Result | Rows |
|---|---:|
| Flagged rows checked | 1,368 |
| Exact secondary tuple matches to v3 | 1,283 |
| Secondary value differences | 0 |
| No secondary row | 85 |
| Matched secondary rows with valid OHLC | 0 |
| Matched secondary rows still invalid | 1,283 |
| Promoted/repaired | 0 |

All 1,283 matched records are exact on Open, High, Low, Close and Volume. All 1,283 still fail the corresponding OHLCV invariant. This is evidence of exact value parity and likely shared ShareSansar lineage, not independent corroboration that the values are correct.

The 85 absent rows remain UNKNOWN; archive absence is not a NO_TRADE determination.

## Per-symbol coverage

| Symbol | Flags | Exact matches | Missing from archive |
|---|---:|---:|---:|
| AHPC | 607 | 524 | 83 |
| SKBBL | 381 | 380 | 1 |
| API | 122 | 121 | 1 |
| MERO | 104 | 104 | 0 |
| SPDL | 72 | 72 | 0 |
| CHL | 48 | 48 | 0 |
| HIDCL | 32 | 32 | 0 |
| RADHI | 1 | 1 | 0 |
| UNHPL | 1 | 1 | 0 |
| **Total** | **1,368** | **1,283** | **85** |

## Pinned source file identities

The comparison matrix records the Git blob SHA for each source series. The nine blob IDs are also included in the summary JSON. No source OHLCV values are copied into this repository.

## Why this does not resolve the anomalies

1. The external archive explicitly identifies ShareSansar as its upstream source. Exact equality with v3 across all 1,283 matched flagged rows strongly suggests shared data lineage; it is not a second independent feed.
2. The matched rows remain invalid under OHLC rules, so source parity cannot justify a repair.
3. The 85 missing rows have no secondary value to compare.
4. The ShareHub historical price API is not an unauthenticated public endpoint: its documentation requires a licensed Data API account, Bearer token and allow-listed server IP. No credentials or licensed access were available, so it was not called.
5. Hamroshare documents its price history as NEPSE EOD data but notes that charts may show raw or adjusted history. That is a potential separate verification route, but the exact flagged rows and price basis have not yet been retrieved.

## Reproducibility and safety

- Tool: `tools/audit_p434_sharesansar_secondary_parity.py`
- Tests: `tools/tests/test_audit_p434_sharesansar_secondary_parity.py`
- Comparison output: `reference/p434_1368_sharesansar_secondary_parity_2026-11-26.csv`
- Summary: `reference/p434_sharesansar_secondary_parity_summary_2026-11-26.json`
- Successful CI run: [45872335751](https://github.com/jaljala044/nepse-smc-data/actions/runs/45872335751)
- Only source identity and comparison metadata are committed. Third-party source CSVs are not stored.

## Disposition and next priority — P4.35

Keep all 1,368 rows UNKNOWN. Next, attempt exact-date historical comparisons using a genuinely separate NEPSE-derived source such as Hamroshare's raw (not adjusted) history or NEPSE Analysis' settled bars, starting with AHPC and SKBBL. Require exact date, symbol/security identity and explicit price basis. Any source disagreement, corporate-action ambiguity or missing record remains UNKNOWN. Seek licensed ShareHub access only if an authorized account and IP allow-list are available.
