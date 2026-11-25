# Instrument-master source acquisition note — 2026-11-26

## Purpose
Record a concrete source lead for completing the instrument register without treating a third-party schema description as captured data or official NEPSE evidence.

## Source reviewed
- ShareHub NEPSE data documentation: https://sharehubnepal.com/data/nepse-data-documentation/
- Reviewed: 2026-11-26
- The documentation describes a `companies` service at `GET /data/api/v1/nepse-data/companies` with fields including `symbol`, `name`, `sector`, `listedShares`, `paidUpCapital`, `faceValue`, `listingDate`, `activeStatus`, and `instrumentType`.
- The same documentation describes security-related data with a `securityId` field in other response structures. It does not establish from the documented companies response alone that every instrument row has a stable security ID.
- This is a third-party data-provider schema, not an official NEPSE publication. It is suitable as a cross-check/discovery source, not as the sole authority for canonical historical lifecycle mappings.

## Retrieval attempt and limitation
- The documented API route was tested through the available web retrieval path but was not accessible there.
- No API response body, HTTP status, retrieval timestamp, or raw-payload checksum was obtained.
- No data rows have been fabricated or inserted into `nepse_instrument_register_template.csv`.
- Authenticated access or a direct raw-response export is still required to capture the actual provider payload. Any captured response must retain its URL, retrieval timestamp, response status, raw bytes, SHA-256, and provider/source tier.

## Next execution
1. Capture the actual companies and securities-list responses from a permitted authenticated session or another directly accessible endpoint.
2. Preserve immutable raw payloads and checksums before parsing.
3. Compare the resulting symbols/IDs with all 525 OHLCV filenames; report unmatched, duplicate, inactive, and ambiguous mappings.
4. Seek official NEPSE evidence for disputed lifecycle and security-ID fields before canonical promotion.
5. Keep unsupported historical listing/delisting and rename dates null/quarantined.

## Status
Source discovery advanced; instrument data acquisition is **not complete**. This note does not satisfy Issue #4 acceptance criteria and must not be represented as a verified instrument master.
