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
| 2 | Recover the official all-instrument security master with instrument class, stable ID, symbol and status | BLOCKED | Exchange-issued raw response and provenance |
| 3 | Establish effective-dated symbol/name/ID mappings for all 209 repeated-pair symbols | BLOCKED | No ticker-similarity inference; explicit unmatched set |
| 4 | Resolve the 26 residual symbols against archived NEPSE security lists | BLOCKED | Historical IDs or explicit unresolved reason per symbol |
| 5 | Reconcile JALPA/KLBSL → MATRI merger dates and distinguish integrated-business date from last trade | PARTIAL | Primary raw notice plus exchange trading boundary |
| 6 | Resolve SABSL/SDLBSL → SMPDA conflicting 2024-07-14 vs 2025-07-14 claims | BLOCKED | Date-authentic primary notice and effective-date interpretation |
| 7 | Recover cancellation notices and raw payload provenance for NICAD8283, NICGF and SBLD2082 | PARTIAL | Original PDFs, SHA-256 and unambiguous Bikram Sambat/Gregorian date conversion |
| 8 | Complete lifecycle event ledger schema validation (event types, dates, source tier, confidence, ID, successor) | PARTIAL — validator and regression tests exist; full interval-overlap / impossible-sequence coverage remains open | Current tests reject malformed dates/events, incomplete verified provenance, duplicate event records and same-date source conflicts |
| 9 | Audit effective-date interval overlaps and impossible lifecycle sequences | IMPLEMENTED — non-mutating audit script and regression tests added; CI result pending | Review-only findings; no dates inferred and no holds released |
| 10 | Parse and verify the existing 281 per-security NEPSE history captures without treating current IDs as historical IDs | PARTIAL EXISTING EVIDENCE | Raw response hashes, field coverage and explicit current-snapshot limitation |
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

1. Continue #1–#12 first because identity and per-security execution evidence are dependencies for the unresolved P4.44 repeated-pair matrix. #9 now has a non-mutating audit tool; next validate its CI result and address any flagged sequence conflicts.
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
- Current branch head at this checkpoint: `e4cd0f0cfebce5cf66cd6dafa54290b794997816`.
