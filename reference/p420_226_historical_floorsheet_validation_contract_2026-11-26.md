# P4.20 — 226 historical floorsheet validation

**Audit scope:** 226 daily CSV candidates listed in the pinned P4.19 manifest, across 281 current equity symbols.

## Six sequential checks

1. **Retrieval and pinning:** download each file from the exact source commit and path in the manifest; record retrieval time, URL, HTTP ETag/Last-Modified/content length, actual size, SHA-256 and Git blob SHA-1. Both expected file size and Git blob identity must match.
2. **Schema and row integrity:** require transaction, symbol, buyer, seller, quantity, rate, amount and date; detect missing/duplicate contract IDs, malformed rows, empty symbols, broker-ID issues, non-positive/non-integral quantities, non-positive rates/amounts and date mismatches.
3. **Contract amount identity:** check quantity × rate against amount using Decimal arithmetic. Accept exact decimal amounts within NPR 0.01; also accept whole-rupee amount values only when they exactly equal the mathematical floor of quantity × rate. Record which policy matched and every exception.
4. **Daily totals and independent completeness:** calculate contracts, shares, turnover and distinct symbols for every file. Exact Parquet/CSV contract-multiset parity is now recorded for 2026-11-19 (40,837 matched contracts), 2026-11-20 (39,966), and 2026-11-24 (52,387), with zero one-sided rows on each date. However, only 2026-11-20 currently has separately verified upstream `totalElements`, full pagination (80/80 pages), and independent daily totals (10,602,468 shares, NPR 3,887,563,470.82 turnover, 352 symbols). Therefore only 2026-11-20 can pass the full-session completeness gate; 2026-11-19 and 2026-11-24 remain `UNKNOWN` for completeness pending their upstream capture logs.
5. **281-equity OHLCV reconciliation:** compare per-symbol contract quantity against an available same-date OHLCV volume row. Emit MATCH, CONFLICT, OHLCV_ROW_ABSENT or NOT_COMPARABLE. This is an archive consistency check; it does not independently validate OHLCV provenance or price basis.
6. **Disposition and evidence log:** emit per-date summaries, per-equity/date TRADED/NO_TRADE/UNKNOWN dispositions and download-integrity metadata. TRADED requires positive valid contracts. NO_TRADE is allowed only for 2026-11-20 after independent totals pass and no contract plus absent/zero OHLCV volume. All other absence remains UNKNOWN.

## Output artifacts

- `download_integrity.csv`: one row per daily file with actual SHA-256, Git blob identity, size and retrieval metadata.
- `daily_validation_summary.csv`: schema/content quality, row-level errors, market totals and completeness status.
- `equity_date_dispositions.csv`: 226 × 281 symbol/date dispositions and OHLCV comparison.

## Limitations and safety

- The 226 dates are not a complete official NEPSE trading calendar. For 225 dates, the positive-open evidence is scoped to security ID 8108; it proves market activity, not every equity's eligibility.
- A valid CSV is not proof that all exchange contracts were captured. File integrity, row validity and full-session completeness are separate gates.
- 2026-11-20 is the only date with independently reconciled full-session totals and contract-level multiset parity in this audit. Raw bronze API pages were not retained by the independent capture.
- No broker accumulation/distribution inference, manipulation claim, canonical data promotion, training admission or scanner BUY authorization follows from this work.
- Download/hash failures and files with no usable valid contracts fail the CI job. A file with otherwise valid contracts but isolated malformed rows is marked `PARTIAL_FAIL`; valid positive contracts can still establish `TRADED` for unaffected symbols, but the date cannot pass the full-session completeness gate and no absent symbol is labelled `NO_TRADE`. The 2026-04-29 file contains one NIBLGF row with quantity 1,000 and zero rate/amount; it remains a recorded invalid row, not a fabricated trade.
