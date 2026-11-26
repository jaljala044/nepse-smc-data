# P4.23 — 2025-07-28 conflict counterpart index
Date: 2026-11-26

## Scope
- The P4.22 reconciliation artifact contains 87 unique SAME_DATE_VALUE_CONFLICT keys.
- 86 keys are dated 2025-07-28; the remaining key is RHGCL on 2026-11-19 and is deliberately excluded from this batch.
- This index captures the pinned external archive side for all 86 keys. It is not primary NEPSE evidence and does not resolve any conflict.

## Provenance
- External repository: `srijankarki07/nepse-data`
- Pinned commit: `688d59c03915dcee73ecad4230d2083a41c61764`
- Source file: `data/daily/2025/2025-07-28.csv`
- Retrieved Git blob SHA: `329146bbdb0ef66722933f8aba0542c7e4ec78f8`
- Source is a secondary archive snapshot; upstream independence from NEPSE is not established here.
- Companion CSV: `p423_2025-07-28_external_conflict_counterpart_2026-11-26.csv`

## Validation
- Expected conflict keys: 86
- External counterpart rows retrieved: 86
- Missing counterpart rows: 0
- Duplicate counterpart rows: 0
- Each row retains source repository, commit, path, evidence tier, and `CONFLICT_UNRESOLVED_PRIMARY_EVIDENCE_PENDING` disposition.
- Original SMC and external raw OHLCV archives were not modified.

## Decision
All 86 rows remain quarantined. A matching secondary archive record is only the other side of the original discrepancy, not independent corroboration. Resolution requires date-matched primary NEPSE EOD evidence or complete date-scoped floorsheets, with corporate-action and price-basis checks.

## Separate RHGCL key
RHGCL 2026-11-19 remains outside this 2025-07-28 batch. Preserve its separate source reconciliation and pending primary confirmation.