# P4.37 — Official NEPSE today-price historical-date probe

**Audit date:** 2026-11-26 (NEPSE market date)  
**CI run:** https://github.com/jaljala044/nepse-smc-data/actions/runs/45879163502  
**Timezone:** `Asia/Kathmandu`  
**Pinned client:** `basic-bgnr/NepseUnofficialApi` commit `180a550c60f1959983b854659e650a4c189a3c0f`

## Objective

Test the official NEPSE `/api/nots/nepse-data/today-price` endpoint with explicit historical `businessDate` values for the four NMLBBL/SMPDA candidate and prior dates. Capture all pages, raw response bytes, SHA-256, returned business dates, and target-row uniqueness.

## Historical-date results

All four historical requests were rejected by the official endpoint with HTTP 500 and the JSON body:

`Searched Date is not valid.`

| Symbol | Requested date | HTTP | Body bytes | SHA-256 | Disposition |
|---|---|---:|---:|---|---|
| NMLBBL | 2024-05-19 | 500 | 27 | `cca881461d563205a8c609c97ca56ed629037478322de2eefdd297a31825710e` | `CAPTURE_ERROR` |
| NMLBBL | 2024-05-16 | 500 | 27 | same | `CAPTURE_ERROR` |
| SMPDA | 2024-08-18 | 500 | 27 | same | `CAPTURE_ERROR` |
| SMPDA | 2024-08-14 | 500 | 27 | same | `CAPTURE_ERROR` |

The exact 27-byte response bodies and structured error manifests are preserved under `reference/p437_official_today_price/{SYMBOL}_{DATE}/`.

## Current-session control

A control request for NMLBBL on 2026-11-26 succeeded:

<badge color="success">HTTP 200 — exact target row found</badge>

- `totalElements = 355`
- `totalPages = 1`
- 355 rows captured; pagination row count reconciles.
- Returned `businessDate`: 2026-11-26.
- Exactly one NMLBBL row found.

<text color="secondary" size="sm">Official current-session NMLBBL row</text>

| Field | Value |
|---|---:|
| Open | 457.00 |
| High | 468.00 |
| Low | 457.00 |
| Close | 467.90 |
| Volume | 3,596 |
| Turnover (NPR) | 1,667,704.20 |
| Trades | 42 |
| Security ID | 396 |

This matches the P4.36 recent official price-volume record for NMLBBL on the same date, confirming that the pinned client, timezone, authorization and current-session EOD capture are functioning.

## Interpretation

The endpoint successfully serves the current market date and returns a complete one-page board. It rejects all four requested 2024 dates with `Searched Date is not valid.`

This establishes that the official `today-price` endpoint did not provide those historical dates during this probe. It does **not** establish that the securities did not trade. The API error is an archive/endpoint limitation, not a zero-trade record.

Together with P4.35 and P4.36:
- Market-wide floorsheet route returns the current session and ignores historical `businessDate`.
- Per-company floorsheet route returns HTTP 403.
- Per-security historical price-volume route returns recent rows but empty 2024 windows.
- `today-price` accepts the current market date but rejects all four 2024 dates.

## Validation

- 7 regression tests passed.
- Tests cover target-row uniqueness, missing-row classification, returned-date mismatch, pagination row totals, and batch capture error handling.
- CI run #45879163502 passed.
- The current-session response and all four historical error bodies are preserved.
- Token values are not persisted.
- No canonical OHLCV, lifecycle `valid_from`, calendar status, training label, or scanner score changed.

## Lifecycle disposition

| Symbol | Candidate date | Prior date | Official historical result | `valid_from` |
|---|---|---|---|---|
| NMLBBL | 2024-05-19 | 2024-05-16 | Both dates rejected as invalid search dates | **UNKNOWN** |
| SMPDA | 2024-08-18 | 2024-08-14 | Both dates rejected as invalid search dates | **UNKNOWN** |

Do not convert HTTP 500 or missing historical data into `NO_TRADE`.

## Next priority — P4.38

The tested official endpoints do not expose the required 2024 records through the current API routes. Next, perform a controlled secondary-source triangulation for all four dates:
1. Retrieve date-specific EOD records from at least two independent providers (e.g. ShareSansar, Merolagani, NepseAlpha).
2. Compare OHLC, volume and turnover against the pinned third-party floorsheets and canonical snapshot.
3. Investigate the SMPDA `contract_no` repetition anomaly against original provider schemas.
4. Keep primary-source status explicitly unresolved; do not promote lifecycle dates or assert `NO_TRADE` without complete session evidence.
