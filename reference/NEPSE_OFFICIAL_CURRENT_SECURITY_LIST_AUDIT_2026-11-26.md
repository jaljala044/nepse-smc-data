# Official NEPSE current security-list audit — 2026-11-26

## Decision

**Current equity identifier crosswalk: evidence-backed for the 281-symbol current equity universe as of the captured NEPSE security-list snapshot. Historical identity intervals and instrument classification are not established by this endpoint.**

This audit corrects the earlier blanket statement that no official security-list snapshot was available. It does not close the historical session-calendar work in Issue #4, and it does not authorize historical ticker splicing or canonical OHLCV changes.

## Primary source capture

- Source: NEPSE official security list
- Endpoint: `https://nepalstock.com.np/api/nots/security?nonDelisted=true`
- HTTP: 200
- Response headers: `content-type: application/json`; `server: nepse-website`
- Captured response SHA-256: `5495d99a73aeb44e573936f59fc6a6d8dbf9ffc45c5a8ba62e672f0b0c6fa2f7`
- Response bytes: 87,572
- Parsed records: 573
- Unique symbols: 573
- Unique numeric IDs: 573
- Active status: 546; suspended status: 27
- Fields actually present: `id`, `symbol`, `securityName`, `name`, `activeStatus`
- Fields not present: instrument type, listing date, delisting date, effective-dated symbol/name history.

The same response hash is recorded in two retained capture contexts:
1. 2026-11-25 conflict-archive capture: `data/evidence/raw/nepse/conflict-ohlcv/2026-11-25/responses/security-list.response-body.bin`, with `SHA256SUMS` and capture report.
2. 2026-11-26 official per-security history capture: `data/evidence/raw/nepse/security-history/2026-11-19_to_2026-11-24/security-list-response-01.bin`. Its capture report records the endpoint, HTTP 200, NEPSE server header, retrieval header timestamp `2026-11-26T16:04:44Z`, and the same SHA-256.

The raw response and parsed representation are preserved in the companion scanner repository:
- [Raw response](https://github.com/jaljala044/nepse-elite-ai-scanner-pro/blob/56b2a5c887e40f792bf0cea5c52d1b480abba78f/data/evidence/raw/nepse/security-history/2026-11-19_to_2026-11-24/security-list-response-01.bin)
- [Capture report](https://github.com/jaljala044/nepse-elite-ai-scanner-pro/blob/56b2a5c887e40f792bf0cea5c52d1b480abba78f/data/evidence/raw/nepse/security-history/2026-11-19_to_2026-11-24/capture-report.json)
- [Parsed response from the 2026-11-25 capture](https://github.com/jaljala044/nepse-elite-ai-scanner-pro/blob/56b2a5c887e40f792bf0cea5c52d1b480abba78f/data/evidence/raw/nepse/conflict-ohlcv/2026-11-25/responses/security-list.parsed-response.json)
- [SHA-256 manifest for the 2026-11-25 capture](https://github.com/jaljala044/nepse-elite-ai-scanner-pro/blob/56b2a5c887e40f792bf0cea5c52d1b480abba78f/data/evidence/raw/nepse/conflict-ohlcv/2026-11-25/SHA256SUMS)

The two retained payload copies have the same content hash; they are repeated observations of the same current list, not independent historical master snapshots.

## Equity crosswalk reconciliation

The companion repository's `data/reference/nepse_equity_security_id_crosswalk_2026-11-26.csv` was independently checked against the captured list and the OHLCV-file-presence flags:

| Check | Result |
|---|---:|
| Current equity crosswalk rows | 281 |
| Unique symbols | 281 |
| Unique security IDs | 281 |
| Active status `A` | 281 |
| Matching OHLCV file present | 281 |
| Crosswalk status `snapshot_id_match_active_status_A` | 281 |
| Duplicate IDs or symbols in the full 573-row list | 0 |

The dated crosswalk is stored at [nepse_equity_security_id_crosswalk_2026-11-26.csv](https://github.com/jaljala044/nepse-elite-ai-scanner-pro/blob/56b2a5c887e40f792bf0cea5c52d1b480abba78f/data/reference/nepse_equity_security_id_crosswalk_2026-11-26.csv). The underlying current security snapshot is [nepse_security_id_snapshot_2026-11-25.csv](https://github.com/jaljala044/nepse-elite-ai-scanner-pro/blob/56b2a5c887e40f792bf0cea5c52d1b480abba78f/data/reference/nepse_security_id_snapshot_2026-11-25.csv).

As an additional point-in-time consistency check, the 2026-11-26 official per-security history capture queried all 281 crosswalk IDs. All 281 returned HTTP 200, matched the current security-list ID, and had one complete page for the requested 2026-11-19 through 2026-11-24 window: 1,124 rows over four observed business dates (2026-11-19, 2026-11-20, 2026-11-23, 2026-11-24). The capture explicitly labels these rows `ROWS_RETURNED_REVIEW_ONLY`; it sets `historical_security_identity_verified=false` for all 281. This is a current-ID/API consistency check, not historical identity proof or OHLCV promotion.

## Safe interpretation

1. The 281 current equity symbols can use the captured NEPSE numeric security IDs as **current-snapshot identifiers**, subject to the snapshot date and source hash.
2. Do not backfill these IDs onto predecessor symbols or earlier dates.
3. The endpoint does not provide instrument type or lifecycle dates. The 281-equity scope comes from the separately maintained equity-universe manifest, not from a type field in this response.
4. The 10 predecessor-to-successor historical ID intervals previously audited remain unresolved. Keep their stable IDs and effective dates null; do not splice predecessor and successor OHLCV.
5. The 573-row list includes non-equity instruments and suspended securities. Do not treat all 573 as the current equity universe.
6. No session-calendar claims are changed. The holiday API remains closure evidence only; weekday candidates are not promoted to verified open sessions.

## Issue #4 disposition

This completes the **current equity security-ID snapshot reconciliation** subtask. It does not complete Issue #4. Remaining blockers are:
- Primary, dated NEPSE trading-schedule transition notices and byte-preserved evidence.
- Positive verified-open session evidence and historical calendar completeness; no weekday-only inference.
- Effective-dated instrument type and lifecycle evidence where historical continuity is required.
- Full discrepancy reporting and CI verification across the bounded calendar and equity reference datasets.

No canonical OHLCV, floorsheet, calendar, lifecycle date, training label, score or signal was changed by this audit.
