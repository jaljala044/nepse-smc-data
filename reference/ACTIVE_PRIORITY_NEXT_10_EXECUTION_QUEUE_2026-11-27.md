# Active priority next-10 execution queue — 2026-11-27

Repository: `jaljala044/nepse-smc-data`  
Branch: `p443-global-integrity-audit`  
Prior queue: `reference/ACTIVE_NEXT_10_EXECUTION_QUEUE_2026-11-27.md` (#31–#40)

This queue continues with packages #41–#50. It does not replace or reopen earlier work. Completed items below refer to read-only audit/documentation deliverables, not resolution of the underlying market-data gaps.

## Work packages #41–#50

| # | Priority work package | Status | Evidence / acceptance |
|---:|---|---|---|
| 41 | Reconcile the 281-payload history audit report with the latest full strict artifact | COMPLETE | Superseding read-back appended to `P444_281_SECURITY_HISTORY_CAPTURE_AUDIT_2026-11-27.md`: 281/281 payloads, 8,142 rows, 281/281 manifest matches, zero row issues, no Open field in any payload. Earlier three-symbol-only wording is explicitly marked intermediate. |
| 42 | Investigate BENH's shorter per-security history window without inferring no-trade dates | COMPLETE — coverage anomaly documented | BENH has 22 rows vs ACLBSL's 29 observed date keys; missing BENH keys are 2026-10-05/06/07/08/09 and 2026-10-12/13. BENH has an explicit zero-trade row on 2026-10-14. The seven missing keys remain UNKNOWN; market-wide observations for security ID 8108 do not prove BENH trading status. Report appended to the 281-payload audit. |
| 43 | Inventory and audit official NEPSE holiday API captures for 2015–2025 | COMPLETE — source-capture audit only | New report `reference/NEPSE_OFFICIAL_HOLIDAY_CAPTURE_AUDIT_2015_2025_2026-11-27.md`: 11/11 yearly captures, HTTP 200, 458 records, 457 unique dates, one 2020 duplicate date with two descriptions. All 458 rows have null id/instrumentTypeId/activeStatus. No open sessions promoted; hashes are report/manifest metadata, not independently recomputed raw-byte hashes. |
| 44 | Verify full P4.43 workflow on the exact current branch head and read back artifacts | PARTIAL — latest full run passed; exact branch-head SHA not directly tested | Run #336 (`46043405148`) passed all 59 steps on code SHA `c261b1c0e3c64cd1268a92eaaf0690cb028a738d`; global and strict artifact ZIP SHA-256 values match GitHub metadata. The subsequent branch/PR-head commits were documentation-only (the two queue/read-back documents); no code delta followed the tested SHA. Code validation is therefore current, but the literal exact-head run criterion is not met. PR #80 remains draft/open/unmerged. |
| 45 | Acquire date-matched per-security execution evidence for the 640 repeated-pair rows belonging to NESDO, ULBSL and YMHL | BLOCKED | Existing 281-symbol history window contains zero endpoint-date overlap. Need new primary date-matched payloads or complete timestamped floorsheets plus historical-ID continuity evidence. Current symbol IDs are not sufficient for old dates. |
| 46 | Obtain an all-instrument master with instrument class and effective-dated identity fields | BLOCKED | Current NEPSE snapshot has 573 rows but no instrument class or historical valid-from/valid-to fields. Obtain official or authorised raw response with provenance and rights, then reconcile against the 525 OHLCV files and 209-symbol matrix. |
| 47 | Resolve the 21 symbols still lacking supported current-snapshot identity or successor mapping | BLOCKED | The 26-symbol residual review has five predecessor-to-successor merger mappings already supported; do not re-open those five. Resolve remaining symbols only with dated official security lists/notices and stable IDs. |
| 48 | Recover primary lifecycle event dates for the four review findings in the 26-row ledger | BLOCKED | Missing event dates: NICAD8283 delisting, NICGF delisting, SAMAJ merger-successor event, SBLD2082 delisting. Obtain source documents/raw bytes and effective-date evidence; no date inference from last observed trades. |
| 49 | Obtain timestamped primary source evidence for 2025-07-28 floorsheet reconstruction | BLOCKED | YONEPSE archive parses 170,726 rows but trade timestamps are blank; no Open/Close ordering may be inferred from contract IDs or unverified sequence sorting. Need complete official timestamped pages or a documented independently validated ordering source. |
| 50 | Establish independent lineage and historical coverage for the 1,368 P4.35 OHLCV flags | BLOCKED | Existing 1,283 exact matches are ShareSansar-derived and not independent; 85 rows are absent. Require independently documented upstream source, raw/adjusted basis, immutable revision, exact-date coverage and permission. Keep all 1,368 UNKNOWN. |

## Guardrails

1. Keep raw captures, OHLCV, canonical calendar, lifecycle dispositions and scanner inputs unchanged.
2. No promotion, date relabeling, deduplication, correction, or hold release from these audit reports.
3. A holiday-list absence is not proof of an open session; a missing per-security row is not proof of no trade.
4. Keep source identity, historical security ID, instrument class, session status and execution evidence as separate fields.
5. Preserve merger predecessor history. Use successor identities only for current lookups, never as predecessor historical IDs.
6. Mark tasks complete only when their stated evidence acceptance is met; do not turn blocked source acquisition into a completed task by writing a handoff note.

## Current stopping point

Packages #41–#43 remain complete as documentation/read-only audits. #44 remains PARTIAL: Run #336 passed 59/59 steps on `c261b1c0e3c64cd1268a92eaaf0690cb028a738d`; subsequent changes are documentation-only, so code validation is current but exact-head execution is not directly evidenced. #45–#50 remain blocked pending new source evidence or their stated acceptance criteria.
