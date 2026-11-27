# P4.43 — first-pass quarantine-pair adjudication

Date: 2026-11-27  
Pinned input: `56362fb4f65b91fdcca8f50b50e53ad80e703649`  
Evidence: strict audit artifact from [workflow run 45928679963](https://github.com/jaljala044/nepse-smc-data/actions/runs/45928679963)

## Scope and method

Reviewed all 35,571 pairs in `repeat_quarantine_candidates.csv`. For each pair, joined both member rows (current and previous) against the existing row-level `recorded_closure_row_hold.csv` and `historical_api_holiday_hold_candidates.csv`, using exact path + pinned blob SHA + row number. No symbol/date-only fuzzy matching was used.

## Results

| Pair disposition | Pairs | Symbols | Interpretation |
|---|---:|---:|---|
| Recorded-closure row hold | 9,027 | 379 | At least one member exactly matches the recorded closure hold register |
| Historical-API-holiday corroborated hold | 26,544 | 400 | At least one member exactly matches the historical API holiday hold register |
| Unexplained by either register | 0 | — | No unmatched pair in this queue |
| **Total** | **35,571** | | |

The two buckets are disjoint and sum exactly to the source queue.

### Row-level join checks

- Closure register: 6,232 rows; 6,232 matched current pair members and 4,060 matched previous pair members. 1,265 pairs have both members in the closure register.
- Historical API holiday register: 22,244 rows; 22,244 matched current pair members and 11,517 matched previous pair members. 7,217 pairs have both members in the holiday register.
- Holiday evidence references two distinct source blobs.

## Adjudication boundary

This pass establishes exact consistency between the 35,571 pair queue and the two existing row-level hold registers. It does **not** independently prove that every listed date was universally closed, prove that a security had no execution, or prove that a repeated candle is false.

Therefore:
- retain all 35,571 pairs in hold/review status;
- do not delete, deduplicate, shift, correct, or promote any OHLCV row;
- keep all `promotion_allowed=false`;
- continue independent provenance checks for closure/holiday sources and security-specific execution evidence.

## Reproducibility

- Machine-readable counts: `reference/P443_QUARANTINE_PAIR_ADJUDICATION_SUMMARY_2026-11-27.json`
- Full row-level exact-join crosswalk: `P443_QUARANTINE_PAIR_ADJUDICATION_CROSSWALK_2026-11-27.csv` (companion generated artifact; SHA-256: `b7d53ad75c0c03605ebe7d45b4bd9ac43d58470e20ea162170f98a91fad7a564`).
- Crosswalk has 35,571 rows and records exact current/previous row matches, pair bucket, and explicit no-promotion/no-modification safeguards.

**Status:** first-pass pair-to-register adjudication complete. P4.43 overall remains open; independent closure provenance, full historical date-lineage reconciliation, canonical-ingestion enforcement, and production acceptance remain outstanding.
