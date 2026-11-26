# P4.22 closeout — row dispositions and RHGCL price decision

Date: 2026-11-26  
Repository: `jaljala044/nepse-smc-data`

## Closure decision

**P4.22 is closed as a reconciliation-control milestone, with unresolved historical values explicitly quarantined.** No disputed raw OHLCV has been overwritten, no invalid value has been repaired by inference, and no UNKNOWN row has been converted to NO_TRADE.

This is not a claim that every historical conflict now has an exchange-authenticated value. The closeout means every item in the P4.22 queue has a documented safe disposition and the remaining primary-source work is carried into P4.23.

## Final dispositions

| Work item | Audited result | Final disposition |
|---|---:|---|
| Correct unsupported conflict counts | 87 same-date conflicts; separate internal pair audit has 1 numeric mismatch | Corrected; do not repeat the unsupported 1,000 figure |
| RHGCL 2026-11-19 | SMC raw 252.10 / 259.50 / 252.10 / 256.00 / 4,216; ShareSansar-derived, history-starter and multiple secondary displays agree on 252.10 / 259.50 / 252.10 / 258.00 / 9,054 | Official NEPSE EOD confirms derived Close 258.00, Volume 9,054; payload SHA-256 303d92756ffbcaa2e6ab5020c29e1eab1b63ed99797bf024914dbb863cbae183; preserve SMC raw row |
| Remaining 86 conflicts | All dated 2025-07-28 | QUARANTINE_UNKNOWN; no value selected |
| Invalid external candidates | 109 total: 88 have open > high; 21 have open < low | QUARANTINE_INVALID; no correction inferred |
| Date-shift candidates | 490 total: 238 from 2026-03-02 to 2026-03-01; 252 from 2026-07-25 to 2026-07-24 | Calendar-consistent and value-matched to existing derived rows; raw dates unchanged; no inserts |
| UNKNOWN policy | Retained | No absent or ambiguous row becomes NO_TRADE without full session and floorsheet proof |

## RHGCL 2026-11-19 — final preferred derived price

| Field | SMC raw | Preferred derived value |
|---|---:|---:|
| Open | 252.10 | 252.10 |
| High | 259.50 | 259.50 |
| Low | 252.10 | 252.10 |
| Close | 256.00 | **258.00** |
| Volume | 4,216 | **9,054** |

The 258.00 / 9,054 row is corroborated by the ShareSansar-derived archive, Hamroshare, Stock Nepals, NEPSE Demo Trading and QuantNepal. These are secondary displays and may share upstream data; they are not counted as five independent exchange feeds.

The official NEPSE EOD API was subsequently queried directly for 2026-11-19. It returned one RHGCL row in a 347-row board and the row passed the strict validator with zero quality flags. The exact response was preserved in artifact 15137973461 (run 45862108316); payload SHA-256 is `303d92756ffbcaa2e6ab5020c29e1eab1b63ed99797bf024914dbb863cbae183`. See [official evidence JSON](official_eod_captures/RHGCL_2026-11-19_nepse_eod.json) and [capture artifact](https://github.com/jaljala044/nepse-smc-data/actions/runs/45862108316/artifacts/15137973461).

The repository's 19 November floorsheet CSV contains only 500 contracts (one page), not a complete session capture. It contains two RHGCL prints totalling 480 shares at 258.00, which corroborates the price but cannot prove the full 9,054-share daily volume.

**Decision:** official NEPSE confirms 258.00 / 9,054. The versioned derived RHGCL row is now labelled `OFFICIAL_CAPTURE_ACCEPTED` with payload provenance. Keep the original SMC raw row unchanged. This row may be used as a primary-source-verified historical label subject to the project's normal corporate-action and session checks.

## 86 historical conflicts — why UNKNOWN is the correct result

The other 86 conflicts are concentrated on 2025-07-28. The external historical archive identifies ShareSansar as its source, not NEPSE directly. NEPSE's official EOD history endpoint has a rolling 365-day limit; as of 2026-11-26, 2025-07-28 is outside that window. No authenticated official historical payload was recovered for these rows.

All 86 are therefore explicitly quarantined from canonical scoring and training as `UNKNOWN_SOURCE_CONFLICT`. This is a completed risk-control disposition, not a fabricated resolution of their prices. Future evidence may promote individual rows only after symbol/date/price-basis and corporate-action checks.

## 109 invalid candidates — primary-source resolution

The P4.26 secondary-source audit found 88 OPEN_ABOVE_HIGH and 21 OPEN_BELOW_LOW external rows. P4.28 then captured the official NEPSE EOD board for all four dates and found all 109 exact symbol/date rows, each accepted with zero quality flags and matching the official security ID.

- The official Open differs from the invalid external Open in all 109 rows and is within the official High–Low range.
- High, Low, Close, Volume and Turnover match the external candidates in all 109 rows.
- The official values are recorded in the P4.28 correction ledger. The raw source archives remain unchanged.
- The 109 rows are no longer unresolved UNKNOWN at the evidence layer; derived promotion is scheduled for P4.29.

## 490 date shifts — primary-source confirmation

P4.27 established the row-level secondary-source and calendar evidence. P4.28 then captured the official NEPSE EOD boards for 2026-03-01 and 2026-07-24 and found all 490 exact symbol/date rows, each accepted with zero quality flags and matching the official security ID.

- 238 records: raw SMC date 2026-03-02 → official business date 2026-03-01.
- 252 records: raw SMC date 2026-07-25 → official business date 2026-07-24.
- 487/490 candidate tuples match official EOD exactly.
- Three rows differ only in Close and are corrected by the official record: KBL 191.80 (not 192.00), SAIL 1,329.00 (not 1,306.00), ULBSL 3,178.00 (not 3,118.00).
- The remaining 487 rows are exact OHLCV matches.
- Raw SMC dates and values remain unchanged; the official business date is applied only in the derived correction ledger.

## Reproducible artifacts

The following immutable GitHub Actions artifacts contain the row-level evidence used for this closeout:

| Artifact | Run | Artifact ID | Contents |
|---|---:|---:|---|
| Equity external reconciliation | 45845443879 | 15132056272 | 87 conflict rows, 599 candidate rows, per-symbol summary and hashes |
| Missing equity recovery | 45846116991 | 15132011878 | 490 recovered date shifts and 109 invalid quarantine rows |
| Provisional market equity build | 45845805778 | 15131697026 | Per-row decision ledger and provisional derived OHLCV files |

The reconciliation/recovery artifacts are review-only. The separate RHGCL official EOD artifact is primary-source evidence for that exact daily OHLCV row. No raw source archive was mutated.

## P4.23 — RHGCL official EOD target

**Completed:** official NEPSE EOD capture, exact payload preservation, strict validation, row reconciliation and derived provenance upgrade. See [P4.23 evidence report](p423_official_nepse_eod_evidence_gate_2026-11-26.md).

## P4.24 — completed: 86-row historical close-conflict matrix

The deterministic row-level matrix is merged and available at [P4.24 matrix](p424_2025-07-28_conflict_matrix_2026-11-26.csv), with its [analysis report](p424_2025-07-28_conflict_matrix_report_2026-11-26.md).

- All 86 SMC raw counterpart rows were found.
- All 86 differences are isolated to Close; Open, High, Low and Volume match exactly.
- External close minus SMC close ranges -24.11 to +274.06; 73 positive, 13 negative; median +3.505.
- The external archive identifies ShareSansar as its source. The scanner-input README also identifies the baseline history as ShareSansar-sourced, so the archives may share upstream lineage and are not counted as independent evidence.
- All 86 are now classified `SECONDARY_CONTEMPORANEOUS_SNAPSHOT_CORROBORATED_PRIMARY_PENDING`: the SMC raw closes match the same-day ShareSansar daily-page capture in 86/86, while the later AJAX backfill differs in 86/86. No raw values changed and no backfill close was promoted. This is secondary evidence, not official NEPSE verification.
- Builder tests and PR CI passed; matrix artifact: [15139400460](https://github.com/jaljala044/nepse-smc-data/actions/runs/45862707787/artifacts/15139400460).

## P4.25 — completed: trace 86 close-field lineage

The source-path audit is documented in [P4.25 report](p425_2025-07-28_contemporaneous_sharesansar_snapshot_report_2026-11-26.md), with [86-row three-way evidence](p425_2025-07-28_contemporaneous_sharesansar_snapshot_comparison_2026-11-26.csv).

- SMC raw and contemporaneous ShareSansar daily-page snapshot Close match in 86/86.
- Later historical AJAX backfill Close matches neither the contemporaneous snapshot nor SMC raw in 86/86.
- Open, High, Low and Volume match across all three records in 86/86.
- The SMC raw close is therefore selected for the derived dataset as `SECONDARY_CONTEMPORANEOUS_SNAPSHOT_CORROBORATED`; this is not official NEPSE verification.
- Raw data remains unchanged.

## P4.26 — completed: 109 invalid external candidate audit

The [P4.26 report](p426_109_invalid_candidate_audit_2026-11-26.md) and [109-row snapshot matrix](p426_109_invalid_candidate_snapshot_matrix_2026-11-26.csv) established that 88 OPEN_ABOVE_HIGH and 21 OPEN_BELOW_LOW external values were already present in contemporaneous ShareSansar page captures. P4.28 subsequently superseded the secondary-only status: official NEPSE EOD records were found for all 109 exact symbol/date rows. Official Open is valid for all 109; High, Low, Close, Volume and Turnover match. The primary values are applied in derived v2. Raw source values remain untouched.

## P4.27 — completed: 490 one-day date-shift audit

See [P4.27 report](p427_490_date_shift_audit_report_2026-11-26.md) and [490-row audit matrix](p427_490_date_shift_audit_2026-11-26.csv). CI passed in run [45865050524](https://github.com/jaljala044/nepse-smc-data/actions/runs/45865050524), artifact [15140301490](https://github.com/jaljala044/nepse-smc-data/actions/runs/45865050524/artifacts/15140301490). PR #40 is merged. This was the secondary/calendar stage; P4.28 supersedes the primary-pending disposition.

## P4.28 — completed: official NEPSE EOD validation for all 599 candidates

See [P4.28 report](p428_599_official_eod_batch_validation_2026-11-26.md), [599-row official matrix](p428_599_official_eod_reconciliation_2026-11-26.csv), and [112-row correction ledger](p428_112_official_eod_corrections_2026-11-26.csv). PR #42 is merged. CI passed in run [45866097177](https://github.com/jaljala044/nepse-smc-data/actions/runs/45866097177); immutable payload artifact [15139463647](https://github.com/jaljala044/nepse-smc-data/actions/runs/45866097177/artifacts/15139463647).

- Six complete official NEPSE EOD boards captured; 599/599 target rows found exactly once.
- 599/599 passed official row validation with zero quality flags.
- 599/599 official security IDs match the current instrument snapshot.
- 487 candidate tuples match official OHLCV exactly.
- 109 invalid external rows require official Open correction; all other fields match.
- Three date-shift rows require official Close correction (KBL, SAIL, ULBSL).
- No raw source archive was modified.

## P4.29 — completed: official EOD-backed derived OHLCV v2

The v2 release is published on [derived/ohlcv-v2-official-eod](https://github.com/jaljala044/nepse-smc-data/tree/derived/ohlcv-v2-official-eod/derived/ohlcv_v2), commit `4255cc293a347857ac77c04a947beb784203062f`. See [v2 release report](derived_ohlcv_v2_release_2026-11-26.md).

- 281 symbols; 246,129 v1 source rows → 246,238 v2 derived rows.
- 599 official NEPSE EOD rows applied across 254 symbols.
- 490 date shifts moved to official business dates in derived files only.
- 109 official rows inserted where the v1 raw-derived files had no row.
- 112 official field corrections: 109 Open and 3 Close.
- 713 correction ledger entries, including the two prior RHGCL field corrections.
- Every one of the 281 raw source Git blob hashes was revalidated; raw source files modified: 0.
- Regression tests and v2 build passed in CI run [45867152948](https://github.com/jaljala044/nepse-smc-data/actions/runs/45867152948); artifact [15139594805](https://github.com/jaljala044/nepse-smc-data/actions/runs/45867152948/artifacts/15139594805).

## P4.30 — completed: full v2 integrity audit and guarded scanner gate

The [P4.30 audit report](derived_ohlcv_v2_integrity_audit_2026-11-26.md) records the full 281-symbol check. CI run [45868691178](https://github.com/jaljala044/nepse-smc-data/actions/runs/45868691178) passed with artifact [15141173903](https://github.com/jaljala044/nepse-smc-data/actions/runs/45868691178/artifacts/15141173903).

- 281/281 raw Git blob hashes and 599/599 official provenance rows verified.
- Zero duplicate-date or ordering flags.
- 1,329 unique invalid OHLCV rows across 13 symbols; 1,379 reason flags. No automatic repair.
- 71,806 adjacent repeated rows across 256 symbols: 18,910 closed-session candidates, 52,891 outside calendar evidence, and 5 open-session repeats.
- Corporate-action evidence remains partial: 3 events across 3 symbols; 278 symbols have no action record; one NLIC split proposal lacks a verified effective date.
- T+2/swing may use individually valid, sufficiently liquid bars only. Positional/investment adjusted-return metrics remain unsafe until corporate-action history is validated.

## Next priority — P4.31: verify five open-session repeated rows

Capture complete official NEPSE floorsheets for both dates in each of the five repeated pairs: BNL (2026-11-13/17), BNT (2026-06-29/07-01), ENL (2026-08-25/26), and UNL (2026-08-24/27 and 2026-09-28/29). Reconcile contract count, quantity and rates to the EOD rows. Missing, incomplete or mismatching evidence must remain UNKNOWN; UNL must not be upgraded without exact symbol/date validation.

The first company-floorsheet API attempt returned HTTP 403 for all ten symbol/date requests. Raw 403 response bodies and hashes are retained in artifact [15141637485](https://github.com/jaljala044/nepse-smc-data/actions/runs/45869582371/artifacts/15141637485). An official EOD-board fallback capture is running; it can confirm daily OHLCV but does not replace a complete floorsheet.
