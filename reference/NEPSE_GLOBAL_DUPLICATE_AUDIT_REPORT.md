# P4.43 global duplicate and data-integrity audit

**Status: reproducible audit baseline complete; adjudication and canonical-ingestion acceptance remain open.**

**Pinned input:** `main` at `56362fb4f65b91fdcca8f50b50e53ad80e703649`.  
**Latest validated workflow:** [Run 205](https://github.com/jaljala044/nepse-smc-data/actions/runs/45899093388), head `7d24f589fef069cdc161ece039ac89cc77cd691b`; all workflow stages passed, including the strict pinned-byte scan, exception join, calendar triage, all-58,972-pair official-history check, recovery-queue regression, and artifact preservation. The separate priority-floorsheet recovery PR check [Run 4](https://github.com/jaljala044/nepse-smc-data/actions/runs/45899093277) also passed.  
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
- **2** do not match the historical equity exception registers: KDBY, 2026-04-29 (row 854), and KEF, 2026-04-28 (row 1160). Both are independently identified in the pinned official security master (`reference/p435_official_historical_floorsheets/security_list.json`, blob `0891e10b56de572816680c8065718ecd4420bd03`) as investment-fund instruments: Kumari Dhanabriddhi Yojana and Kumari Equity Fund. They are recorded separately in `P443_NON_EQUITY_OHLCV_EXCEPTIONS_2026-11-27.csv` and remain quarantined from the equity candle set; this classification does **not** validate or repair their prices.

An exception-register match is reconciliation, **not independent validation**. The prior P4.35 source-lineage audit found no qualified independent historical source for the affected equity candles; matched rows remain UNKNOWN pending source adjudication. No values were repaired or promoted.

### UNL secondary-source recheck (not transaction verification)

The branch preserves three UNL rows from `03_stock_charts_ohlcv/UNL_OHLCV.csv` in `P443_UNL_PRIORITY_PRICE_CORROBORATION_2026-11-27.csv` (source blob `107d1ef058992cfd1b8b4a88db9f6304edf22932`, rows 809, 810, 822). A secondary-source recheck found matching published OHLCV/volume values for 2026-08-24 and 2026-08-27 on ArthaKendra's UNL price-history page, and for 2026-09-28 on the NEPSEAlpha UNL history result. These are **secondary aggregator matches**; their upstream lineage/independence is unknown and they provide no exchange contract IDs. The separate `P443_UNL_SECONDARY_SOURCE_RECHECK_2026-11-27.csv` records the URLs and exact fields matched. All three remain `contract_verified=false` and `promotion_allowed=false`; no canonical value was changed.

### Targeted priority floorsheet observations (third-party archive only)

The dedicated recovery workflow [Run 4](https://github.com/jaljala044/nepse-smc-data/actions/runs/45899093277) passed on the current PR revision and reproduced the successful ten-partition retrieval from [Run 1](https://github.com/jaljala044/nepse-smc-data/actions/runs/45898947134). For BNL (2026-11-13, 2026-11-17), BNT (2026-06-29, 2026-07-01), ENL (2026-08-25, 2026-08-26), and UNL (2026-08-24, 2026-08-27, 2026-09-28, 2026-09-29), each pinned daily file passed byte-size/Git-blob verification and row/schema/arithmetic checks. Each selected symbol/date had one observed 10-share row at the expected rate and matching amount. The rows and source hashes are preserved in `P443_PRIORITY_FLOORSHEET_CONTRACT_OBSERVATIONS_2026-11-27.csv`.

These are **third-party archive observations**, not independently authenticated exchange records. The archive's file-level completeness status is `UNKNOWN`, source independence is `UNKNOWN`, and the archive's contract-number field is not treated as a verified exchange contract ID. No absence inference is permitted; no OHLCV opening price is established by this check. All ten remain `promotion_allowed=false`; no canonical values were changed.

### Priority-equity external archive comparisons

Four symbol-specific comparisons now preserve the 2026-11-27 external archive matches for the existing invalid-OHLCV exception registers:

| Symbol | Register rows | Aabishkar2 | SamirWagle | binayabaral | srijankarki07 | Verified replacements |
|---|---:|---:|---:|---:|---:|---:|
| API | 122 | 113 match / 9 missing | 122 match | 113 / 9 | 121 / 1 | 0 |
| SKBBL | 379 | 379 match | 379 match | 379 match | 378 / 1 | 0 |
| MERO | 102 | 102 match | 102 match | 102 match | 102 match | 0 |
| SPDL | 53 | 46 / 7 | 53 match | 46 / 7 | 53 match | 0 |

`match` here means the external daily archive repeats the same candidate tuple already flagged as invalid in the pinned exception register; it is **not** a valid replacement. The missing counts are unavailable rows in that source, not proof of no trade. All four repository records show `fork=false` in GitHub metadata, but that does not establish independent data lineage; copied upstream data, common source capture, LTP/close mapping, corporate actions and execution evidence remain unverified. Per-source blobs and row-level dates are preserved in `API_EXTERNAL_SOURCE_RECONCILIATION_2026-11-27.json`, `SKBBL_EXTERNAL_SOURCE_RECONCILIATION_2026-11-27.json`, `MERO_EXTERNAL_SOURCE_RECONCILIATION_2026-11-27.json`, and `SPDL_EXTERNAL_SOURCE_RECONCILIATION_2026-11-27.json`. No replacement was verified or promoted.

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

The pair-level classifier verifies both pinned source rows and exact OHLCV tuple equality, checks calendar evidence for both the current and previous dates, and exports disjoint review queues:

| Pair disposition | Count | Review queue |
|---|---:|---|
| PAIR_CONTAINS_HISTORICAL_LISTED_HOLIDAY | 26,544 | Review pair for quarantine |
| PAIR_CONTAINS_RECORDED_CLOSURE | 9,027 | Review pair for quarantine |
| BOTH_OPEN_TUPLE_UNVERIFIED | 73 | Require independent security/date evidence |
| INSUFFICIENT_SESSION_EVIDENCE | 58,899 | Require independent security/date evidence |

The two review queues contain **35,571** pair candidates for quarantine review and **58,972** pairs requiring independent security/date evidence. Every row has `promotion_allowed=false`; the workflow reports zero corrected rows and zero promoted rows. A historical listed-holiday entry is a candidate, not proof of universal closure. An open market session does not establish a security-specific execution. Pair classification is not an instruction to delete either source row.

Full row-level pair dispositions and the two disjoint review queues are retained in the workflow artifact: `repeat_calendar_triage.csv`, `repeat_quarantine_candidates.csv`, and `repeat_evidence_review.csv`.

### Official security-history check of open-session pairs

Run 156 additionally checked all **73** `BOTH_OPEN_TUPLE_UNVERIFIED` pairs against the pinned official per-security EOD history captures. Result: **73 / 73 had no matching security/date evidence** for either side of the pair (`NO_SECURITY_DATE_EVIDENCE` for current and previous rows). This is an evidence-availability result, not evidence that no trade occurred. All 73 remain unverified, `promotion_allowed=false`, and no rows were corrected. The source EOD fields, where available, would only establish HLCV and execution counts—not opening price—so even a match would not have independently validated the complete OHLCV tuple.

### Equity-first prioritization of unresolved pairs

Run 166 also joined the 58,972 unresolved/evidence-review pairs to the pinned 2026-11-26 active-instrument crosscheck. This is a current-status prioritization aid only; it does not establish the instrument's point-in-time classification on the historical pair dates or prove execution.

| Pair class | Current equity first-pass | Current mutual fund | Unclassified / not in captured active lists | Total |
|---|---:|---:|---:|---:|
| BOTH_OPEN_TUPLE_UNVERIFIED | 5 | 5 | 63 | 73 |
| INSUFFICIENT_SESSION_EVIDENCE | 44,283 | 6,351 | 8,265 | 58,899 |
| **Total** | **44,288** | **6,356** | **8,328** | **58,972** |

The five open-session equity-priority pairs concern BNL (1), BNT (1), ENL (1), and UNL (2). Five open-session mutual-fund pairs concern C30MF, LVF2, SAGF, and SFEF. The remaining 63 open-session pairs are unclassified by the captured current master. All remain unverified and `promotion_allowed=false`; current active status is not historical identity or execution evidence. The full row-level file `equity_first_repeat_review.csv` and summary `equity_first_repeat_summary.json` are preserved in the strict audit artifact. The workflow also exports `equity_security_date_recovery_queue.csv` and `equity_security_date_source_lineage.csv`, deduplicating both sides of the equity-priority pairs into security/date evidence requests while preserving source blob/row references; this queue is not evidence of invalidity or permission to alter data. Run 190 produced **68,783 unique security/date requests** across 253 current-equity-first-pass symbols from 44,288 pairs (5 both-open and 44,283 insufficient-session pairs): 10 `P1_OPEN_PAIR` dates and 68,773 `P2_SESSION_AND_EXECUTION` dates. The queue includes both sides of each pair and is an evidence-acquisition worklist, not a finding that those rows are invalid.

Run 190 completed the read-only cross-check of **all 58,972** evidence-review pairs against the pinned official per-security EOD captures:

| Calendar pair class | No security/date capture for either date | Previous-date HLCV/execution match; current date unverified | Total |
|---|---:|---:|---:|
| BOTH_OPEN_TUPLE_UNVERIFIED | 73 | 0 | 73 |
| INSUFFICIENT_SESSION_EVIDENCE | 58,462 | 437 | 58,899 |
| **Total** | **58,535** | **437** | **58,972** |

There were **zero** pairs with both dates matched, zero HLCV mismatches, and zero conflicting official captures. The source-presence counts show no current-date captures for any of the 58,972 pairs; 437 previous dates have captures whose HLCV plus positive execution counts match. This is partial evidence only: the current row remains unverified, and official EOD fields do not provide opening price. The other 58,535 pairs have no security/date capture on either side. Missing capture is not proof of no trade. All rows remain `promotion_allowed=false`; no source rows were corrected or promoted. Run 182's import-test failure was fixed, and run 190 passed both new regression suites and the full cross-check.

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

- Latest complete workflow and artifacts: [Run 205](https://github.com/jaljala044/nepse-smc-data/actions/runs/45899093388); all scan, quarantine, cross-repository contract, strict-byte, exception join, pair-calendar triage, disjoint queue, row-hold, authenticated-holiday, open-pair check, equity-first triage, all-58,972-pair official-history check, recovery-queue regression, and artifact-preservation stages passed. The targeted floorsheet workflow [Run 4](https://github.com/jaljala044/nepse-smc-data/actions/runs/45899093277) passed and preserves the 10-row observation CSV.
- Standard row-level CSV findings: `NEPSE_GLOBAL_DUPLICATE_AUDIT_FINDINGS.csv`.
- Per-file scan coverage: `NEPSE_GLOBAL_DUPLICATE_AUDIT_SCAN_SUMMARY.csv`.
- Strict pinned-byte row-level findings and exception join: preserved in the run's `p443-strict-content-audit` artifact (`findings.jsonl`, `coverage.json`, `summary.json`, `exception_join.csv`, `exception_join_summary.json`, `open_pair_security_evidence.csv`, `open_pair_security_summary.json`, `unresolved_pair_security_evidence.csv`, `unresolved_pair_security_summary.json`, `equity_first_repeat_review.csv`, `equity_first_repeat_summary.json`, `equity_security_date_recovery_queue.csv`, `equity_security_date_source_lineage.csv`, `equity_security_date_recovery_summary.json`).

## Acceptance still open

1. Classify the 94,543 repeated adjacent tuples using exact overlap with verified open/closed-session evidence and prior P4.37/P4.42 row-level matrices.
2. Complete date-shift/misdated candidate reconciliation across the full 928-file scope, not only the P4.37/P4.42 samples; historical session evidence is incomplete for much of the 2011–2026 OHLCV span.
3. Obtain independent security/date and execution evidence to adjudicate the 35,571 quarantine-review pairs and 58,972 evidence-review pairs. The 73 pairs checked against official security history had no matching security/date capture; this does not prove no trade. Current calendar/API corroboration is not proof of security-specific execution.
4. Decide whether full canonical-ingestion quarantine enforcement belongs in a separate implementation issue; the scanner-preparation guard is not a canonical ingestion gate.

**P4.43 is not complete.** The audit pipeline and pinned scan now pass; evidence adjudication and final acceptance items remain open. PR #80 remains draft until those items are resolved or explicitly accepted as documented blockers.
