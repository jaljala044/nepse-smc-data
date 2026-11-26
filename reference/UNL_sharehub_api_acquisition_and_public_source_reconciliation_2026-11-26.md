# UNL ShareHub API acquisition and public-source reconciliation — 2026-11-26

## Decision
**UNL historical recovery remains blocked at source acquisition.** ShareHub documents the exact all-history endpoint and response contract, but the service is licensed/authenticated and IP-restricted. No project-owned ShareHub Data API credentials, service entitlement, or allow-listed runner IP were available in this work session. The endpoint did not yield a data payload through the available public web reader. No credentials were requested, guessed, stored, or committed.

## 1. ShareHub endpoint verified from public documentation
Documentation: https://sharehubnepal.com/data/nepse-data-documentation/

- Service: `price-history`
- Method/path: `GET /data/api/v1/nepse-data/price-history/{symbol}`
- UNL request period: `time=ALL` (documented as history from listing)
- Base URL: `https://sharehubnepal.com/data/api/v1/nepse-data`
- Response envelope: `success`, `code`, `message`, `data`
- Data fields: `time` (numeric timestamp), `symbol`, `open`, `close`, `high`, `low`, `volume`
- Authentication: Bearer access token, obtained using a ShareHub Data API account.
- Access control: licensed Data API account, endpoint service enabled on licence, and calling server IP allow-listed.
- Access token lifetime documented as 30 minutes; refresh token as 30 days.
- IP allow-listing requires calling the documented `my-ip` endpoint from the actual server and having ShareHub add that IP to the licence.
- Rate limits are licence-specific.

Relevant docs sections also describe 401/403 outcomes for invalid token, non-Data-API account, missing/expired/suspended licence, disabled service and non-allow-listed IP.

## 2. Acquisition readiness
| Requirement | Status |
|---|---|
| Endpoint and ALL-history semantics documented | VERIFIED |
| Response schema documented | VERIFIED |
| ShareHub public UNL price-history page exists | VERIFIED |
| Data API account available to this project session | NOT PROVIDED |
| price-history service entitlement confirmed | NOT PROVIDED |
| project runner IP allow-listed | NOT DONE |
| authenticated ALL response captured | NOT AVAILABLE |
| source payload/hash and retrieval timestamp | NOT CAPTURED |
| OHLCV/session/calendar validation on ShareHub payload | NOT RUN |
| rights/redistribution terms approved for project storage | NOT ESTABLISHED |

**Conclusion:** the documented API is a credible acquisition route, not acquired evidence. Do not represent it as a successful download or as an independently validated dataset.

## 3. Public-page and recent-history cross-check
Public pages inspected:
- ShareHub UNL price history: https://sharehubnepal.com/company/UNL/price-history
- ArthaKendra UNL price history: https://www.arthakendra.com/stock-market/company/UNL/price-history
- Dharke UNL page: https://www.dharke.com/stocks/UNL
- NepView UNL page: https://nepview.com/explore/UNL
- NEPSE Alpha UNL search/info pages: https://nepsealpha.com/search?q=unl and https://nepsealpha.com/stocks/UNL/info

The public pages expose recent daily data (mostly 2026 and limited 1-year/15-session samples) but do not provide a verified downloadable full-listing daily OHLCV payload in the evidence captured here. Similar recent figures across pages are not automatically independent corroboration: shared upstream vendors or copied feeds have not been ruled out. This limited recent sample cannot validate the 2011–2024 history or repair the project archive.

ShareHub's public UNL page reports listing date 1994-09-22. This confirms that the project CSV's 2024-03-05 first row is not the listing boundary; it remains a source-coverage boundary.

## 4. Required acquisition procedure once project access is authorized
1. Use the project's designated server/runner, not a developer laptop or public browser, to call ShareHub's `my-ip` endpoint and register that IP with ShareHub.
2. Confirm a Data API account, the `price-history` service entitlement, licence start/end dates and rate limits with the account owner.
3. Keep email/password, access token and refresh token in the approved secret manager only; never in Git, logs, issue comments or client-side code.
4. Request `GET /price-history/UNL?time=ALL` with the Bearer token.
5. Persist the untouched response bytes, HTTP status/headers, request URL (without token), UTC retrieval timestamp, response hash, source identity and licence/terms reference in immutable raw storage.
6. Parse `time` using the documented timestamp semantics only after confirming whether it represents UTC midnight, local session date, or another bucket convention. Do not guess timezone/date.
7. Validate finite numeric fields, `high >= max(open, close, low)`, `low <= min(open, close, high)`, non-negative volume, unique session dates, exchange-session calendar membership, chronological ordering, plausible price/volume jumps and corporate-action boundaries.
8. Compare a sample of daily rows against a genuinely independent source and executed floorsheet/session evidence. Shared vendor lineage is not independent confirmation.
9. Preserve all raw source rows. Put any rejected records in a quarantine/exception layer; never rewrite or shift raw dates.
10. Promote only after source rights, provenance, date mapping, row-level checks and independent sample reconciliation are signed off.

## 5. Existing UNL source status remains unchanged
- Project history-starter CSV: 845 rows, 2024-03-05 to 2026-11-20.
- Prior alternate public CSV: 2,018 rows, 2011-03-28 to 2026-11-26; 362 rows failed OHLC validation, including 361 pre-2024 rows.
- All 545 overlapping dates between the two CSVs matched numerically, which is consistency but not independent confirmation.
- Separate session-date audit found 226 of 845 project rows dated on non-session weekdays under the documented market-week regime. Do not ingest these as trading sessions without independent evidence.
- No raw data was changed, spliced, shifted, repaired, deleted, or promoted in this acquisition task.

## 6. Disposition
**UNL historical data: QUARANTINE / LOW CONFIDENCE for historical indicators, backtests, model training and historical signals.** This is not a rejection of ShareHub as a potential source; it is a hold pending authorized access and successful evidence capture/validation.

Next project action after authorized API access: retrieve the raw ALL response and run the validation sequence above. Until then, continue with independently obtainable sources and do not fabricate a recovered history.
