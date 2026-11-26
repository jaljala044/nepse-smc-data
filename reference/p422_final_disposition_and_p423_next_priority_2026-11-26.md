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

## 109 invalid candidates — investigation result

The full 109-row recovery queue was inspected. Every row fails the OHLC envelope because either the open is above the high (88 rows) or the open is below the low (21 rows). No row has a non-positive price, non-positive volume, high-below-low condition, or close outside the high/low range. The values remain in the quarantine artifact; no OHLC field is rewritten.

## 490 date shifts — audited, secondary corroboration complete

P4.27 independently audited all 490 candidate rows:

- 238 records: raw SMC date 2026-03-02 → provisional derived target 2026-03-01.
- 252 records: raw SMC date 2026-07-25 → provisional derived target 2026-07-24.
- All 490 OHLCV tuples match the SMC raw row on the following date.
- All 490 also match the ShareSansar daily-page capture made on the following date (2026-03-02 and 2026-07-25).
- The canonical calendar marks the candidate dates as `verified_open_observed` (official positive trade observation for security ID 8108 only) and the following raw dates as `verified_closed` (official holiday / weekly closure).
- The same-day ShareSansar capture for 2026-03-01 contains only 13 symbols and none of the 238 candidate symbols; no 2026-07-24 capture was found. The next-day snapshots are secondary corroboration, not primary per-security trade proof.

All 490 remain `SECONDARY_CORROBORATED_ONE_DAY_DATE_SHIFT_PRIMARY_PENDING`. The one-day derived mapping is supported for provisional use, but is not scanner-approved or primary-confirmed. Raw source dates and values remain unchanged. No rows were inserted.

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

The row-level comparison is documented in [P4.26 audit report](p426_109_invalid_candidate_audit_2026-11-26.md) and [109-row snapshot matrix](p426_109_invalid_candidate_snapshot_matrix_2026-11-26.csv).

- 109 rows across four verified-open sessions: 15 (2026-04-24), 18 (2026-04-27), 21 (2026-04-28), 55 (2026-04-29).
- Invalidity: 88 OPEN_ABOVE_HIGH and 21 OPEN_BELOW_LOW.
- All 109 rows match the same-day ShareSansar daily-page snapshot exactly, including the invalid OHLC tuple.
- This establishes the invalid values were already present in the contemporaneous ShareSansar page capture, not just the later historical AJAX backfill.
- It does not establish the correct exchange OHLC. ShareSansar is a secondary source; all 109 remain quarantined as UNKNOWN. No raw data changed and no candidates were promoted.

## P4.27 — completed: 490 one-day date-shift audit

See [P4.27 report](p427_490_date_shift_audit_report_2026-11-26.md) and [490-row audit matrix](p427_490_date_shift_audit_2026-11-26.csv). CI passed in run [45865050524](https://github.com/jaljala044/nepse-smc-data/actions/runs/45865050524), artifact [15140301490](https://github.com/jaljala044/nepse-smc-data/actions/runs/45865050524/artifacts/15140301490). PR #40 is merged.

- 490/490 match the raw SMC row on the following date.
- 490/490 match the following-date ShareSansar page capture.
- 490/490 show the calendar pair `verified_open_observed → verified_closed`.
- No unresolved row-level mismatches; no raw file modified.

## Next priority target — P4.28: official per-security EOD validation

1. Resolve and validate the symbol-to-security-ID mapping for all unique symbols in the 490 shifted rows and the 109 invalid candidates.
2. Capture official NEPSE EOD payloads for the exact candidate dates (2026-03-01, 2026-07-24, 2026-04-24, 2026-04-27, 2026-04-28, 2026-04-29), within the official rolling history window.
3. Use the P4.23 strict capture validator; preserve original response bytes, endpoint, retrieval timestamp, security ID, date, row uniqueness and SHA-256.
4. Compare official rows against external candidate values and raw SMC values. For 109 invalid rows, do not repair any OHLC field without primary proof.
5. Where official rows cannot be retrieved or mappings are ambiguous, retain UNKNOWN / secondary-only status. Never promote by inference.

## Acceptance

P4.22 closeout is accepted when this report and the three referenced artifacts are retained, raw archives remain unchanged, all 87 conflicts are safely dispositioned, all 109 invalid rows remain quarantined, all 490 shifts are auditable, and the RHGCL derived value is clearly marked secondary-source corroborated rather than official.
