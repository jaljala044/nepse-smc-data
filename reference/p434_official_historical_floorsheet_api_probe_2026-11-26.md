# P4.34 — Official NEPSE historical floorsheet API authentication probe

**Audit date:** 2026-11-26  
**Workflow:** https://github.com/jaljala044/nepse-smc-data/actions/runs/45876581906  
**Source capture:** `reference/p434_official_api_probe/probe_report.json`

## Objective

Establish whether the official NEPSE per-company floorsheet endpoint can be queried for historical `businessDate` values and whether the response exposes pagination totals needed for complete-session validation.

## Controlled probe results

All requests were sent to the official NEPSE domain `https://www.nepalstock.com` using ordinary HTTP requests. No token challenge was solved and no access-control bypass was attempted.

| Endpoint | Method | Result | Response |
|---|---|---:|---|
| `/api/nots/nepse-data/market-open` | GET | 401 | 87-byte HTML response |
| `/api/nots/security?nonDelisted=true` | GET | 401 | 87-byte HTML response |
| `/api/authenticate/prove` | GET | 200 | JSON, 723 bytes |

The token-prove response contained the fields `accessToken`, `refreshToken`, `salt1`–`salt5`, `serverTime`, and token metadata. The raw response body was **not saved**; token and salt values were never persisted. Only response length, SHA-256, field names, and field-presence booleans were recorded.

Because the security-list request returned 401, no current security IDs were obtained and all four company-specific historical requests were skipped. No floorsheet page was requested.

## Route and authentication implementation lead

The public `basic-bgnr/NepseUnofficialApi` client documents the following implementation pattern:
- Official base URL: `https://www.nepalstock.com`.
- Company/security lookup: `GET /api/nots/security?nonDelisted=true`.
- Per-security floorsheet route: `/api/nots/security/floorsheet/{securityId}?businessDate={date}&size={pageSize}&sort=contractid,desc`.
- POST body contains a dynamic `id` value; authorization header uses the `Salter` token scheme.
- The client obtains a token from `/api/authenticate/prove` and derives the authorization value from the returned salts using a bundled WebAssembly module.
- The client reads `floorsheets.totalPages` and iterates through pages.

References:
- https://github.com/basic-bgnr/NepseUnofficialApi/blob/master/nepse/NepseLib.py
- https://github.com/basic-bgnr/NepseUnofficialApi/blob/master/nepse/TokenUtils.py
- https://github.com/basic-bgnr/NepseUnofficialApi/blob/master/nepse/DummyIDUtils.py
- https://github.com/basic-bgnr/NepseUnofficialApi/blob/master/nepse/data/API_ENDPOINTS.json

These are third-party client implementation details, not official NEPSE API documentation. They provide a reproducible lead, not proof that the route still works or honors historical dates.

## Interpretation

The probe confirms:
1. The official token-prove endpoint is publicly reachable and returns the expected token/salt field structure.
2. The market-status and security-list endpoints reject unauthenticated requests with HTTP 401.
3. The official per-company floorsheet route has not yet been tested because the security IDs and valid authorization header were unavailable.
4. Historical `businessDate` behavior, `totalElements`, `totalPages`, and complete pagination remain unverified.

The token-prove response was deliberately redacted. Do not persist live access tokens, refresh tokens, or salts in repository artifacts or logs.

## Disposition

- Official API authentication: **partially understood; not yet reproduced**.
- Historical floorsheet API: **not yet queried**.
- Candidate/prior session evidence: unchanged from P4.33.
- NMLBBL and SMPDA lifecycle first-trade boundaries: **UNKNOWN**.
- No canonical OHLCV, lifecycle dates, calendar statuses, training labels, or scanner scores changed.

## Next priority — P4.35

In a controlled CI-only probe, reproduce the public frontend token flow using the pinned open-source client implementation and its pinned WASM asset. Keep token values in memory only; redact all request/response logs. Then:
1. Obtain market status and security-list responses with authorization.
2. Resolve the current security IDs for NMLBBL and SMPDA.
3. Query one historical candidate date per symbol using the documented per-company route.
4. Record the exact HTTP status, request date, response schema, `totalElements`, `totalPages`, and page-zero count.
5. Only if the route honors the requested date, fetch every page for all four dates and preserve raw page bodies plus checksums.
6. Fail closed on token expiry, empty/missing pages, inconsistent totals, or unexpected dates. Do not promote `NO_TRADE` from incomplete responses.
