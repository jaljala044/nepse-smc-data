# P4.35 — Authenticated NEPSE API and historical floorsheet route verification

**Audit date:** 2026-11-26  
**Workflow:** https://github.com/jaljala044/nepse-smc-data/actions/runs/45877590883  
**Pinned client:** `basic-bgnr/NepseUnofficialApi` commit `180a550c60f1959983b854659e650a4c189a3c0f`  
**WASM Git blob:** `06162abc9206c6a855648ed5c0abb2fd515aa555`

## Objective

Reproduce the public NEPSE frontend token flow in a controlled CI job, retrieve the current security master, and test whether official floorsheet routes honor historical `businessDate` values.

## Authentication flow reproduced

The CI job:
1. Called `GET /api/authenticate/prove`.
2. Parsed the returned access/refresh tokens using the pinned upstream `css.wasm` module.
3. Derived the frontend-style `Salter` authorization header.
4. Used the authenticated header to retrieve market status and the security list.
5. Derived the floorsheet POST payload ID using the pinned dummy-data table and NEPSE server day.

Authentication succeeded:
- Market status: HTTP 200.
- Security list: HTTP 200.
- NMLBBL security ID: 396.
- SMPDA security ID: 2896.

The raw token-prove body, access token, refresh token, salts, and dynamic payload ID were never persisted or printed. The WASM binary is embedded as a base64 constant and verified against its pinned Git blob SHA before use.

## Official floorsheet route results

### Market-wide current-session endpoint

`POST /api/nots/nepse-data/floorsheet?&size=500&sort=contractId,desc`

<badge color="success">HTTP 200</badge>

- Page-zero content: 500 records.
- `totalElements`: 49,806.
- `totalPages`: 100.
- Returned rows have `businessDate = 2026-11-26`.
- The request used the derived payload day 27, matching NEPSE local day.

### Historical businessDate test

The same market-wide endpoint was queried with each historical date:
- 2024-05-19
- 2024-05-16
- 2024-08-18
- 2024-08-14

All four requests returned the same current-session page:
- HTTP 200.
- 500 rows.
- `totalElements = 49,806`.
- `totalPages = 100`.
- Every returned row had `businessDate = 2026-11-26`.

**Conclusion:** this endpoint ignores the supplied historical `businessDate` parameter and serves the current session only. It cannot be used to establish historical first-trade boundaries.

### Per-company floorsheet endpoint

The pinned public client documents:

`POST /api/nots/security/floorsheet/{securityId}?&businessDate={date}&size=500&sort=contractid,desc`

Tests were run for both securities on all four candidate/prior dates, plus current-session control requests for both securities. All per-company requests returned HTTP 403 with a 146-byte nginx HTML response. No `floorsheets` JSON or pagination metadata was returned.

The 403 is an observed endpoint response, not evidence that the securities had no trades. No retry/bypass of the access restriction was attempted.

## Validation

- 7 regression tests passed in CI.
- Tests cover pinned WASM Git blob identity, WASM token parsing, payload-ID derivation, token redaction, fail-closed pagination metadata, payload-day fallback, and current-session control probes.
- CI run: https://github.com/jaljala044/nepse-smc-data/actions/runs/45877590883
- Capture report and public market/security responses are committed under `reference/p435_official_historical_floorsheets/`.

## Evidence classification and disposition

- Token flow: reproduced from a pinned third-party public client implementation.
- Market status and security master: observed HTTP 200 responses from the official NEPSE domain.
- Market-wide current floorsheet page 0: observed official API response with pagination totals.
- Historical market-wide query: **not honored**; returned current date on every test.
- Per-company floorsheet: **403 Forbidden** for all candidate/prior and current-session probes.
- Historical floor contract rows: none retrieved from NEPSE.
- NMLBBL and SMPDA lifecycle first-trade boundaries: **UNKNOWN**.
- No canonical OHLCV, lifecycle dates, trading-calendar status, training labels, or scanner scores changed.

## Next priority — P4.36

Use the now-working authenticated token flow to test NEPSE's official per-security historical price-volume endpoint:

`GET /api/nots/market/history/security/{securityId}?&size=500&startDate={startDate}&endDate={endDate}`

Query the four exact date windows for NMLBBL and SMPDA. Preserve raw JSON and response hashes, validate returned dates and OHLCV fields, and compare candidate-day volume against the existing dataset. This is an official EOD cross-check only; it must not be presented as floorsheet or unique-contract evidence. Keep lifecycle `valid_from` UNKNOWN unless a complete prior-session record or primary floorsheet evidence is obtained.
