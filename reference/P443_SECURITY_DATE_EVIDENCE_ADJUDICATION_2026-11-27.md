# P4.43 — security/date evidence-review queue adjudication

Date: 2026-11-27  
Pinned input: `56362fb4f65b91fdcca8f50b50e53ad80e703649`  
Source: strict audit artifact from [workflow run 45928679963](https://github.com/jaljala044/nepse-smc-data/actions/runs/45928679963), `unresolved_pair_security_evidence.csv`.

## Scope

All 58,972 pairs in the `REQUIRE_INDEPENDENT_SECURITY_DATE_EVIDENCE` queue were reviewed. The queue covers 456 symbols. The review reconciled the pair-level evidence result, each member's security-date evidence result, and the recorded session-calendar classification.

## Disjoint disposition

| Disposition | Pairs | Meaning |
|---|---:|---|
| No security-date evidence for either date | 58,462 | Neither member has pinned official security-date evidence; session/execution status remains unknown. |
| Previous-date HLCV match only | 437 | Previous date has HLCV + execution-count match, but current date is unverified and Open remains unverified. |
| Both dates open; tuples unverified | 73 | Calendar evidence marks both dates open, but neither security tuple has security-date corroboration. |
| **Total** | **58,972** | All candidates accounted for exactly once. |

Additional checks:
- Current-date security evidence is missing for all 58,972 pairs.
- Previous-date security evidence is missing for 58,535 pairs; the other 437 are HLCV/execution-count matches with Open unverified.
- No pair member is flagged as a listed holiday in this queue.

## Decision

This completes **queue triage**, not full independent adjudication. None of the 58,972 pairs has evidence sufficient to validate both OHLCV records or establish that the repeated tuple is erroneous.

- Keep all 58,972 pairs in `HOLD_UNRESOLVED`.
- Do not infer no trading from missing source records.
- Do not infer security execution from an open exchange session.
- Do not infer full OHLCV validity from HLCV/execution-count matches; Open remains unverified.
- No row deletion, deduplication, date shift, correction, or promotion.

## Reproducibility

- Machine-readable summary: `reference/P443_SECURITY_DATE_EVIDENCE_ADJUDICATION_SUMMARY_2026-11-27.json`.
- Full 58,972-row row-level disposition crosswalk: companion CSV `P443_SECURITY_DATE_EVIDENCE_ADJUDICATION_2026-11-27.csv`, SHA-256 `993f4dca976c31ab4d4012ed9cafc4178e784dce53c6f90479ec4aef5e521c21`.

## Remaining work

To move these cases beyond HOLD requires additional independently sourced evidence: official security/date EOD history with complete fields, authenticated exchange session/holiday records, and/or complete security-specific execution floorsheets with reliable symbol identity and session coverage. Existing archive gaps cannot be treated as negative proof.

**Status:** all 58,972 queue entries triaged and classified; substantive independent adjudication remains blocked by missing evidence. P4.43 remains open, draft and unmerged.
