# P4.20 — 226-date floorsheet validation results

**Validation date:** 2026-11-26  
**Source:** `socrateai-official/nepse-open-data`, pinned commit `70324524df83eaa7c2964441ad4026d6ab00cc7e`  
**Universe:** 281 current Equity candidates

## 1. Retrieval and pinning

- Daily files retrieved: **226 / 226**
- Expected file sizes matched: **226 / 226**
- Git blob SHA-1 matched the P4.19 manifest: **226 / 226**
- Actual SHA-256 calculated: **226 / 226**
- Download failures: **0**

The per-file SHA-256, retrieval timestamp, URL and response metadata are retained in the P4.20 workflow artifact. The source Git blob ID and size are also retained in the permanent P4.19 manifest.

## 2–3. Schema, contract and amount validation

- Content status: **225 PASS, 1 PARTIAL_FAIL**
- Duplicate/missing contract IDs: **0**
- Date mismatches: **0**
- Missing/invalid buyer or seller broker IDs: **0**
- Amount identity failures after applying the evidence-backed precision policy: **0** on valid rows.

### Historical whole-rupee amount precision

For 2025-12-01, 2025-12-02 and 2025-12-03, the CSV amount field is whole-rupee truncated rather than exact-decimal. Integer-scaled decimal arithmetic verified that every row equals either exact quantity × rate or its exact whole-rupee floor:

| Date | Rows | Exact decimal | Exact floor | Other mismatches |
|---|---:|---:|---:|---:|
| 2025-12-01 | 60,620 | 55,322 | 5,298 | 0 |
| 2025-12-02 | 56,009 | 51,053 | 4,956 | 0 |
| 2025-12-03 | 67,485 | 61,471 | 6,014 | 0 |

The validator accepts only the exact decimal result within NPR 0.01 or a whole-rupee amount exactly equal to the mathematical floor. It does not use a broad tolerance.

### Remaining partial failure — 2026-04-29

One row for `NIBLGF` (transaction `2026042901000179`) reports quantity 1,000 with rate 0 and amount 0. The row fails both positive-rate and positive-amount rules. It is retained as an invalid row; it is not counted as a trade. The other 104,004 valid contracts remain positive evidence for their respective traded symbols. The date remains incomplete/UNKNOWN for absence decisions.

## 4. Daily totals and independent completeness

Exact pipeline-Parquet vs SocrateAI CSV trade-multiset parity is recorded for three dates:

| Date | Matched contracts | One-sided rows | Exact multiset |
|---|---:|---:|---|
| 2026-11-19 | 40,837 | 0 | PASS |
| 2026-11-20 | 39,966 | 0 | PASS |
| 2026-11-24 | 52,387 | 0 | PASS |

Only 2026-11-20 also has separately verified upstream pagination evidence: 39,966 upstream total elements, 80/80 pages, zero rejected rows and zero empty pages. Its independent market totals reconcile to 10,602,468 shares, NPR 3,887,563,470.82 turnover and 352 symbols. The raw bronze API page payloads were not archived.

Therefore:
- **2026-11-20:** `PASS_INDEPENDENT_TOTALS`
- **Other 225 dates:** `UNKNOWN` for full-session completeness

Cross-source multiset equality on 2026-11-19 and 2026-11-24 is corroboration, not a substitute for independently verified pagination/totalElements.

## 5. 281-equity OHLCV comparison

Across the 226 × 281 symbol/date grid (63,506 rows):

- Same-date volume matches: **58,953**
- Volume conflicts: **1,000**
- Positive floorsheet trades with no matching OHLCV date row: **656**

The 1,000 volume conflicts are spread thinly across the universe (top symbol GCIL has 5; most next-ranked symbols have 4). The 656 absent rows are also dispersed (top symbol GBBL has 5). No single-symbol concentration is established by this summary. The date-level CSV artifact is required to inspect each discrepancy.

A conflict is an unresolved discrepancy, not an automatic correction. Possible causes such as price-basis, corporate actions, source revision or incomplete OHLCV archives require per-symbol/date investigation. Missing OHLCV rows remain archive gaps.

## 6. Per-equity/date dispositions

| Disposition | Rows |
|---|---:|
| TRADED | 60,609 |
| UNKNOWN | 2,895 |
| NO_TRADE | 2 |
| **Total** | **63,506** |

The only `NO_TRADE` rows are BNL and NLO on 2026-11-20, after that date's full-session evidence and totals passed. No absent contract on any other date is treated as no trade.

### UNL-specific reconciliation
Across the 226 observed dates, UNL has 185 dates with positive contracts: 748 contracts, 7,974 shares and NPR 376,209,330.70 turnover. The other 41 dates remain `UNKNOWN`, not `NO_TRADE`; no UNL no-trade date is asserted. On 2026-11-20 specifically, UNL had 4 contracts, 50 shares and NPR 2,408,700 turnover. This confirms that UNL does trade infrequently on some observed dates, but the archive cannot yet prove that its other 41 dates were no-trade sessions.

## Artifacts and CI

- P4.20 workflow: https://github.com/jaljala044/nepse-smc-data/actions/runs/45853177867
- Validation CSV artifact (download integrity, daily summary and equity/date dispositions): https://github.com/jaljala044/nepse-smc-data/actions/runs/45853177867/artifacts/15134114504
- The complete workflow run passed. The `PARTIAL_FAIL` is an explicit data-quality result, not a software-test failure.

## Decision

This validates the integrity and row-level content of 226 third-party candidate files, with one documented partial date exception. It does **not** establish a complete official NEPSE session calendar, per-security eligibility for all dates, official source lineage, raw bronze capture completeness, corporate-action-adjusted OHLCV, or broker ownership/manipulation. Do not promote this archive to canonical training/broker-flow data and do not authorize scanner BUYs from this audit.
