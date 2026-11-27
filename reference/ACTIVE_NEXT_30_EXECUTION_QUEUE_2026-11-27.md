# Active next-30 execution queue — 2026-11-27

Repository: `jaljala044/nepse-smc-data`  
Working branch: `p443-global-integrity-audit`  
Base reviewed before queue creation: `4630178881feceb9a1d9faa3c1f00dd8021790c0`  
Scope: open work tracked by P4.43 (#74), P4.44 (#82), session/instrument register (#4), P4.23 (#27), P4.23.2 (#31), and P4.35 (#56).

This queue decomposes the open acceptance criteria into 30 reviewable work packages. It is **not** a declaration that all 30 are complete. Statuses are evidence-based. Existing raw/canonical files are preserved; no unresolved record is promoted.

## P4.44 — identity, lifecycle and execution evidence

| # | Work package | Status | Acceptance / dependency |
|---:|---|---|---|
| 1 | Capture original bytes for the six already identified NEPSE lifecycle PDF leads; record UTC retrieval, byte length, SHA-256 and Git blob SHA | PARTIAL — readable rendering only for two PDFs; direct binary capture failed; see `P444_PRIMARY_DOCUMENT_CAPTURE_ATTEMPT_2026-11-27.md` | Raw unmodified payloads and reproducible hashes |
| 2 | Recover the official all-instrument security master with instrument class, stable ID, symbol and status | PARTIAL — 573-row current snapshot parsed; no class field or effective-dated history | Exchange-issued raw response and provenance |
| 3 | Establish effective-dated symbol/name/ID mappings for all 209 repeated-pair symbols | PARTIAL — 183 direct current-snapshot matches plus 5 predecessor aliases mapped to 3 successor IDs (MATRI/694, SMPDA/2896, GBLBS/583); 21 symbols still lack a supported current mapping; historical predecessor IDs remain unverified; see `P444_MERGER_SUCCESSOR_CURRENT_ID_CROSSWALK_2026-11-27.csv` | No ticker-similarity inference; explicit unmatched set |
| 4 | Resolve the 26 residual symbols against archived NEPSE security lists | PARTIAL — 5 merged predecessors now mapped to current successors; 21 residual symbols still lack a supported successor mapping; predecessor historical IDs remain unverified; see `P444_MERGER_SUCCESSOR_CURRENT_ID_CROSSWALK_2026-11-27.csv` | Historical IDs or explicit unresolved reason per symbol |
| 5 | Reconcile JALPA/KLBSL → MATRI merger dates and distinguish integrated-business date from last trade | PARTIAL — NEPSE-hosted notice supports integrated operations from 2024-07-11; last exchange trade boundary and raw PDF bytes remain unverified; see `P444_JALPA_KLBSL_MERGER_BOUNDARY_REVIEW_2026-11-27.md` | Primary raw notice plus exchange trading boundary |
| 6 | Resolve SABSL/SDLBSL → SMPDA conflicting 2024-07-14 vs 2025-07-14 claims | PARTIAL — both claims retained; NEPSE-hosted PDF bytes/read-back and exchange trading boundary unavailable; see `P444_SABSL_SDLBSL_DATE_CONFLICT_REVIEW_2026-11-27.md` | Date-authentic primary notice and effective-date interpretation |
| 7 | Recover cancellation notices and raw payload provenance for NICAD8283, NICGF and SBLD2082 | PARTIAL — three notice leads/date conversions catalogued; original PDF bytes and hashes still absent; see `P444_THREE_CANCELLATION_NOTICE_PROVENANCE_REVIEW_2026-11-27.md` | Original PDFs, SHA-256 and unambiguous Bikram Sambat/Gregorian date conversion |
| 8 | Complete lifecycle event ledger schema validation (event types, dates, source tier, confidence, ID, successor) | IMPLEMENTED — seven validator regression tests passed in publication-gate run #19; overall workflow failed at private Drive verification | Requires all 15 ledger columns; validates event/date/tier/confidence, verified ID/provenance, successor and duplicate/conflict checks; no promotion |
| 9 | Audit effective-date interval overlaps and impossible lifecycle sequences | IMPLEMENTED — regression tests and compile passed in run #18; overall workflow failed at private Drive verification | Review-only findings; no dates inferred and no holds released |
| 10 | Parse and verify the existing 281 per-security NEPSE history captures without treating current IDs as historical IDs | COMPLETE — latest run 46033103956 audited all 281/281 payloads: 8,142 rows, all manifest hashes match, zero row issues; no Open field in any payload; see `P443_P444_ACTIVE_10_TASK_BATCH_READBACK_2026-11-27.md` | Point-in-time capture only; no historical-ID continuity inferred |
| 11 | Build exact per-security execution evidence for every repeated-pair endpoint date | BLOCKED — new exact-symbol/date coverage audit added; pinned 281-capture overlaps only NESDO/ULBSL/YMHL with 640 pair rows, but 0 endpoint dates fall in capture window; CI regression and audit steps passed in Run #325 (overall workflow still running) | Requires date-matched primary execution payloads joined through verified historical identity; no alias inference |
| 12 | Expand the 23,377-pair matrix with source row identity, stable-ID confidence, session evidence and per-security evidence | PARTIAL — Run #334 passed all workflow steps; strict artifact JSON now parses with a real newline and validates 23,377 rows / 209 symbols / 23,377 unique pair IDs / zero issues. Execution bundles and historical stable IDs remain absent for all rows; all remain held | Matrix structure/read-back complete; actual historical execution evidence and verified IDs still required |

## P4.43 — global integrity and canonical quarantine

| # | Work package | Status | Acceptance / dependency |
|---:|---|---|---|
| 13 | Revalidate 928-file inventory and pinned blob/byte metadata | COMPLETE — 928/928 inventory entries checked against pinned blob SHA and byte count; zero file failures; run 46033103956 | Reproducible pinned inventory; disclose unsupported files |
| 14 | Complete content parsing for the 138 inventory-only/unsupported files where formats permit | COMPLETE WITH EXCEPTIONS — 89 text files inspected, 36 Python files syntax-checked, 11 workflow YAML files syntax-checked; two PDFs require manual review; six provider error bodies excluded from market data; see `P443_P444_ACTIVE_10_TASK_BATCH_READBACK_2026-11-27.md` | Parse logs and explicit unsupported reasons |
| 15 | Reconcile strict-vs-global JSON counting units and lock report terminology | RECONCILED | Keep CSV rows + JSON documents distinct from CSV rows + JSON entries |
| 16 | Reconcile exact duplicate rows and business-key duplicates across OHLCV/floorsheets/calendars | COMPLETE FOR PINNED 928-FILE AUDIT — Run #336 passed all 59 workflow steps; both artifacts independently SHA-256 matched GitHub metadata. Global report: 0 OHLCV duplicate symbol/date keys, 0 OHLCV exact duplicate rows, 0 floorsheet explicit record-ID repeats, 0 exact repeated floorsheet rows, and 0 duplicate calendar dates. Files without explicit source IDs are unsupported for record-ID duplicate checks; no composite fallback is used | Completion is limited to pinned inventory and implemented checks; 150 unsupported file/check combinations remain disclosed; no synthetic row identity or global uniqueness inference |
| 17 | Classify repeated adjacent OHLCV tuples across the complete 462-symbol finding set | COMPLETE FOR CLASSIFICATION — Run #336 strict artifact read-back confirms 94,543/94,543 pairs classified: 26,544 historical-holiday candidates; 9,027 recorded-closure pairs; 73 both-open/unverified; 58,899 insufficient-session-evidence. Review queues: 35,571 quarantine-review and 58,972 independent-evidence. Zero corrections/promotions | Classification is complete; source-level adjudication, full lineage and any correction remain separate open work; never blanket-delete repeated candles |
| 18 | Complete full-scope row-level date-lineage scan across all 525 OHLCV files | PARTIAL — Run #336 artifact cross-check: 94,543 repeat-pair symbol/date keys across 462 symbols; lineage file has 68,783 unique keys across 253 symbols, but only 47,665 intersect the repeat-pair set. Thus 46,878 repeat-pair keys are not covered; 209 symbols have zero coverage, 245 have partial coverage, and only 8 are fully covered. 21,118 lineage keys fall outside the repeat-pair set | Full 525-file/date-lineage scan still requires effective-dated IDs, verified session calendar and official date-key evidence; no date-shift inference |
| 19 | Reconcile March 1/2 archive lineage and 13 baseline-conflict rows | UNRESOLVED — 2026-03-01 partition has 13 symbols/30 transactions vs 2026-03-02 candidate 341 symbols/55,206 transactions; independent 2026-03-01 summary supports date-shift hypothesis but no exchange-origin complete total; see batch read-back | Authoritative session date and complete transaction totals |
| 20 | Verify floor-sheet contract identity uniqueness with session/source scoping | PARTIAL — selected 22-session comparison found no duplicate contract numbers within those session files (21 exact parity, 1 row conflict); P4.33 archives show contract_no reuse but unique source/session record IDs; use source+revision/blob+date+record ID as row key; see batch read-back | Contract identity scope must not be assumed global |
| 21 | Add P4.44 lifecycle-symbol/date hold source to scanner staging and publication gates | IMPLEMENTED — predecessor-symbol holds tested; current successor codes MATRI/694, SMPDA/2896 and GBLBS/583 are not in the 26-symbol predecessor hold set; see `P444_MERGER_SUCCESSOR_CURRENT_ID_CROSSWALK_2026-11-27.csv` | Symbol-wide fail-closed holds remain on predecessor history only; successor current-security lookup remains available |
| 22 | Add regression tests for lifecycle holds, unknown symbols, date boundaries and bypass paths | PARTIAL COMPLETE — combined unittest step passed | Tests cover 26-symbol scope, missing/incomplete ledger, unknown symbols, OHLCV, floorsheet and broker-summary paths; end-to-end workflow still fails at private Drive credential verification |
| 23 | Validate atomic publication, no-overwrite behavior and raw archive immutability | COMPLETE — publication regression suite passed in run #14 | Exclusive publish, identical rerun, differing-content no-overwrite, destination/parent symlink rejection, evidence digest failure, duplicate contract and unchanged target bytes all covered |
| 24 | Re-run complete P4.43 workflow on the final branch head after implementation | NOT RUN ON CURRENT HEAD | Successful run must identify exact head SHA and artifacts |
| 25 | Reconcile final audit outputs and PR #80 acceptance checklist | OPEN | No merge until all issue acceptance criteria and review evidence are satisfied |

## Other open evidence work

| # | Work package | Status | Acceptance / dependency |
|---:|---|---|---|
| 26 | P4.23: preserve and reconcile all 87 same-date conflict keys, including RHGCL | PARTIAL — RHGCL 2026-11-19 is now PRIMARY_CONFIRMED for full OHLCV (security ID 8108; raw response SHA-256 `303d92756ffbcaa2e6ab5020c29e1eab1b63ed99797bf024914dbb863cbae183`; derived view uses official Close 258.00 / Volume 9,054; raw SMC row preserved); 86 keys on 2025-07-28 remain unresolved | Key-complete matrix and source-specific field dispositions |
| 27 | P4.23: acquire and completeness-validate 2025-07-28 floorsheet evidence for 86 conflict keys | BLOCKED | Complete primary-origin capture, pagination proof and per-symbol totals |
| 28 | P4.23.2: reconstruct 2025-07-28 Open/Close for 86 symbols without assuming contract-ID order | BLOCKED | Timestamped primary records or independently validated ordering semantics |
| 29 | P4.35: independently classify lineage and coverage for 1,368 historical OHLCV flags | BLOCKED | Independent historical source or exact acquisition blocker by candidate |
| 30 | Issue #4: extend official session-calendar and instrument evidence across the full historical period | PARTIAL — 2026 closure capture and validators exist; full verified-open history absent | Raw exchange captures, source hashes, effective-dated instrument master and tests |

## Execution order and guardrails

1. Continue #1–#12 first because identity and per-security execution evidence are dependencies for the unresolved P4.44 repeated-pair matrix. #8 now has fail-closed schema/provenance validation; #9 sequence audit remains review-only.
2. In parallel, implement #21–#23 only after reviewing the existing scanner gate and test conventions; preserve a fail-closed default and avoid weakening existing overlay checks.
3. Continue #18–#20 only when primary session and contract evidence is available.
4. Treat #26–#30 as independent queues; do not import secondary mirrors as independent primary evidence.
5. Keep all existing HOLD/UNKNOWN dispositions, raw source blobs, finalized OHLCV, and canonical data unchanged until the relevant acceptance criteria are independently met.

## Current checkpoint

- P4.44 lifecycle ledger: 26 rows, all `HOLD_UNKNOWN`; zero verified historical stable IDs.
- P4.44 repeated-pair matrix: 23,377 rows; all `HOLD_UNKNOWN_NO_INFERENCE`; zero promotions.
- Session recovery: 149 rows, 148 candidate-total matches and one baseline conflict; all publication disallowed.
- March 1/2: alternative date remains a candidate only; official transaction total not verified.
- Canonical publication and scanner staging now load the 26-symbol P4.44 lifecycle ledger as symbol-wide wildcard holds. Regression coverage passed in publication-gate run #13; the overall workflow remains failed closed at the private Drive credential check. The 23,377-pair matrix remains an evidence/review artifact, not a promotion input.
- Latest successful full global audit run is #316 (`46009773312`) on intermediate SHA `4653263c575dee39243ccfb6e07d15b2d87ad0a3`; all 53 steps passed. Both artifacts were downloaded and their local SHA-256 values matched GitHub: strict `77dc65bff7ac0099f89b3c63383faf10e0b54d74e08d9bd88fe7e40fcb6206d3`, global `cb38c4e08bf0a36b0008a72f1e7b45e5c6e6b22cf998169361378020617c5f23`. The current branch head is newer (`9798cdf990fdc6f8eb0ea070d17876d2456b68c6`); run #316 is not current-head validation.

**No raw OHLCV, floorsheet, canonical, date, security identity or scanner input rows were changed by this queue creation.**


## 2026-11-27 continuation checkpoint

- Added `tools/p444_audit_lifecycle_sequences.py` and `test_p444_audit_lifecycle_sequences.py`.
- The audit validates required schema columns and emits review findings for missing event dates, missing merger successors, duplicate event dates, terminal events preceding later trading events, and resumptions without a prior suspension candidate.
- The audit is read-only: it reports zero mutations, zero promotions and zero disposition changes. Review findings do not establish that a source record is wrong; they require evidence review.
- Added the new test module to `.github/workflows/p443-publication-gate.yml`. Workflow result has not yet been verified; do not count the tests as passed until a run is observed.
- No lifecycle register, raw source, OHLCV, floorsheet, canonical or scanner-input data rows were changed.
- Run #18 tested code commit: `7ff62a8eb922196f63f805335148fdc4fe311fda`. Queue/documentation head has advanced separately; no new full workflow has tested the final documentation-only head.


## Run #317 current-head audit read-back — 2026-11-27

- Full P4.43 workflow Run #317 completed successfully (53/53 steps) on exact tested SHA `ad4eca1c0892ec6c1e55e0a264fc87988dce86aa`: https://github.com/jaljala044/nepse-smc-data/actions/runs/46010696573
- Both artifacts were downloaded and independently SHA-256 checked against GitHub Actions metadata:
  - Global artifact ID 15203502332: `eaea2fa735031755dc2c1fecda0a396987933bbdc597127f99a64cf2c2ebef71` — MATCH.
  - Strict artifact ID 15202733267: `1873b11145aaa55c18d0539bc108c35dd8942e21eeaa241460e136feaa0f2b61` — MATCH.
- Strict read-back: 928 files; 784 parsed; 89 text-inspected; 36 code-syntax-checked; 11 workflow-syntax-checked; 2 manual document reviews; 6 non-JSON responses. Strict parsed records 1,668,641; 94,543 repeated-adjacent tuples; 1,331 invalid-OHLCV flags; 10 exact repeated JSON records. Findings overlap and are not unique affected-row counts.
- Global report separately reports 1,650,883 CSV rows plus JSON documents; this is a different JSON counting unit from strict parsed record elements. It reports 95,356 repeated tuples across rows, of which 94,543 are consecutive identical tuples. These are separate, overlapping definitions.
- P4.44 matrix read-back: 23,377 rows / 209 symbols / 23,377 unique pair IDs; zero read-back issues. Identity: 21,082 current-snapshot-only and 2,295 unresolved; historical stable IDs verified: 0. Current/previous market-closed evidence: 1,503 / 979; current/previous session unknown: 21,874 / 22,398. All rows remain `HOLD_UNKNOWN_NO_INFERENCE`; promotion false; canonical_data_modified=false.
- Floorsheet coverage remains limited: 22 primary-indexed dates / 5,235 requests; 3,177 H/L/volume matches and 2,058 conflicts, with Open/Close unverified. HF-only archive inventory identifies 74 secondary-only dates / 15,439 requests; 48,099 requests have no indexed source. Third-party source lineage and full-session completeness remain unverified. No rows promoted.
- 2024-08-01 diagnostic: 72,500 arithmetic-failing rows have whole-rupee stored rates; implied-rate proximity is a hypothesis only. Four half-rupee cases do not follow half-up; no amount/rate reconstruction authorized.
- No raw/canonical market rows were changed, shifted, deduplicated, corrected or promoted.

### Subsequent lifecycle-sequence audit work

- Work #9 now has `tools/p444_audit_lifecycle_sequences.py` and regression tests. The audit is read-only and emits review flags only; it does not infer dates or release holds.
- Publication-gate Run #18 (ID 46031200729) on SHA `7ff62a8eb922196f63f805335148fdc4fe311fda` passed the combined regression suite, including the lifecycle-sequence tests, and Python compilation. It failed closed only at actual private Drive retrieval because `GDRIVE_SERVICE_ACCOUNT_JSON` is unavailable; no private overlay was retrieved or promoted. https://github.com/jaljala044/nepse-smc-data/actions/runs/46031200729
- The current branch/PR head at this queue update is `5395cb0d2727319375302d2fd67ac8d2c281653c`, a documentation follow-up after the lifecycle-test fixture correction. Run #317 predates these lifecycle-sequence changes; Run #18 tests the preceding code head. A new full P4.43 audit is still required for the latest branch head.
- Work #9 status: IMPLEMENTED; regression tests passed in Run #18; actual lifecycle-ledger sequence scan is not yet an executed CI acceptance result. Work #24: Run #317 passed on its exact head, but the newer branch head still needs full-audit validation.
- PR #80 remains open/draft/unmerged; issue #82 remains open. All unresolved lifecycle and repeat-pair dispositions remain held.


### P4.44 lifecycle-ledger validator continuation

- Strengthened `tools/p444_validate_lifecycle_evidence.py`: now rejects missing/duplicate required columns; validates source tiers and confidence vocabulary; requires dates for populated event types; checks merger successors; requires primary provenance, security ID and source statement for any `verified` event; validates SHA character sets; and detects duplicate/conflicting event records and impossible terminal/resumption sequences.
- Replaced/expanded `test_p444_validate_lifecycle_evidence.py` with seven focused regression tests covering schema, event dates/types, source tier, confidence, verified provenance, successor, duplicate and conflict behavior.
- Added validator tests and compile checks to the publication-gate workflow. Run #19 (`46031522183`) passed the full combined unittest step and Python compilation. Overall workflow failed at the separate private Drive overlay retrieval step because the credential secret is unavailable; no private overlay was retrieved.
- Existing 26-row evidence ledger is unchanged. Existing `HOLD_UNKNOWN` dispositions remain intact; this change is validator/test/workflow code only.
- Current branch head after the validator implementation and queue update is recorded by this documentation commit; run #19 validates the code commit `85ef6c86e0562d0c38cf9c6ae8beee8317f29635`, before the final queue-only update.


### Work package #10 — 281-capture inventory and three-symbol payload audit

- Inspected companion repository `jaljala044/nepse-elite-ai-scanner-pro`, branch `main`, exact tree commit `889f28be685385e27b2fc5350d5a744a32880c80`.
- Found exactly 281 per-security raw response payloads under `data/evidence/raw/nepse/security-history/2026-10-05_to_2026-11-26/symbols/`, one for each of 281 unique symbols; aggregate Git tree byte size is 1,477,676.
- Parsed the capture `SHA256SUMS` manifest: 281 symbol-response entries, 281 unique symbols, zero duplicate entries, zero missing manifest entries and zero extra manifest entries. Manifest Git blob SHA: `40c2d4d6b482c0aacf0f6cb0baf8083e0b3d37`.
- Independently fetched and JSON-parsed NESDO, ULBSL and YMHL payloads: 29 rows each, date coverage 2026-10-05 through 2026-11-26. Each contains `businessDate`, `totalTrades`, `totalTradedQuantity`, `totalTradedValue`, `highPrice`, `lowPrice`, and `closePrice`; none contains Open.
- All three payload SHA-256 values match their manifest entries and the existing parity report; Git blob SHAs and byte sizes are preserved in the companion report `reference/P444_281_SECURITY_HISTORY_CAPTURE_AUDIT_2026-11-27.md`.
- Scope limit: this pass verified the 281-file inventory against the manifest and parsed only the three symbols already selected for parity analysis. It did not parse/validate all 281 JSON payload schemas or establish historical security-ID continuity. Current security IDs remain point-in-time labels only.
- No source payloads, OHLCV, lifecycle dispositions, canonical rows or scanner inputs were modified. No promotion or date adjudication was authorized.


### Run #324 — work package #10 full payload audit and P4.43 revalidation

- Workflow Run #324 completed successfully (55/55 steps) on exact tested SHA `ebf0f59732da0b5c8f8b9244f77a706868712f00`: https://github.com/jaljala044/nepse-smc-data/actions/runs/46033103956
- Strict artifact ID 15214839272 downloaded; local ZIP SHA-256 matched GitHub artifact digest: `afed913e7c2c45f98f90633f5c6c4a07ed2a54dfb6fb08a23c668fedab5aab98`.
- Work package #10 audit JSON: 281 symbols, 281 payload files, 281 manifest entries, 8,142 total rows, all 281 SHA-256 entries match, zero row-level issues, audit valid=true. Date range 2026-10-05 through 2026-11-26. All 281 payloads lack Open; no Open was synthesized. `promotion_allowed=false`; `canonical_data_modified=false`.
- The capture is point-in-time history and does not prove exchange completeness or historical security-ID continuity. Missing dates were not inferred to be non-trading days.
- The same run read-back validated the 23,377-row / 209-symbol repeat-pair matrix: 23,377 unique pair IDs, zero read-back issues, all rows held and promotion disabled.
- Work package #11 remains BLOCKED: 0/23,377 previous and current endpoint rows have per-security execution evidence populated; historical stable IDs remain 0/23,377. The 281-payload capture covers only 2026-10-05 to 2026-11-26 and does not supply historical ID continuity.
- Work package #12 remains PARTIAL; matrix structure/read-back is validated, but execution fields and historical IDs remain empty.
- Run #324 strict inventory summary: 928 files; 784 parsed, 89 text-inspected, 36 code-syntax-checked, 11 workflow-syntax-checked, 2 manual document reviews and 6 non-JSON responses. Unsupported/semantic coverage work remains under #14.
- Run #324 tested an earlier code head than the current branch documentation head. It is not represented as validation of any later commit.
- No raw source, OHLCV, floorsheet, lifecycle disposition, canonical row or scanner input was modified; no promotion or hold release occurred.


### Run #334 — matrix JSON artifact read-back corrected and verified

- Run #334 completed successfully on tested SHA `48492befc3da6581cbba8e0a9609769774cc3505`: https://github.com/jaljala044/nepse-smc-data/actions/runs/46041575399
- Strict artifact ID `15221155794`; ZIP SHA-256 `30d6e1a395268228d49f4679485f10d4d87c30ee2ad0e880fc8606165d5c4236`, matching GitHub artifact metadata.
- `P444_UNCOVERED_REPEAT_PAIR_EVIDENCE_READBACK_AUDIT_2026-11-27.json` parses successfully and ends with a real newline. It reports 23,377 rows, 209 symbols, 23,377 unique pair IDs, date range 2024-03-05 through 2026-11-20, `issues=[]`, `valid=true`, `promotion_allowed=false`, and `canonical_data_modified=false`.
- All 23,377 previous and current execution-evidence bundles remain absent. Historical stable IDs remain absent; identity counts remain 21,082 current-snapshot-only and 2,295 unresolved. Session evidence remains incomplete (current: 1,503 closed / 21,874 unknown; previous: 979 closed / 22,398 unknown).
- Exact-symbol endpoint coverage remains 0/46,754 occurrences covered and 0 pairs with both endpoints covered. Only NESDO, ULBSL and YMHL overlap the 281-symbol capture, and none of their endpoint dates fall within its window.
- Work package #12 is COMPLETE for matrix structure, schema validation and reproducible artifact read-back only. Work package #11 remains BLOCKED; no historical execution evidence or stable IDs were created, and this does not authorize any disposition change or promotion.
- Run #334 tested the code commit above; the current branch head at this documentation update is later. No raw/canonical rows were changed.

### Work package #11 — exact-symbol endpoint coverage audit added

- Added `tools/p444_audit_repeat_pair_capture_coverage.py` and `test_p444_audit_repeat_pair_capture_coverage.py`.
- The audit compares exact symbol names and actual payload business dates only; it does not infer predecessor/successor aliases or ticker similarity.
- Independent matrix/capture comparison: 209 repeat-matrix symbols; exact overlap is NESDO, ULBSL and YMHL only. Those symbols contribute 640 pair rows, but zero of their endpoint dates fall within the pinned capture window 2026-10-05 to 2026-11-26. Therefore this capture provides zero endpoint execution records for those pairs.
- Run #325 on exact SHA `aae6050f9b366125a00aebf5b4c4d65e4ac3e553`: the new regression-test step (#37), exact-symbol endpoint coverage audit step (#38), matrix read-back tests (#39) and matrix read-back audit (#40) all completed successfully. Full workflow was still in progress at the time of this queue update; the output artifact has not yet been independently downloaded/read back.
- This confirms the 281-capture cannot fill the historical repeated-pair execution gap. Work package #11 remains BLOCKED. All rows remain held; no promotion or canonical change.
- Work packages #12–#20 remain at their existing evidence-based statuses. See `P443_P444_ACTIVE_10_TASK_BATCH_READBACK_2026-11-27.md` for the #13–#20 detailed read-back.


### Run #334 — global audit artifact read-back and business-key summary

- Global artifact ID `15221430564`; downloaded ZIP SHA-256 `e5d605d8e7abd71a5650f3b1a33e3b5d2cb3d8266679b8dfd59b7041194f2e11`, matching GitHub artifact metadata.
- Report confirms 928 inventory files, 1,650,883 CSV rows plus parsed JSON documents, 691 parsed CSV files, 93 parsed JSON documents, zero parse errors and 189,899 findings.
- Corrected floorsheet metrics are now emitted with accurate semantics: 0 record-ID repeats within source file/session and 0 exact repeated floorsheet rows. Contract-number reuse is not treated as a duplicate key.
- OHLCV summary remains 95,356 repeated tuples across rows and 94,543 consecutive identical tuples; these are findings for review, not automatic corrections. No raw/canonical data was modified.
- This run tested code SHA `48492befc3da6581cbba8e0a9609769774cc3505`; documentation commits followed it. It does not constitute a full audit of the later documentation-only branch head.


### Floorsheet row-identity guard refinement — Run #336

- Reviewed `tools/audit_global_data_integrity.py` and found that when an explicit transaction ID was absent, a composite of contract number, symbol, buyer and seller was used as a substitute key. That is not a source-issued record ID and can conflate legitimate repeated business attributes.
- Removed the composite fallback. The duplicate-record-ID check now runs only when an explicit source record/transaction ID column exists; otherwise the file increments `unsupported` for this check. Exact full-row repeats continue to be evaluated independently.
- Added regression test `test_composite_contract_fields_are_not_treated_as_record_id` with same contract/symbol/brokers but differing quantities. It expects no duplicate-ID or exact-row finding and one unsupported check.
- Run #336 (`46043405148`) on SHA `c261b1c0e3c64cd1268a92eaaf0690cb028a738d`: the `Verify global floorsheet business-key scope tests` step passed. Full workflow and artifact read-back were still running at this checkpoint.
- No source rows or canonical data changed. No record was deduplicated, corrected or promoted.


### Run #336 — refreshed full audit and artifact read-back

- Run #336 completed successfully on tested code SHA `c261b1c0e3c64cd1268a92eaaf0690cb028a738d`; all 59 workflow steps passed. The branch/PR head subsequently advanced to documentation-only SHA `b8812f29090e08140efc33b533772aa60befc50f`.
- Global artifact ID `15221652252`, ZIP SHA-256 `5dd8dd7ce89e538510745c28683058d2140b7fc9e50d65387c450b7606898248`, matches GitHub metadata. Strict artifact ID `15221597345`, ZIP SHA-256 `1242b5abcd38f7a37f7f819b44992b8d202d2075d7b9f1a57f949138a1b30d01`, also matches.
- The explicit floorsheet record-ID semantics regression passed. No composite contract/symbol/broker fallback is counted as a record ID. The global report records 928 files, 1,650,883 CSV rows plus parsed JSON documents, 691 parsed CSV files, 93 parsed JSON documents, zero parse errors and 150 unsupported file/check combinations.
- Global duplicate results: zero OHLCV duplicate symbol/date keys, zero OHLCV exact duplicate rows, zero floorsheet record-ID repeats within source file/session, zero exact repeated floorsheet rows and zero duplicate dates within calendar files. Unsupported checks remain disclosed; these zeroes are not a claim of universal uniqueness beyond the pinned checks.
- The strict artifact reconfirms 94,543 repeated adjacent OHLCV pairs and their four-way classification; zero rows were corrected or promoted. Work #17 is complete for classification only.
- Recomputed #18 coverage from `repeat_calendar_triage.csv` and `equity_security_date_source_lineage.csv`: 94,543 unique repeat-pair symbol/date keys across 462 symbols; 68,783 unique lineage keys across 253 symbols; 47,665 keys intersect; 46,878 repeat-pair keys are absent from lineage; 209 symbols have no lineage coverage, 245 partial coverage, and 8 full coverage. Of the 68,783 lineage keys, 21,118 are outside the repeat-pair set. This is a coverage-gap measurement, not proof of missing trading or a date shift.
- No raw OHLCV, floorsheet, calendar, canonical or scanner-input rows were modified. No correction, promotion or hold release occurred.
