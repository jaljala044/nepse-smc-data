# Active next-10 continuation queue — 2026-11-27

Repository: `jaljala044/nepse-smc-data`  
Working branch: `p443-global-integrity-audit`  
Queue predecessor: `reference/ACTIVE_NEXT_30_EXECUTION_QUEUE_2026-11-27.md`  
Current branch head at creation: `e3c9e3302c3fea02ebbc1e1517e785c8b711d49d`

This continuation defines work packages #31–#40 from the still-open acceptance criteria in issues #4, #27, #31, #56 and #82. It does not reopen completed packages or replace the prior queue. “Complete” below means the named audit/check was completed; it does not mean the underlying historical evidence gap is resolved.

## Evidence checkpoint used to scope this batch

- P4.43 global-integrity Run #325: `46037025935`, conclusion `success`, tested code SHA `aae6050f9b366125a00aebf5b4c4d65e4ac3e553`.
- Strict artifact ID: `15219745781`; size 58,304,773 bytes; GitHub digest `sha256:140f1543d70f648fe8f6f2c70e994ae49ca33a6b8a1e152f8bc5aa6361a8c009`.
- Global artifact ID: `15219330875`; size 1,403,274 bytes; GitHub digest `sha256:7ac9cd45f927efba5afc2d708fdc315e905d49cf3816446b07bd148ec97a6d44`.
- The strict artifact was downloaded and inspected. It contains the 281-payload audit, lifecycle sequence audit, 23,377-pair endpoint coverage audit and matrix read-back report.
- The tested SHA is an ancestor of current branch head. Comparison from tested SHA to current head shows two commits, both documentation-only changes to the prior queue and the repeat-pair evidence audit note. No code changed after Run #325, but an exact-head workflow run is still preferred and has not been observed.
- No raw OHLCV, floorsheet, lifecycle, canonical or scanner-input data was changed or promoted in this continuation pass.

## Work packages #31–#40

| # | Work package | Status | Evidence / next acceptance |
|---:|---|---|---|
| 31 | Audit all 281 pinned NEPSE per-security history payloads and preserve missing-field semantics | COMPLETE — 281/281 manifest hashes match; 8,142 rows; zero row issues; no Open field in 281/281 payloads; valid audit; promotion disallowed | Audit output: `P444_281_SECURITY_HISTORY_CAPTURE_AUDIT_2026-11-27.json`. This is a point-in-time payload audit, not historical-ID continuity evidence. |
| 32 | Measure exact-symbol and exact-date execution coverage for all 23,377 repeated pairs | COMPLETE — 23,377 pairs / 209 symbols; 46,754 endpoint occurrences; 0 covered; 34,099 unique endpoint dates, 0 covered; exact ticker intersection NESDO, ULBSL, YMHL only | Audit output: `P444_REPEAT_PAIR_CAPTURE_ENDPOINT_COVERAGE_2026-11-27.json`. Current capture dates do not overlap the pair endpoints; no alias or no-trade inference. |
| 33 | Run the lifecycle event-sequence audit on the 26-row evidence ledger | COMPLETE — 26 rows / 26 symbols; four review findings; zero errors, mutations, promotions or disposition changes | Audit output: `P444_LIFECYCLE_SEQUENCE_AUDIT_2026-11-27.json`. Review findings: missing dates for NICAD8283, NICGF, SAMAJ and SBLD2082. Obtain primary event-date evidence before editing ledger rows. |
| 34 | Validate P4.43 global audit on the latest branch head and read back artifacts | PARTIAL — Run #325 passed on `aae6050f9b366125a00aebf5b4c4d65e4ac3e553`; current head `e3c9e3302c3fea02ebbc1e1517e785c8b711d49d` is two documentation-only commits ahead | No code delta since tested SHA, but rerun or record an exact-head workflow result before claiming exact-head validation. PR #80 remains draft/open/unmerged. |
| 35 | Acquire date-matched primary execution evidence for NESDO, ULBSL and YMHL pair endpoints | BLOCKED — current 281-symbol capture contains no endpoint-date overlap | Need primary NEPSE per-security history or complete timestamped floorsheets covering exact dates; current ticker match alone does not establish historical ID continuity. |
| 36 | Resolve the 21 remaining unmatched symbols in the 209-symbol identity triage | BLOCKED — no supported current successor/security mapping for these 21 symbols in the reviewed snapshot | Obtain archived NEPSE security lists or dated lifecycle notices with stable IDs; preserve the five established merger edges and predecessor histories. |
| 37 | Acquire an all-instrument NEPSE master with instrument class and effective-dated identity fields | BLOCKED — current snapshot has 573 records but lacks instrument class and historical validity intervals | Require raw exchange-origin response/document, retrieval metadata, hashes, stable ID, symbol, class, status and effective-date evidence; reconcile against the 525 OHLCV symbol files. |
| 38 | Extend positive-open session evidence earlier than 2025-11-26 and verify schedule-transition notices | PARTIAL/BLOCKED — 228 positively evidenced open dates cover only 2025-11-26 through 2026-11-25; 2026 closure capture is closure-only | Obtain dated official EOD witnesses and byte-preserved exchange schedule notices; never infer open sessions from weekdays or holiday-list absence. |
| 39 | Recover timestamped primary-source evidence for 2025-07-28 floorsheet Open/Close reconstruction | BLOCKED — 170,726 YONEPSE rows parse, but all timestamps are blank; alternate SocrateAI file also has no trade-time field | Request original NEPSE response/capture from archive maintainer with endpoint, request parameters, retrieval time, raw bytes, pagination totals and SHA-256. Do not infer order from contract IDs. |
| 40 | Establish independent lineage, raw/adjusted basis and permitted provenance for the 1,368 P4.35 flags | BLOCKED — no candidate has passed independent-lineage and historical-coverage gates; SocrateAI provenance/rights remain unverified | Require documented upstream source/capture method, rights/permission, immutable revision and exact date-matched coverage for the 1,283 matched and 85 absent keys. Keep all flags UNKNOWN. |

## Execution guardrails

1. Do not duplicate or overwrite completed work packages #1–#30; this file is a continuation only.
2. Keep all raw source files, canonical OHLCV and scanner inputs unchanged.
3. Preserve all merger predecessor history. Use confirmed successor codes only for current-security lookup; never reuse successor IDs as predecessor historical IDs.
4. Do not infer Open/Close from contract IDs, sequence labels, blank timestamps, or unverified sort parameters.
5. Keep unresolved pair rows and the 86 July 2025 conflicts quarantined. Missing evidence is not evidence of no trade.
6. No promotion, date relabeling, deduplication, scoring change or hold release is authorized by these audit results.

## Current stopping point

The three available machine audits (#31–#33) are complete and read back. The remaining seven packages require exact-head CI evidence or new primary-source material; they are not marked complete merely because the next action is documented.


## Live recheck addendum — 2026-11-27 20:00 UTC

- Rechecked branch head: `p443-global-integrity-audit` = `c3084ac8a1b7682acd9a4497699b35a06457379a`.
- Work package #34 is now **COMPLETE for exact-head CI**: P4.43 workflow run #340 (`46056596815`) completed successfully on that exact SHA. This supersedes the earlier #325 ancestor-only checkpoint. PR #80 remains draft/open/unmerged; CI success is not PR acceptance.
- Work package #35 remains **BLOCKED**: the 281 official per-security history payloads cover 2026-10-05 through 2026-11-26 and contain no Open field; their dates do not overlap the 23,377 pair endpoint dates. No primary endpoint evidence can be derived from those captures.
- **Next active item: #36 — resolve the 21 unmatched symbols.** Preserve the five supported current successor edges (JALPA/KLBSL→MATRI; SABSL/SDLBSL→SMPDA; SAMAJ→GBLBS) strictly as current-identity links. They do not establish predecessor historical IDs or effective dates. The next pass must seek archived exchange security lists / primary lifecycle notices for the remaining 21, record raw-byte provenance, and leave unsupported mappings HOLD/UNKNOWN.
- Rechecked the app/web repo as well: PR #241 has since merged to `main`; PRs #240 and #243 remain open draft PRs with passing relevant CI. PR #245/#246 are stacked draft work and their checks pass, but they are not merged to main.
- No raw OHLCV, floorsheet, lifecycle, canonical, scanner-input or identity-ledger records were changed in this recheck. No promotion or hold release occurred.
