# Equity OHLCV Repository Parity and Quality Audit — 2026-11-26

## Scope

Task 5 of the five-task common-equity validation queue. Compared the 281 provisional equity OHLCV paths between:

- `jaljala044/nepse-smc-data`
- `jaljala044/nepse-history-starter`

Git tree blob SHA comparison establishes exact byte-level parity without downloading all files. For the 23 divergent pairs, both files were fetched and row-level checks were run. The earlier 10-symbol pilot audit remains the only separate row-quality pilot outside these 23 divergent pairs.

## Repository parity

| Metric | Result |
|---|---:|
| Provisional equity symbols | 281 |
| Files present in `nepse-smc-data` | 281 |
| Files present in `nepse-history-starter` | 281 |
| Exact matching blob SHA pairs | 258 |
| Divergent blob SHA pairs | 23 |
| Missing files in either repository | 0 |

The 23 divergent symbols are listed in the CSV deliverable. Exact matching blob SHA means the corresponding files are byte-identical across repositories; it does not by itself certify their data quality.

## Row-level checks on the 23 divergent pairs

| Check | `nepse-smc-data` | `nepse-history-starter` |
|---|---:|---:|
| Total rows across 23 files | 33,439 | 20,767 |
| Duplicate dates | 0 | 0 |
| Zero-volume rows | 0 | 0 |
| Invalid OHLC rows | 1,329 | 0 |
| Adjacent repeated OHLCV rows | 5 | 7,067 |

OHLC validity was checked using the rule: `High >= max(Open, Close, Low)` and `Low <= min(Open, Close, High)`.

### Key findings

1. The starter files in the 23 divergent pairs have no invalid OHLC rows, duplicate dates, or zero-volume rows under the tested rules. They contain 7,067 adjacent repeated OHLCV rows, consistent with extensive forward-filling. These repeated rows must not be interpreted as executed trades without separate evidence.
2. The SMC files contain 1,329 invalid OHLC rows across the 23 divergent symbols. The affected symbols include AHPC (588), SKBBL (379), API (122), MERO (102), SPDL (53), CHL (45), HIDCL (30), and smaller counts in several others. Preserve the source rows and investigate them individually; do not auto-correct.
3. The 23 divergent files have extensive date-set and OHLCV value disagreement. In every inspected pair, all common-date rows differed in OHLCV values; the CSV records counts of dates unique to each archive and common dates with differing values.
4. The SMC files generally contain more historical rows and earlier start dates. The starter files generally begin on 2024-03-04 (with symbol-specific exceptions) and have a daily-looking series with repeated values. These are different archive constructions, not interchangeable snapshots.
5. No raw data was overwritten, merged, or silently selected as canonical.

## Divergent pairs

See `reference/equity_repository_divergence_audit_2026-11-26.csv` for per-symbol blob hashes, row counts, quality counts, date-set differences, and common-date value differences.

## Important limitation

This is **not yet a complete row-level quality audit of all 281 files**. Exact parity identifies 258 byte-identical pairs, and the 23 divergent pairs were audited individually. The 258 identical pairs have not all been re-fetched and run through the OHLC/duplicate/zero-volume/carry-forward checks in this task. The prior 10-symbol pilot covered a small sample only.

## Task 5 outcome

**Partially completed — repository parity is complete for all 281 symbols; row-level quality is complete for the 23 divergent pairs plus the earlier 10-symbol pilot, but not yet for all 281 files.**

Recommended continuation:
- Resolve the 23 divergent symbols with accepted provider evidence (ShareHub, Chukul, ShareSansar, NepseAlpha), preserving both source versions and recording the selected derived values with provenance.
- Extend row-level quality checks to the 258 byte-identical pairs in batches.
- Do not treat carry-forward rows as trading volume/turnover evidence.
- Do not overwrite raw archive files.

## Related reports

- [Per-symbol observed-date coverage](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/equity_observed_date_coverage_2026-11-26.csv)
- [10-symbol pilot quality audit](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/equity_ohlcv_coverage_audit_pilot_2026-11-26.md)
- [Canonical session calendar](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_canonical_session_calendar_2025-2026.csv)
