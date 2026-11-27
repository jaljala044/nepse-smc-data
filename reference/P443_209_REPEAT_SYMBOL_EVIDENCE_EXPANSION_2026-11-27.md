# P4.43 — evidence expansion for 209 uncovered repeated-OHLCV symbols

Date: 2026-11-27  
Pinned OHLCV audit input: `56362fb4f65b91fdcca8f50b50e53ad80e703649`  
Branch: `p443-global-integrity-audit`

## Outcome

The identity/source search has been completed for the previously uncovered 209 repeat-finding symbols. It narrows the instrument universe and identifies concrete evidence sources, but it does **not** validate the 23,377 repeated adjacent-tuple pairs as date shifts. No source dates or OHLCV values are changed.

## Reconciled identity evidence

The row-level identity triage is preserved in `P443_UNCOVERED_REPEAT_SYMBOL_IDENTITY_TRIAGE_2026-11-27.csv` (209 symbols; source blob `52debaa4c70d5adc968a8b9ea6986095c29bbe15`). Its companion report records:

- 183/209 symbols have exact current-snapshot matches after decoding URL-escaped slash characters in filenames.
- 26/209 have no exact match in the 2026-11-25 current security snapshot.
- 39 symbols are classified as mutual funds in the dated target-candidate register.
- Three symbols (NESDO/8041, ULBSL/8063, YMHL/9342) match the current equity crosswalk.
- 71 snapshot display names are debt/debenture candidates and 67 are promoter-share candidates. These are display-name clues, not authoritative instrument-type fields.
- Ten records were separately routed to class review; the captured NEPSE security-list schema has no instrument-type field.

These categories are not additive and must not be treated as a historical instrument classification.

The eight URL-escaped filename matches are current-snapshot matches only. They do not establish historical ID continuity, original listing dates, or effective-dated aliases.

## Primary-source evidence located

### NEPSE current security-list capture

The pinned scanner repository contains a NEPSE-hosted security-list response captured on 2026-11-25 (573 records; raw response SHA-256 recorded in that repository's evidence manifest). The captured fields include ID, symbol, security name, active status and related display fields, but not an instrument-type field or historical validity intervals.

This is useful for current ID matching. It is not a historical instrument master.

### NEPSE per-security history capture

The scanner repository also contains raw NEPSE per-security history response files for 281 current-equity candidates over 2026-10-05 through 2026-11-26. The window audit explicitly labels the data review-only, disallows canonical promotion and coverage admission, and warns that the 281-equity subset is not the full market universe. The endpoint's normalized fields are business date, trades, volume and turnover; it does not provide OHLC prices.

Three symbols in the 209-symbol set are current equity-crosswalk matches and appear in the captured history directory: NESDO, ULBSL and YMHL. The raw response files are retained in the scanner repository and have per-file SHA-256 entries. They still require content parsing and a date-key join before they can support any row-level finding. The captured window cannot adjudicate older rows outside its date range.

### Third-party instrument-type source lead

ShareHub's published API documentation describes:
- `GET /data/api/v1/nepse-data/companies`, with an `instrumentType` field; and
- `GET /data/api/v1/nepse-data/security/all/mini`, with security ID, symbol, name and active/promoter flags.

The documentation states that the API requires a licensed account, bearer token or API key, and an allow-listed server IP. No authenticated payload was available or captured in this task. Therefore this is a source lead, not acquired evidence, and no rows from it were added.

### Floorsheet archive limitation

Existing archive research provides useful date-specific trade evidence, but the captured samples have known daily shortfalls and unresolved source-completeness / rights questions. A missing symbol in a third-party floorsheet is not evidence of no trade. Only a complete, date-matched, identity-verified partition can be used for a positive per-security execution check.

## What is now established vs unresolved

| Question | Status |
|---|---|
| Current security-ID match for 183 symbols | Matched to dated current snapshot only |
| Current-snapshot absence for 26 symbols | Confirmed absence from that snapshot; historical identity unresolved |
| Instrument class for 39 mutual-fund candidates | Target-candidate register classification; historical effective intervals unresolved |
| Instrument class for 71 debt and 67 promoter candidates | Display-name candidates only |
| Historical stable IDs / symbol aliases / valid-from and valid-to | Not established for the full set |
| NEPSE security-history coverage for 2026-10-05 to 2026-11-26 | Captured for 281 current-equity candidates; review-only |
| Date-specific evidence for all 23,377 repeated pairs | Not complete |
| Automatic date shift, correction or promotion | Not authorized; zero performed |

## Next task: P4.44 — acquire effective-dated all-instrument identity and date-key evidence

1. Acquire a directly captured, reproducible all-instrument security master with instrument type, stable ID, symbol, status and source provenance. Prefer NEPSE primary records; use licensed third-party data only as a separately tiered cross-check.
2. Acquire effective-dated listing, trading release, suspension, resumption, merger/successor and delisting events. Keep listing date distinct from first executed trade.
3. Parse and audit the existing NEPSE per-security history responses for the three current-equity matches in this set, starting with the overlap inside 2026-10-05 to 2026-11-26. Preserve raw bytes and hashes; compare only business-date, trades, volume and turnover fields the endpoint actually supplies.
4. Resolve the remaining 26 no-current-snapshot symbols with exchange notices, archived security lists and dated source evidence. Do not infer IDs from ticker resemblance.
5. Build a date-keyed evidence matrix for the 23,377 repeated pairs. Keep source date, candidate business date, source row identity, session evidence and per-security execution evidence separate. Any missing, conflicting or duplicate match stays HOLD/UNKNOWN.
6. Re-run the full-scope date-lineage join only after the identity and evidence inputs are pinned. Publish a coverage manifest and tests; do not alter raw/canonical OHLCV during evidence acquisition.

## Safety and disposition

All 23,377 repeated-pair findings remain HOLD/UNKNOWN for date-lineage purposes. Current identity matching does not prove the historical security was the same instrument on the source date. Missing official rows are UNKNOWN, not zero trading. No raw or canonical OHLCV was edited, shifted, deleted, deduplicated, corrected or promoted.

**P4.43 identity-source discovery subtask: complete. P4.43 full-scope date-lineage acceptance: still blocked. P4.44 is the next active evidence-acquisition task.**
