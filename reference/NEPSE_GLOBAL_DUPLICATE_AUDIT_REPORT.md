# P4.43 global duplicate and data-integrity audit

**Status: reproducible audit baseline complete; adjudication and canonical-ingestion acceptance remain open.**

**Pinned input:** `main` at `56362fb4f65b91fdcca8f50b50e53ad80e703649`.  
**Latest validated workflow:** [Run 104](https://github.com/jaljala044/nepse-smc-data/actions/runs/45894421068), head `c4f2207db7b6baf8d90d27325ea7da9c2b7e5219`.  
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

The triage checks the current row's date, not the prior row's date. It does not establish that a tuple is valid, invalid, carried forward, or date-shifted. No tuple is independently verified and no automatic correction is permitted. Full row-level dispositions are retained in the workflow artifact `repeat_calendar_triage.csv`.

P4.37 independently identified 1,455 canonical-only rows across 24 sampled symbols that match official HLCV tuples on 81 verified closed dates. P4.42 traced the NMLBBL/SMPDA date-label pattern to ShareSansar scrape-date filenames. These source-backed findings are useful but do not independently classify every adjacent tuple across the full historical universe.

Historical session evidence remains incomplete outside the captured one-year official EOD window. Do not infer an open session from weekdays or absence from a closure list. Do not label repeated tuples as NO_TRADE or as erroneous solely because values repeat.

## Quarantine and safeguards

The two 2024 SMPDA floorsheet archives remain `BLOCK_CANONICAL`:
- `reference/p433_floorsheets/floorsheet_2024-08-14.csv.gz` — blob `0dd938bc5e6bfd50fa09bf85f0836d443ab15983`.
- `reference/p433_floorsheets/floorsheet_2024-08-18.csv.gz` — blob `49d6498b30681b7896b6c5c824b518e50f941d`.

Preserve all rows. The source capture report reports unique archive-local record IDs and zero exact repeated rows; repeated contract-number values do not establish duplicate trades or exchange-contract identity.

- No raw, canonical, or user-finalized OHLCV values were modified.
- No date shifts, deletions, deduplication, or canonical promotion occurred.
- No quarantine rule was integrated into production ingestion in this audit-only task.
- AI recommendations and scanner/training eligibility were not changed.

## Reproducibility and machine-readable outputs

- Workflow and artifacts: [Run 104](https://github.com/jaljala044/nepse-smc-data/actions/runs/45894421068).
- Standard row-level CSV findings: `NEPSE_GLOBAL_DUPLICATE_AUDIT_FINDINGS.csv`.
- Per-file scan coverage: `NEPSE_GLOBAL_DUPLICATE_AUDIT_SCAN_SUMMARY.csv`.
- Strict pinned-byte row-level findings and exception join: preserved in the run's `p443-strict-content-audit` artifact (`findings.jsonl`, `coverage.json`, `summary.json`, `exception_join.csv`, `exception_join_summary.json`).

## Acceptance still open

1. Classify the 94,543 repeated adjacent tuples using exact overlap with verified open/closed-session evidence and prior P4.37/P4.42 row-level matrices.
2. Review the two unmatched invalid-OHLCV rows (KDBY and KEF) against existing provenance and exception records.
3. Complete date-shift/misdated candidate reconciliation across the full 928-file scope, not only the P4.37/P4.42 samples.
4. Decide whether ingestion quarantine enforcement belongs in a separate implementation issue; do not silently add runtime mutation to this read-only audit PR.

**P4.43 is not complete.** The audit pipeline and pinned scan now pass; evidence adjudication and final acceptance items remain open. PR #80 remains draft until those items are resolved or explicitly accepted as documented blockers.
