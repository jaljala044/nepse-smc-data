# P4.43 — uncovered repeated-OHLCV identity and instrument-scope triage

Date: 2026-11-27  
Pinned global-audit source commit: `56362fb4f65b91fdcca8f50b50e53ad80e703649`  
External reference commit: `5a8768828d58bdcebb82393262726d1d030b7ec4`

## Result

All **209/209** uncovered repeat-finding symbols were compared against the scanner repository's dated 2026-11-25 NEPSE security snapshot, 2026-11-26 equity crosswalk, and 2026-11-26 unmatched-symbol review.

| Measure | Count |
|---|---:|
| Uncovered symbols assessed | 209 |
| Symbols present in current security snapshot | 175 |
| Symbols absent from current snapshot | 34 |
| Current equity crosswalk matches | 3 |
| Snapshot names suggest debenture/bond | 61 |
| Snapshot names suggest promoter share | 62 |
| Snapshot names suggest fund/yojana | 34 |
| Snapshot records requiring instrument-class review | 15 |
| Existing unmatched-review rows | 34 |
| Of those: unresolved historical identity | 26 |
| Of those: filename-encoding candidates | 8 |

Snapshot status values among matched symbols: `A`: 172, `S`: 3.

## Equity candidate matches

The three exact current equity-crosswalk matches are NESDO (snapshot ID 8041), ULBSL (8063), and YMHL (9342). A separate Priority 94 evidence report at the same external commit supports their ordinary-equity classification using provider company profiles/listing evidence. These remain current-snapshot IDs; the evidence does not establish historical ID continuity or effective-dated lifecycle mapping.

## Classification limits

The debenture/bond, promoter-share, and fund/yojana counts are **name-based triage from the dated security snapshot's display name**, not authoritative instrument-type fields. The 15 other snapshot records are intentionally unclassified. Snapshot presence does not prove the instrument's historical identity on each OHLCV date. Absence from the current snapshot does not prove that a symbol was never listed, was not an equity, or had no historical security ID.

The 34 symbols absent from the snapshot remain unresolved; the existing unmatched-symbol review labels 26 as unresolved historical identities and eight as filename-encoding candidates needing review. No filename decoding was promoted as a canonical ticker. Candidate IDs in that review are not accepted as stable IDs.

## Disposition

This reduces uncertainty about the likely instrument mix in the 209-symbol gap, but it does **not** adjudicate any repeated candle or date. All 23,377 pair findings remain `HOLD/UNKNOWN` pending per-date authoritative evidence and effective-dated identity. No OHLCV value was corrected, shifted, deleted, deduplicated, or promoted. No canonical identity, price-history splice, scanner coverage admission, or model-training approval is authorized.

## Reproducibility

The row-level 209-symbol triage is in `P443_UNCOVERED_REPEAT_SYMBOL_IDENTITY_TRIAGE_2026-11-27.csv`; machine summary is `P443_UNCOVERED_REPEAT_SYMBOL_IDENTITY_TRIAGE_2026-11-27.json`.
