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
| 3 | Establish effective-dated symbol/name/ID mappings for all 209 repeated-pair symbols | PARTIAL — 183 current-snapshot-only matches; 26 unresolved; 0 historical stable IDs; see `P444_209_SYMBOL_CURRENT_SNAPSHOT_RECONCILIATION_2026-11-27.md` | No ticker-similarity inference; explicit unmatched set |
| 4 | Resolve the 26 residual symbols against archived NEPSE security lists | PARTIAL — evidence coverage reconciled 26/26; historical IDs/effective dates verified 0/26; no historical archive recovered; see `P444_26_RESIDUAL_ARCHIVE_CROSSCHECK_2026-11-27.md` | Historical IDs or explicit unresolved reason per symbol |
| 5 | Reconcile JALPA/KLBSL → MATRI merger dates and distinguish integrated-business date from last trade | PARTIAL | Primary raw notice plus exchange trading boundary |
| 6 | Resolve SABSL/SDLBSL → SMPDA conflicting 2024-07-14 vs 2025-07-14 claims | BLOCKED | Date-authentic primary notice and effective-date interpretation |
| 7 | Recover cancellation notices and raw payload provenance for NICAD8283, NICGF and SBLD2082 | PARTIAL | Original PDFs, SHA-256 and unambiguous Bikram Sambat/Gregorian date conversion |
| 8 | Complete lifecycle event ledger schema validation (event types, dates, source tier, confidence, ID, successor) | IMPLEMENTED — seven validator regression tests passed in publication-gate run #19; overall workflow failed at private Drive verification | Requires all 15 ledger columns; validates event/date/tier/confidence, verified ID/provenance, successor and duplicate/conflict checks; no promotion |
| 9 | Audit effective-date interval overlaps and impossible lifecycle sequences | IMPLEMENTED — regression tests and compile passed in run #18; overall workflow failed at private Drive verification | Review-only findings; no dates inferred and no holds released |
| 10 | Parse and verify the existing 281 per-security NEPSE history captures without treating current IDs as historical IDs | PARTIAL — exact 281/281 raw-file ↔ SHA256SUMS inventory parity verified; 3/281 payloads parsed and field-audited in this pass | Raw response hashes, field coverage and explicit current-snapshot limitation |
| 11 | Build exact per-security execution evidence for every repeated-pair endpoint date | BLOCKED | Security identity plus date-matched execution payload; market totals are insufficient |
| 12 | Expand the 23,377-pair matrix with source row identity, stable-ID confidence, session evidence and per-security evidence | PENDING | All rows retained; no inferred promotions |

## P4.43 — global integrity and canonical quarantine

| # | Work package | Status | Acceptance / dependency |
|---:|---|---|---|
| 13 | Revalidate 928-file inventory and pinned blob/byte metadata | INVENTORY STAGE COMPLETE; content scope still open | Reproducible pinned inventory; disclose unsupported files |
| 14 | Complete content parsing for the 138 inventory-only/unsupported files where formats permit | PENDING | Parse logs and explicit unsupported reasons |
| 15 | Reconcile strict-vs-global JSON counting units and lock report terminology | RECONCILED | Keep CSV rows + JSON documents distinct from CSV rows + JSON entries |
| 16 | Reconcile exact duplicate rows and business-key duplicates across OHLCV/floorsheets/calendars | PENDING FULL-SCOPE | Separate duplicate rows, duplicate keys and legitimate repeated values |
| 17 | Classify repeated adjacent OHLCV tuples across the complete 462-symbol finding set | PARTIAL — 23,377 uncovered pair matrix held | Per-pair evidence; never blanket-delete repeated candles |
| 18 | Complete full-scope row-level date-lineage scan across all 525 OHLCV files | BLOCKED | Effective-dated IDs, verified session calendar and official date-key evidence |
| 19 | Reconcile March 1/2 archive lineage and 13 baseline-conflict rows | UNRESOLVED | Authoritative session date and complete transaction totals |
| 20 | Verify floor-sheet contract identity uniqueness with session/source scoping | PENDING | Contract identity scope must not be assumed global |
| 21 | Add P4.44 lifecycle-symbol/date hold source to scanner staging and publication gates | IMPLEMENTED — code tested at `ccc1bd911e29c84a448dd05cd4bd0b782bb8d9b6` | Symbol-wide fail-closed holds wired into canonical publication and scanner staging; all 26 symbols remain held |
| 22 | Add regression tests for lifecycle holds, unknown symbols, date boundaries and bypass paths | PARTIAL COMPLETE — combined unittest step passed | Tests cover 26-symbol scope, missing/incomplete ledger, unknown symbols, OHLCV, floorsheet and broker-summary paths; end-to-end workflow still fails at private Drive credential verification |
| 23 | Validate atomic publication, no-overwrite behavior and raw archive immutability | COMPLETE — publication regression suite passed in run #14 | Exclusive publish, identical rerun, differing-content no-overwrite, destination/parent symlink rejection, evidence digest failure, duplicate contract and unchanged target bytes all covered |
| 24 | Re-run complete P4.43 workflow on the final branch head after implementation | NOT RUN ON CURRENT HEAD | Successful run must identify exact head SHA and artifacts |
| 25 | Reconcile final audit outputs and PR #80 acceptance checklist | OPEN | No merge until all issue acceptance criteria and review evidence are satisfied |

## Other open evidence work

| # | Work package | Status | Acceptance / dependency |
|---:|---|---|---|
| 26 | P4.23: preserve and reconcile all 87 same-date conflict keys, including partial RHGCL primary HLCV evidence | PARTIAL — 87 retained; 86 2025-07-28 unresolved; RHGCL Open absent | Key-complete matrix and source-specific field dispositions |
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
