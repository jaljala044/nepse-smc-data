# P4.43/P4.44 Run 313 artifact and session-crosswalk reconciliation

**Date:** 2026-11-27  
**Branch reviewed:** `p443-global-integrity-audit`  
**Run 313 tested commit:** `271c63022d9134e21a1e08718777cbc6f1263ffb`  
**Run 313:** [46007287653](https://github.com/jaljala044/nepse-smc-data/actions/runs/46007287653) — completed successfully.

## 1. Independent artifact read-back

Downloaded both Run 313 artifacts and independently checked their archive SHA-256 and contents:

| Artifact | ID | ZIP bytes | SHA-256 |
|---|---:|---:|---|
| Strict content audit | 15201004193 | 58,287,639 | `47f081e960b9061b19d5023fbaca58490c9c28e2c83db897bee893eceea8f61d` |
| Global duplicate audit | 15200569698 | 1,403,274 | `0bc9495e4e56e7d5dfd2ccee24ff69952238ab32aef4af883172feb22b762d15` |

The strict artifact contains the P4.44 matrix and independent read-back auditor. Its matrix reports 23,377 rows, 209 symbols, 23,377 unique pair IDs, and all rows remain `HOLD_UNKNOWN_NO_INFERENCE`; promotion is false.

## 2. Reconcile the two reported record totals

The global Markdown report's **1,650,883** and strict summary's **1,668,641** are not counts in the same unit.

| Component | Global report convention | Strict coverage convention |
|---|---:|---:|
| CSV / CSV.GZ records | 1,650,790 | 1,650,790 |
| JSON | 93 parsed JSON documents | 17,851 parsed JSON entries |
| **Total** | **1,650,883** | **1,668,641** |

The 17,758 difference is exactly the additional nested/top-level JSON entries counted by the strict parser beyond the global report's one-per-document convention. A path-level comparison found 84 JSON paths with differing JSON record counts; the CSV record totals match exactly. Thus this is a **counting-unit/documentation mismatch**, not evidence of 17,758 missing CSV rows or an unexplained file-scan gap.

Recommendation: retain both measures but label them explicitly as **CSV rows + JSON documents** versus **CSV rows + JSON entries**. Do not publish either as a generic unqualified "records" total.

## 3. Crosswalk the 149-session recovery against the P4.44 repeat-pair matrix

The dedicated session recovery artifact was independently read back:

- 149 session dates, 2026-01-01 through 2026-09-09.
- 148 `CANDIDATE_TOTALS_MATCH`; one `BASELINE_TOTALS_CONFLICT`.
- Every row has `publication_allowed=false`; promoted = 0.
- Pinned scraper source commit: `524442d518d2f2705ade0680c9d2e3f90738e3d6`.

An exact ISO-date join (no ticker/security inference) against the 23,377 P4.44 adjacent-pair rows found:

| Pair-date coverage | Pair rows |
|---|---:|
| Previous date appears in recovered session set | 2,000 |
| Current date appears in recovered session set | 62 |
| Both dates appear | 40 |
| At least one date appears | 2,022 |

The 2,022 pair rows partition as follows:

- 1,960 have a candidate-total match on the previous date only.
- 40 have candidate-total matches on both dates.
- 9 have a candidate-total match on the current date only.
- 13 have the March 1 baseline-total conflict on the current date only.

These are **market-wide session-total crosswalks only**. They do not establish that a particular security traded, validate its OHLCV, establish opening/closing prices, or adjudicate an adjacent repeated tuple. The March 1 conflict remains unresolved and no totals are patched.

## 4. Current validation boundary

Run 313's success applies only to commit `271c630...`. Run 314 was observed in progress on `e5bdfd4...`, while the branch subsequently advanced to `a3fb067a11245c1dc554990113c3f6b6a5065008`. Therefore neither Run 313 nor the in-progress Run 314 is evidence that the current branch head passed the full workflow.

## 5. No-mutation statement

This reconciliation only reads artifacts and joins session dates to pair dates. It does not modify raw floorsheets, OHLCV, canonical dates, identities, lifecycle events, or scanner inputs. No rows are deduplicated, corrected, relabeled, or promoted.

**Disposition:** P4.43 and P4.44 remain open. This document is a reproducibility/read-back checkpoint, not task acceptance.
