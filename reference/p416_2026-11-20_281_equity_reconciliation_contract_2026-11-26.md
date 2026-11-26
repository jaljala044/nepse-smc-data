# P4.16 — 2026-11-20 full-session reconciliation against the 281-equity matrix

## Universe input correction

The first CI attempt correctly rejected the older `nepse_target_universe_candidates_2026-11-26.csv` input: it contains 278 rows classified as Equity. The Stage 1 P4.10 coverage matrix contains 281 unique equity symbols, including NESDO, ULBSL and YMHL. The reconciliation job now uses `reference/p410_stage1_coverage_matrix_2026-11-26.csv` as its explicit equity universe and asserts 281 unique symbols.

This preserves the 281-equity target and prevents the three additional securities from silently disappearing from the session audit.

## Pinned 2026-11-20 session evidence

The run uses the SocrateAI daily floorsheet CSV pinned to SHA-256 `abafc3b8eaa8d2b9b884e9f2df974deb267485d4476f2a4e953d6324787fc43d`. The independent published pipeline capture record reports:
- upstream `totalElements=39966`;
- 80 pages read of 80 total pages;
- zero rejected rows and zero empty pages;
- exact normalized trade-multiset equality between the pipeline Parquet partition and the SocrateAI CSV;
- 39,966 contracts, 10,602,468 shares, NPR 3,887,563,470.82 turnover and 352 symbols.

The pipeline's raw bronze payload archive was not available in the evidence record. Therefore the session is marked as observed-open for this date based on independent full-session capture parity, but the source remains a third-party capture and is not promoted to raw official-source status.

## Reconciliation semantics

For each of the 281 equities, the job produces one row:
- `TRADED`: valid symbol contracts in the pinned session file;
- `NO_TRADE`: no contracts, with the complete hash-matched session file, all market totals reconciled, verified-open date, and no positive OHLCV volume for that symbol;
- `UNKNOWN`: all other cases, including positive OHLCV volume without a matching contract.

The older 500-row local floorsheet extract is not used as the session source. Prior parity testing showed it is not a full-session file.

## Limitations

This is one-date, 281-equity reconciliation only. It does not construct historical per-security open-session calendars, prove listing/first-trade dates, or establish no-trade days for other dates. It does not authorize scanner BUYs, broker-footprint scoring, training, or canonical-data promotion.
