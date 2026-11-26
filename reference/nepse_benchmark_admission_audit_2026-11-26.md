# NEPSE Benchmark Admission Audit — 2026-11-26

## Decision

**Status: NOT ADMITTED — relative-strength benchmark remains insufficient evidence.**

The existing index archives are useful research candidates, but they do not currently satisfy the scanner's P4.8 benchmark admission contract. Do not promote these rows into canonical benchmark history, training data, backtests, or live scanner signals. Keep the RS component null until a date-complete, source-verified, point-in-time NEPSE index series is captured and reconciled.

## Files examined on data-repository main

| File | NEPSE records | Date range | Disposition |
|---|---:|---|---|
| `scanner_inputs/benchmark_daily.csv` | 138 | 2026-01-06 to 2026-11-20 | Mixed source labels; not row-level provenance verified |
| `scanner_inputs/index_history/closes_only.csv` | 56 | 2026-01-01 to 2026-04-30 | Closing values only; validation label is a third-party source string |
| `scanner_inputs/index_history/ohlc.csv` | 0 | — | No NEPSE rows; file contains other index series |

### Benchmark daily source-label breakdown

| Label in file | Rows | First date | Last date |
|---|---:|---|---|
| YONEPSE archived index | 105 | 2026-05-04 | 2026-10-06 |
| Nepse Decode closing index | 23 | 2026-10-07 | 2026-11-20 |
| YONEPSE + SocrateAI | 10 | 2026-01-06 | 2026-04-24 |
| **Total** | **138** | 2026-01-06 | 2026-11-20 |

All 138 dates in `benchmark_daily.csv` are unique. The 56 NEPSE close-only rows are also unique. The close-only dates and the 10 sparse Jan–Apr OHLC rows do not form one validated daily series. The 10 sparse OHLC rows report zero volume and blank turnover, so they do not independently establish executed-market activity or complete index-session coverage.

## Admission blockers

1. **Source lineage:** the CSV files contain descriptive source labels, not per-row immutable source identifiers and captured-payload SHA-256 provenance.
2. **Finality and point-in-time availability:** the rows do not carry a verified final/provisional status plus timezone-aware `available_at` timestamps suitable for as-of filtering.
3. **Completeness:** the Jan–Apr OHLC sample has only 10 dates; the 56 close-only observations do not provide OHLC; no approved complete official NEPSE benchmark-session series has been demonstrated.
4. **Independent reconciliation:** the 2026-11-25 market audit records a NEPSE Index Open conflict between ShareSansar (2644.68) and ShareHub (2643.79). This is unresolved evidence, not permission to choose one provider.
5. **Corporate-action/price basis:** stock-side histories also need verified price-basis and corporate-action statuses before a cross-sectional RS score can be calculated.

## Scanner interface contract

The scanner must admit only rows meeting all of the following:

- `record_type=index_ohlcv`, `index_code=NEPSE`
- Valid ISO `session_date`, finite positive close
- `source_validation_status=verified`, `finality_status=final`
- Nonblank `source_id`, valid 64-character `source_payload_sha256`
- Timezone-aware `available_at` no later than the decision timestamp

For each stock, the P4.8 engine additionally requires verified source provenance, an approved price basis, a cleared/verified corporate-action status, the latest exact benchmark session, and every exact benchmark date in the 5/21/63/126-session windows. At least two securities and 80% coverage of the expected equity universe are required before any percentile score is emitted. No forward-fill, interpolation, stale endpoint, shortened horizon, or inferred neutral score is allowed.

## Evidence references

- `scanner_inputs/benchmark_daily.csv` (main blob at audit time: `fe7ca038cc409c43059c5c1d7fa8afbfdc5a7676`)
- `scanner_inputs/index_history/closes_only.csv` (main blob at audit time: `3bf38519818e27be3f48339b70921e040906c2c4`)
- `scanner_inputs/index_history/ohlc.csv` (main blob at audit time: `638dc9cf63cca35f8070f06a2e57fd10a46d2116`)
- `01_market_indices/audit_2026-11-25.json`: records the ShareSansar/ShareHub NEPSE Index Open conflict and source-payload hashes for that day's captured pages.
- `scanner_inputs/audit/source_coverage.json`: documents the source-coverage inventory; it does not certify the index archive as canonical.

## Next evidence task

Capture the official NEPSE index-history endpoint with raw response bytes, request URL/parameters, retrieval timestamp, response headers, source revision and SHA-256. Reconcile each session against an independent dated source, resolve all conflicts explicitly, establish finality and session coverage, then emit a versioned row-level manifest. Until this is complete, the correct scanner result is **RS = UNKNOWN / insufficient evidence**, not a market-leader ranking.
