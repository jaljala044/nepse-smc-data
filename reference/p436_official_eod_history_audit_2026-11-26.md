# P4.36 — Official NEPSE historical EOD endpoint and OHLCV parity audit

**Audit date:** 2026-11-26  
**Evidence branch:** `p436-official-eod-history-crosscheck`  
**Successful CI run:** https://github.com/jaljala044/nepse-smc-data/actions/runs/45884435506  
**Capture timestamp:** 2026-11-26T19:32:53.676563Z

## Objective

Use the authenticated official NEPSE historical price-volume endpoint to:
1. Test whether historical EOD records exist for the NMLBBL and SMPDA candidate first-trade dates and prior sessions.
2. Validate the endpoint against a recent one-year control window.
3. Compare official HLCV records with the repository's canonical OHLCV files without silently changing canonical dates.

This endpoint is EOD data, not a floorsheet. It cannot identify individual contracts, buyers/sellers, or broker flow.

## Authentication and endpoint

The pinned frontend authentication flow was reproduced using the same pinned third-party WASM implementation as P4.35:
- Client repository: `basic-bgnr/NepseUnofficialApi`
- Commit: `180a550c60f1959983b854659e650a4c189a3c0f`
- WASM Git blob SHA: `06162abc9206c6a855648ed5c0abb2fd515aa555`
- Official endpoint: `GET /api/nots/market/history/security/{securityId}?size=500&startDate=...&endDate=...&page=0`

Observed:
- Token prove: HTTP 200.
- Official security master: HTTP 200.
- NMLBBL security ID 396; SMPDA security ID 2896, matching the P4.35 security master.
- Authentication secrets, salts and derived authorization values were held in memory only; no tokens were saved or logged.

## Historical candidate windows — no records returned

| Symbol | Requested window | Candidate date | Prior session | HTTP | totalElements | totalPages |
|---|---|---|---|---:|---:|---:|
| NMLBBL | 2024-05-01 to 2024-05-31 | 2024-05-19 | 2024-05-16 | 200 | 0 | 0 |
| SMPDA | 2024-08-01 to 2024-08-31 | 2024-08-18 | 2024-08-14 | 200 | 0 | 0 |

The raw JSON responses and SHA-256 hashes are preserved in `reference/p436_official_eod_history/`.

**Interpretation:** The endpoint returned a valid empty page for the full month windows. It does not provide a primary EOD cross-check for either 2024 candidate date. An empty EOD result is not proof of `NO_TRADE`, and does not establish the completeness of a prior-session floorsheet.

## Rolling one-year controls

Both securities were queried from 2025-11-26 through 2026-11-26.

| Symbol | Rows | totalElements | totalPages | Oldest returned date | Newest returned date | HLC present | Open present |
|---|---:|---:|---:|---|---|---:|---:|
| NMLBBL | 228 | 228 | 1 | 2025-11-26 | 2026-11-25 | 228 | 0 |
| SMPDA | 228 | 228 | 1 | 2025-11-26 | 2026-11-25 | 228 | 0 |

The observed response schema includes `businessDate`, `totalTrades`, `totalTradedQuantity`, `totalTradedValue`, `highPrice`, `lowPrice` and `closePrice`. The endpoint did not return an open price in the captured rows. The one-year query establishes that the authenticated route is functioning and returning paginated EOD history for these securities; the 2024 empty windows are consistent with a historical-retention boundary, but this audit does not assert an exact backend retention policy.

## Cross-check against canonical OHLCV

Comparison uses only the four fields present in both sources: High, Low, Close and Volume. Open is excluded because the observed official EOD response does not supply it.

| Metric | NMLBBL | SMPDA |
|---|---:|---:|
| Official one-year rows | 228 | 228 |
| Canonical rows in same date window | 304 | 304 |
| Exact-date overlaps | 223 | 223 |
| Exact-date HLCV mismatches | **0** | **0** |
| Official-only dates | 5 | 5 |
| Canonical-only dates | 81 | 81 |
| Canonical-only rows whose HLCV tuple exactly matches another official date | **81/81** | **81/81** |

### Official-only dates

For both symbols:
- 2026-11-23, 2026-11-24 and 2026-11-25 are official records later than the canonical file's current endpoint.
- Official 2026-03-01 exactly matches canonical 2026-03-02 on HLCV.
- Official 2026-07-24 exactly matches canonical 2026-07-25 on HLCV.

The last two are one-calendar-day date discrepancies, not price or volume discrepancies.

### Canonical-only dates

All 81 canonical-only date rows for each symbol have an exact High/Low/Close/Volume tuple match to a record on a different official date. The nearest matched official-date offsets are:

| Canonical date minus matched official date | Rows |
|---:|---:|
| +1 day | 37 |
| +2 days | 31 |
| +3 days | 9 |
| +4 days | 3 |
| +5 days | 1 |
| **Total** | **81** |

The identical 81-row date-offset pattern appears in both NMLBBL and SMPDA. This is a strong signal of shared date duplication/forward-shift contamination in the canonical OHLCV date series. It is an anomaly requiring source-provenance investigation, not permission to rewrite dates automatically. The official records also contain two exact HLCV matches on dates one day earlier than their canonical counterparts.

The canonical OHLCV files remain unchanged. No date was corrected or removed by this task.

## Lifecycle and scanner disposition

| Symbol | Candidate first-trade date | Prior-session date | P4.36 result | Lifecycle `valid_from` |
|---|---|---|---|---|
| NMLBBL | 2024-05-19 | 2024-05-16 | Official 2024 EOD window empty | **UNKNOWN** |
| SMPDA | 2024-08-18 | 2024-08-14 | Official 2024 EOD window empty | **UNKNOWN** |

- The P4.33 third-party archive evidence remains secondary only.
- The P4.35 official historical floorsheet route remains unusable for these dates: market-wide history ignored the date and per-company requests returned 403.
- P4.36 does not turn an empty EOD query into `NO_TRADE`.
- No canonical OHLCV, lifecycle `valid_from`, trading-calendar status, training label, backtest label, or scanner score changed.

## Reproducibility

- Capture: `tools/capture_p436_official_eod_history.py`
- Regression tests: `tools/tests/test_capture_p436_official_eod_history.py`
- CI workflow: `.github/workflows/p436-official-eod-history.yml`
- Immutable response pages and report: `reference/p436_official_eod_history/`
- CI run #45884435506 passed unit tests, official endpoint capture, HLCV comparison and artifact commit.

## Next priority — P4.37

Investigate the shared canonical date anomaly across the full equity universe:
1. Identify whether the 81 extra dates are generated by a date-expansion, weekend carry-forward, timezone conversion, or source merge defect.
2. Compare official one-year EOD windows against canonical rows for a stratified sample across sectors and instruments.
3. Trace the exact ingestion/source revision that introduced the duplicated date pattern.
4. Preserve the original rows and publish a quarantine/impact matrix before any canonical date corrections.
5. Keep UNKNOWN where no primary evidence is available; do not use inferred date shifts to create or delete trading sessions.
