# P4.43 / PR #80 acceptance checklist — 2026-11-27

Repository: `jaljala044/nepse-smc-data`  
Branch: `p443-global-integrity-audit`  
Pinned audit input: `main` at `56362fb4f65b91fdcca8f50b50e53ad80e703649`  
Latest completed P4.43 workflow: [Run #338](https://github.com/jaljala044/nepse-smc-data/actions/runs/46046751745), code SHA `f0965688f085050e1a9499bfbca80d60dffe2c3f`  
Issue: [#74](https://github.com/jaljala044/nepse-smc-data/issues/74)  
Draft PR: [#80](https://github.com/jaljala044/nepse-smc-data/pull/80)

This checklist maps the issue's ten acceptance requirements to the evidence currently present. It is not a declaration that P4.43 is fully accepted.

| # | Issue #74 acceptance requirement | Status | Evidence / remaining gap |
|---:|---|---|---|
| 1 | Inventory every relevant OHLCV, floorsheet, calendar and provider/archive file with repository/ref/path/blob SHA/bytes/status | COMPLETE FOR PINNED SCOPE | 928 inventory entries are pinned to the base commit; 928/928 blob and byte checks passed. This is a fixed inventory, not every future repository change. |
| 2 | Count files and parseable records separately; disclose skipped/unsupported files | COMPLETE WITH EXPLICIT EXCEPTIONS | 784 structured files parsed; 138 inventory-only/unsupported files format-inspected; six non-JSON provider responses isolated; count units reconciled in work package #15. Two PDFs remain manual semantic-review exceptions. |
| 3 | Detect exact duplicate rows and duplicate business keys for OHLCV, floorsheets and calendars | COMPLETE WITH SCOPE LIMITS | Run #336/Run #338 audit outputs report zero OHLCV duplicate symbol/date keys, zero exact duplicate OHLCV rows, zero explicit floorsheet source-record-ID repeats in supported checks, and zero duplicate calendar dates. 150 file/check combinations remain unsupported; no composite ID is invented. |
| 4 | Detect duplicate contract IDs without assuming contract number is globally unique | PARTIAL | 74 HF sessions / 6,131,763 rows were audited; 42 sessions contain repeated contract-number values, with 378,766 duplicate-value groups/IDs and 3,449,823 occurrences beyond first. P4.33 samples show unique archive-local source `id` values despite repeated `contract_no`. Full source-by-source identity semantics and independent upstream provenance remain open. |
| 5 | Identify repeated consecutive OHLCV tuples and classify them without blanket deletion | COMPLETE FOR CLASSIFICATION; ADJUDICATION OPEN | 94,543/94,543 pairs classified: 26,544 historical-holiday candidates; 9,027 recorded-closure pairs; 73 both-open/unverified; 58,899 insufficient-session-evidence. Zero corrections/promotions. Full source adjudication remains open. |
| 6 | Identify date-shift/misdated candidates using pinned evidence and official session dates | PARTIAL | Prior P4.27/P4.28, P4.5, P4.37 and P4.42 evidence is cross-referenced. Run #338 exports 46,878 exact repeat-pair lineage gaps. Full 928-file lineage reconciliation, full-period official calendar and historical identity remain incomplete. |
| 7 | Reconcile prior audit outputs without double-counting overlapping findings | PARTIAL | Known cross-audit keys and invalid/repeat overlap are documented; two adjacent pairs (four endpoints) overlap invalid-OHLCV exceptions. Full source/date reconciliation across all historical flags remains open. |
| 8 | Produce row-level findings with source path, row/key, classification, evidence and action | PARTIAL / OUTPUTS PRESENT | Pinned strict findings and review queues include source references and dispositions; the new lineage-gap CSV has 46,878 unique `(symbol,date)` keys with path/blob/row references. Unavailable source evidence remains visible as gaps, not filled by inference. |
| 9 | Add automated regression tests and reproducible command/workflow | COMPLETE FOR IMPLEMENTED AUDIT | Run #338 passed the full P4.43 workflow on code SHA `f0965688f085050e1a9499bfbca80d60dffe2c3f`; lineage exporter tests and export step passed. Separate private Drive publication verification remains blocked and is tracked in P4.44 work package #22. |
| 10 | Publish report with totals, limitations, confirmed/unresolved counts, corrections and quarantines | COMPLETE AS AUDIT BASELINE; FINAL ACCEPTANCE OPEN | `NEPSE_GLOBAL_DUPLICATE_AUDIT_REPORT.md` is updated with Run #338, lineage output and evidence limits. No corrections, deletions, date shifts or canonical promotions were made. Final acceptance depends on resolving or explicitly accepting the outstanding evidence blockers. |

## Run #338 artifact provenance

- Strict artifact ID: `15222152680`; 58,728,598 bytes; SHA-256 `96cbdb5f7d4275c5ee93337b11525237910192897ef4482f92110a6b7f01109d`.
- Global artifact ID: `15221704196`; 1,403,280 bytes; SHA-256 `3e6f452d17bf49f57d504706079e6fecddfd938e67b64c4503d60a38d651f0cc`.
- Both ZIP hashes were independently recomputed and matched GitHub artifact metadata.
- Lineage summary: 94,543 pair keys / 462 symbols; 68,783 lineage keys / 253 symbols; 47,665 exact intersections; 46,878 uncovered keys; 21,118 lineage keys outside the pair set; 209 symbols with no lineage, 245 partial and 8 full.
- Every exported gap row has `lineage_covered=false` and `promotion_allowed=false`; summary has `canonical_data_modified=false`.

## Open acceptance blockers

1. Full historical date/session evidence and effective-dated instrument identity are not available for all 525 OHLCV symbols.
2. Security-date execution evidence is absent for the 23,377-pair P4.44 matrix: 0/46,754 endpoints covered in the pinned capture.
3. Source-level contract-number/record-ID semantics and archive completeness are not established for every floorsheet source.
4. Two PDFs in the pinned inventory still require manual review.
5. Canonical-ingestion quarantine scope is not fully implemented; the existing scanner-preparation guard is not represented as a universal canonical-ingestion gate.
6. P4.44 private Drive end-to-end verification remains blocked by unavailable credentials; no overlay was retrieved or promoted.

## Disposition

- P4.43: **not complete**; reproducible pinned audit baseline and implemented checks pass, while historical evidence adjudication and final acceptance remain open.
- Issue #74: remains open.
- PR #80: remains draft and unmerged; do not merge solely on the basis of Run #338.
- Data safety: raw OHLCV, floorsheets, calendars, canonical data and scanner inputs were not modified by this checklist or the documented read-backs. No correction, deletion, deduplication, date relabeling, promotion or hold release occurred.
