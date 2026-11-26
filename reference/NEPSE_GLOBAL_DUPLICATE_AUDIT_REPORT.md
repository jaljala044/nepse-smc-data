# P4.43 global duplicate and data-integrity audit

**Status: reproducible audit baseline complete; adjudication and canonical-ingestion acceptance remain open.**

**Pinned input:** `main` at `56362fb4f65b91fdcca8f50b50e53ad80e703649`.  
**Latest validated workflow:** [Run 141](https://github.com/jaljala044/nepse-smc-data/actions/runs/45895851920), head `b8e48c1d936f984caf0b50f2efec9dcdd28fcf19`.  
**Method:** deterministic, read-only scan of pinned file blobs. Findings are review flags, not automatic corrections.

## Coverage

- Files inventoried: **928**
- Structured files parsed: **784**
- Inventory-only/unsupported: **138** (88 Markdown, 36 Python, 11 workflow YAML, 2 PDF, 1 text)
- Non-JSON provider responses: **6**
- Parseable records: **1,668,641**
- Pinned-byte verification and regression tests: **passed**
- File failures: **0**

The six non-JSON responses are two unauthorized HTML responses from the P4.34 probe and four `Searched Date is not valid.` responses from P4.37 historical EOD probes. They are not counted as parsed market data.

## Strict content findings

| Finding class | Count | Disposition |
|---|---:|---|
| Repeated adjacent OHLCV tuples | 94,543 | UNRESOLVED; not presumed duplicate trades |
| Invalid OHLCV invariants | 1,331 | 1,329 exact matches to historical exception registers; 2 unmatched review rows |
| Trade-shaped floorsheet records with missing session date | 0 | No remaining flags after transaction-shape gating |
| Missing trade identity after transaction-row gating | 0 | Prior metadata/summary false positives excluded |
| Exact repeated JSON records | 10 | Summary-object repeats in two P4.37 capture reports; not duplicate trade rows |

Finding classes overlap and must not be summed as unique affected rows.

### OHLCV exception-register reconciliation

The strict workflow joined all 1,331 invalid-OHLCV rows to the existing historical exception registers:
- **1,329** matched an existing exception register exactly.
- **2** remain unmatched and require review:
  - KDBY, 2026-04-29, source row 854, blob `21764adf5c5a030dbdd5ca570225a07e2f4c41f7`.
  - KEF, 2026-04-28, source row 1160, blob `e0039a5b74f53c84e5ce48047b3bbd8e3b9e02f3`.

An exception-register match is reconciliation, **not independent validation**. The prior P4.35 source-lineage audit found no qualified independent historical source; the affected OHLCV rows remain UNKNOWN. No values were repaired or promoted.

### Floorsheet row classification and contract-number reuse

The strict parser now requires transaction-shaped fields before classifying a record as a trade, including a symbol plus buyer/seller and quantity/rate evidence or equivalent contract-shaped fields. It excludes generic security-master IDs and market-status IDs. The earlier 2,687 broad missing-session flags were parser false positives; after transaction-shape gating, **zero** trade-shaped records remain flagged for missing session dates. The 364 prior missing-identity flags were likewise non-transaction metadata/summary rows.

The two quarantined P4.33 historical floorsheet files contain **544,937** trade rows in total. Within each file/session, the strict scan reports:

| Source file | Trade rows | Distinct contract-number values | Values reused | Repeated occurrences (beyond first) | Values appearing across symbols |
|---|---:|---:|---:|---:|---:|
| 2024-08-14 | 244,019 | 24,404 | 24,404 | 219,615 | 22,329 |
| 2024-08-18 | 300,918 | 30,093 | 30,093 | 270,825 | 27,893 |

These are **contract-number field collisions**, not confirmed duplicate exchange contract IDs. The P4.33 capture report states that all 544,937 archive-local source record IDs are unique and that zero exact repeated rows were found. Do not infer a duplicate trade, invent identifiers, or assume a contract number is globally unique across securities. Both source files remain `BLOCK_CANONICAL` pending explanation of the identifier precision/collision pattern.

### Repeated JSON summary records

The ten exact-repeat flags occur in the `sector_rollup` objects of two preserved P4.37 capture reports (five repeated rollup objects in each report). These are summary-statistic repeats, not repeated floorsheet trades. The reports intentionally preserve separate evidence copies; no deletion is warranted.

## Repeated-tuple calendar triage and date-lineage evidence

The latest strict workflow cross-checked all 94,543 repeated adjacent tuples against the pinned calendar evidence and produced a row-level triage artifact:

| Triage disposition | Count | Meaning |
|---|---:|---|
| SESSION_UNKNOWN | 88,208 | No matching verified session status in the pinned calendar evidence |
| CLOSED_SESSION_CANDIDATE | 6,232 | Current row date matches pinned closed-session evidence; candidate only |
| OPEN_SESSION_TUPLE_UNVERIFIED | 103 | Current row date has open-session evidence, but the repeated tuple itself is not independently validated |

The pair-level classifier now verifies both pinned source rows and exact OHLCV tuple equality, checks calendar evidence for both the current and previous dates, and exports disjoint review queues:

| Pair disposition | Count | Review queue |
|---|---:|---|
| PAIR_CONTAINS_HISTORICAL_LISTED_HOLIDAY | 26,544 | Review pair for quarantine |
| PAIR_CONTAINS_RECORDED_CLOSURE | 9,027 | Review pair for quarantine |
| BOTH_OPEN_TUPLE_UNVERIFIED | 73 | Require independent security/date evidence |
| INSUFFICIENT_SESSION_EVIDENCE | 58,899 | Require independent security/date evidence |

The two review queues contain **35,571** pair candidates for quarantine review and **58,972** pairs requiring independent security/date evidence. Every row has `promotion_allowed=false`; the workflow reports zero corrected rows and zero promoted rows. A historical listed-holiday entry is a candidate, not proof of universal closure. An open market session does not establish a security-specific execution. Pair classification is not an instruction to delete either source row.

Full row-level pair dispositions and the two disjoint review queues are retained in the workflow artifact: `repeat_calendar_triage.csv`, `repeat_quarantine_candidates.csv`, and `repeat_evidence_review.csv`.

Two additional read-only row-hold exports narrow the pair queues to unique source rows:
- Recorded verified-closure evidence: 9,027 pairs resolve to **6,232 unique source rows**, across 20 dates and 379 symbols. The hold is `EXCLUDE_RECORDED_CLOSURE_PENDING_INDEPENDENT_ADJUDICATION`; no replacement is allowed.
- Authenticated API holiday-list corroboration: all 26,544 historical-listed-holiday pairs were corroborated by the pinned API holiday evidence, producing **22,244 unique candidate rows** across 77 dates. This is corroboration of the listing only, not independent proof of universal closure or individual-security execution.
- The two unique-row sets are disjoint: **28,476 candidate rows total** (6,232 recorded-closure rows + 22,244 API-holiday rows). These remain hold candidates, not applied exclusions or corrected data. No replacements occurred.

P4.37 independently identified 1,455 canonical-only rows across 24 sampled symbols that match official HLCV tuples on 81 verified closed dates. P4.42 traced the NMLBBL/SMPDA date-label pattern to ShareSansar scrape-date filenames. These source-backed findings are useful context, but they do not establish a cause for every repeated pair across the full historical universe.

Historical session evidence remains incomplete outside the captured one-year official EOD window. Do not infer an open session from weekdays or absence from a closure list. Do not label repeated tuples as NO_TRADE or as erroneous solely because values repeat.

## Quarantine and safeguards

The two 2024 SMPDA floorsheet archives remain `BLOCK_CANONICAL`:
- `reference/p433_floorsheets/floorsheet_2024-08-14.csv.gz` — blob `0dd938bc5e6bfd50fa09bf85f0836d443ab15983`.
- `reference/p433_floorsheets/floorsheet_2024-08-18.csv.gz` — blob `49d6498b30681b7896b6c5c824b518e50f941d`.

Preserve all rows. The source capture report reports unique archive-local record IDs and zero exact repeated rows; repeated contract-number values do not establish duplicate trades or exchange-contract identity.

- No raw, canonical, or user-finalized OHLCV values were modified.
- No date shifts, deletions, deduplication, or canonical promotion occurred.
- Added a fail-closed validator to `scanner_inputs/prepare_scanner_inputs.py`: it validates original and supplemental daily-price rows for OHLCV invariants, duplicate symbol/date keys, and pinned verified-closed dates; validates supported floorsheet CSV schemas, identities, arithmetic, and session dates; and rebuilds weekly/monthly aggregates from observed daily sessions before publishing to a new output directory.
- Both quarantined SMPDA floorsheet archives are blocked by their exact Git blob fingerprints and verified uncompressed SHA-256 fingerprints, so a decompressed copy is also rejected. Regression tests cover this.
- The guard does not edit the input folder, silently filter rows, or repair values; rejected input aborts publication. It is a scanner-preparation guard, not a full canonical-ingestion quarantine implementation.
- No AI recommendations or training labels were enabled or promoted.

## Reproducibility and machine-readable outputs

- Workflow and artifacts: [Run 141](https://github.com/jaljala044/nepse-smc-data/actions/runs/45895851920).
- Standard row-level CSV findings: `NEPSE_GLOBAL_DUPLICATE_AUDIT_FINDINGS.csv`.
- Per-file scan coverage: `NEPSE_GLOBAL_DUPLICATE_AUDIT_SCAN_SUMMARY.csv`.
- Strict pinned-byte row-level findings and exception join: preserved in the run's `p443-strict-content-audit` artifact (`findings.jsonl`, `coverage.json`, `summary.json`, `exception_join.csv`, `exception_join_summary.json`).

## Acceptance still open

1. Classify the 94,543 repeated adjacent tuples using exact overlap with verified open/closed-session evidence and prior P4.37/P4.42 row-level matrices.
2. Review the two unmatched invalid-OHLCV rows (KDBY and KEF) against existing provenance and exception records.
3. Complete date-shift/misdated candidate reconciliation across the full 928-file scope, not only the P4.37/P4.42 samples.
4. Decide whether ingestion quarantine enforcement belongs in a separate implementation issue; do not silently add runtime mutation to this read-only audit PR.

**P4.43 is not complete.** The audit pipeline and pinned scan now pass; evidence adjudication and final acceptance items remain open. PR #80 remains draft until those items are resolved or explicitly accepted as documented blockers.
