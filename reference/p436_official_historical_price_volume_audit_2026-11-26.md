# P4.36 — Official NEPSE historical price-volume cross-check

**Audit date:** 2026-11-26  
**CI run:** https://github.com/jaljala044/nepse-smc-data/actions/runs/45878416995  
**Source files:** `reference/p436_official_price_volume/`

## Objective

Use the authenticated official NEPSE per-security historical price-volume endpoint to cross-check the candidate first-trade dates and the immediately preceding sessions. This is daily EOD evidence only, not floorsheet or contract-level evidence.

## Authentication and endpoint

The P4.35 pinned Salter flow was reused. Authentication and security-list retrieval succeeded:
- Token prove: HTTP 200; raw token response not saved.
- Security list: HTTP 200.
- NMLBBL security ID: 396.
- SMPDA security ID: 2896.

Endpoint:
`GET /api/nots/market/history/security/{securityId}?&size=500&startDate={startDate}&endDate={endDate}`

The raw response bodies are preserved with SHA-256 in the capture report. Access/refresh tokens and salts are held in memory only.

## Exact historical windows

| Symbol | Requested window | HTTP | Rows | totalElements | totalPages | Candidate date rows | Prior date rows |
|---|---|---:|---:|---:|---:|---:|---:|
| NMLBBL | 2024-05-16 to 2024-05-19 | 200 | 0 | 0 | 0 | 0 | 0 |
| SMPDA | 2024-08-14 to 2024-08-18 | 200 | 0 | 0 | 0 | 0 | 0 |

Both historical windows returned an empty Spring-style page object with `content=[]`, `totalElements=0`, and `totalPages=0`. This is not evidence that the securities did not trade; the endpoint is not returning the 2024 history.

## Recent-window controls

To verify the endpoint and query parameters were functioning, the same API was queried for 2026-10-27 to 2026-11-26:

| Symbol | HTTP | Rows | totalElements | totalPages | Returned date range |
|---|---:|---:|---:|---:|---|
| NMLBBL | 200 | 18 | 18 | 1 | 2026-10-27 to 2026-11-26 |
| SMPDA | 200 | 18 | 18 | 1 | 2026-10-27 to 2026-11-26 |

The recent responses prove the authenticated endpoint returns daily history for a recent period and that the date filters are active. The 2024 empty windows therefore indicate the endpoint does not provide the requested older records at this time; the exact retention policy is not documented by this probe.

The recent response schema contains `businessDate`, `totalTrades`, `totalTradedQuantity`, `totalTradedValue`, `highPrice`, `lowPrice`, and `closePrice`. It did not include `openPrice` in the captured records. Therefore this endpoint is not a complete OHLC source in the observed schema.

## Reconciliation outcome

- No official EOD row was returned for either 2024 candidate date.
- No official EOD row was returned for either preceding date.
- Candidate volume/OHLCV matching could not be performed from this endpoint.
- Existing P4.33 third-party candidate-day quantities (NMLBBL 864 and SMPDA 5,314) remain secondary-source evidence only.
- The recent controls demonstrate the API is live and returns current/recent daily history, but they do not establish a 2024 archive.

## Validation

- 5 regression tests passed.
- Tests cover candidate EOD field normalization, expected OHLCV comparisons, token redaction, out-of-window date rejection, HTTP-error fail-closed behavior, and recent-window endpoint controls.
- CI run #45878416995 passed and committed the raw official responses plus capture report.
- Historical empty responses are preserved exactly; no zero-trade assertion was generated.

## Disposition

- Official historical EOD cross-check for 2024: **unavailable from this endpoint response**.
- Recent official EOD endpoint: **reachable and returning 18 daily rows per security**.
- First-trade boundaries for NMLBBL and SMPDA: **UNKNOWN**.
- No canonical OHLCV, lifecycle `valid_from`, calendar status, training labels, or scanner scores changed.

## Next priority — P4.37

Investigate NEPSE's other official historical data sources and retention boundaries:
1. Test the official `today-price`/EOD history endpoint with explicit `businessDate` for 2024 dates.
2. Inspect official security/company history endpoints for alternate date-range paths and archive limits.
3. Determine whether the official API provides a 365-day rolling history, a different archive path, or no older data.
4. Do not reinterpret empty historical API responses as `NO_TRADE`; keep UNKNOWN unless a documented complete-date response or floorsheet exists.
