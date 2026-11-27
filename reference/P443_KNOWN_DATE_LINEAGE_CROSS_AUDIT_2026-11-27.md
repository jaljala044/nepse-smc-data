# P4.43 — exact-key reconciliation of known date-lineage audits

Date: 2026-11-27  
Pinned global input: `56362fb4f65b91fdcca8f50b50e53ad80e703649`

## Result

Built a key-level crosswalk across the already completed P4.27/P4.28, P4.5, P4.37 and P4.42 evidence matrices. The exact de-duplication key is `symbol + source_date`.

- P4.27/P4.28: 490 candidate source rows across 254 symbols. All 490 were found exactly once in official NEPSE per-security EOD history; 487 full OHLCV tuples match and three official Close values differ. The broader P4.28 official response matrix contains 599 rows: 490 recovered-date rows and 109 invalid external OHLCV rows. The correction ledger contains 112 entries.
- P4.5: all 20 overlay rows (18 symbols) are already included in P4.27's 490 source-date keys. They add **zero** unique rows.
- P4.37: 1,455 verified-closed-date carry-forward rows across 19 symbols in a purposive 24-security / 12-sector sample.
- P4.42: 162 source-date lineage rows across NMLBBL and SMPDA, each with a source-row match and a unique official HLCV+volume match on another date.

## Exact overlaps

| Audit overlap | Shared symbol/source-date keys |
|---|---:|
| P4.5 with P4.27 | 20 (all P4.5 rows) |
| P4.42 with P4.27 | 4 |
| P4.42 with P4.37 | 0 |
| P4.37 with P4.27 | 36 |

The distinct union is **2,067 symbol/source-date keys**:

`490 + 162 + 1,455 - 4 - 36 = 2,067`

P4.5 contributes no additional keys because its 20 rows are already within P4.27. These counts are de-duplicated by key; they do not imply that all evidence classes have equal strength or authorize automatic date relabeling.

## Committed artifacts

- `reference/P443_KNOWN_DATE_LINEAGE_CROSS_AUDIT_2026-11-27.csv`: 2,067-row union crosswalk, including audit membership, official matched date/offset where available, and P4.5 overlay membership.
- `reference/P443_KNOWN_DATE_LINEAGE_CROSS_AUDIT_2026-11-27.json`: counts, overlap arithmetic, source blob SHAs and outstanding coverage limits.

The crosswalk was generated from these pinned source matrices:
- P4.27: `p427_490_date_shift_audit_2026-11-26.csv`
- P4.28: `p428_599_official_eod_reconciliation_2026-11-26.csv` and `p428_112_official_eod_corrections_2026-11-26.csv`
- P4.42: `p442_sharesansar_date_lineage_matrix_2026-11-26.csv`
- P4.37: `p437_cross_sector_date_audit/quarantine_matrix.csv`
- P4.5: `P4_5_date_shift_overlay_2026-11-26.csv`

## Full-scope coverage gap — still open

This is a reproducible cross-audit reconciliation of existing evidence, **not** completion of the full 928-file date-lineage scan.

The pinned global inventory contains 928 files (525 OHLCV archive files). The global repeat scan reports 462 symbols with repeated-tuple findings. The strict security/date source-lineage table has 68,783 rows across 253 symbols, leaving 209 of those 462 repeat-finding symbols absent from that table. The 94,543 adjacent-repeat calendar triage rows all have `prior_date_shift_candidate=false`; that field is a repeat-pair triage result, not a general row-level date-shift detector.

The current evidence therefore does not establish date lineage for all 525 OHLCV files, all instruments, or all historical dates. A full pass still requires:
1. effective-dated official security-ID mapping for every source symbol (including historical aliases and non-equity instruments);
2. a complete, evidence-backed NEPSE open/closed calendar for the relevant history;
3. official per-security EOD date-key histories or complete date-matched floorsheets with verified symbol identity and coverage;
4. row-level source-date-to-business-date matching across every applicable file, preserving ambiguity and duplicate matches as HOLD/UNKNOWN.

No missing source record is treated as proof of no trade. The 24-security P4.37 sample is purposive and cannot be extrapolated to the full universe. The official EOD HLCV-only endpoint does not validate Open. No source rows, dates or canonical OHLCV values were changed, relabeled, deleted, deduplicated or promoted.

**Status:** known-audit exact-key reconciliation complete (2,067 unique keys); full 928-file date-lineage adjudication remains incomplete. P4.43 remains open, draft and unmerged.
