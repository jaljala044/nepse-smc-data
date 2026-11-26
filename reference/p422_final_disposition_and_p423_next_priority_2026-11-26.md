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
| RHGCL 2026-11-19 | SMC raw 252.10 / 259.50 / 252.10 / 256.00 / 4,216; ShareSansar-derived, history-starter and multiple secondary displays agree on 252.10 / 259.50 / 252.10 / 258.00 / 9,054 | Preferred derived value finalized at Close 258.00, Volume 9,054, evidence tier SECONDARY_SOURCE_CORROBORATED; preserve SMC raw row |
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

The official NEPSE website was checked, but its public page was returned as a JavaScript shell without readable historical rows in this retrieval. NEPSE's official EOD endpoint is documented by the independently maintained capture pipeline as authoritative and limited to a rolling 365-day history window. The 19 November 2026 date is inside that window, but an authenticated NEPSE payload was not captured in this run.

The repository's 19 November floorsheet CSV contains only 500 contracts (one page), not a complete session capture. It contains two RHGCL prints totalling 480 shares at 258.00, which corroborates the price but cannot prove the full 9,054-share daily volume.

**Decision:** use 258.00 / 9,054 in a versioned derived view with `SECONDARY_SOURCE_CORROBORATED_PRIMARY_CONFIRMATION_PENDING`. Keep the original SMC raw row unchanged. Do not label this record official-NEPSE-verified, and do not use the row as a primary-source training label.

## 86 historical conflicts — why UNKNOWN is the correct result

The other 86 conflicts are concentrated on 2025-07-28. The external historical archive identifies ShareSansar as its source, not NEPSE directly. NEPSE's official EOD history endpoint has a rolling 365-day limit; as of 2026-11-26, 2025-07-28 is outside that window. No authenticated official historical payload was recovered for these rows.

All 86 are therefore explicitly quarantined from canonical scoring and training as `UNKNOWN_SOURCE_CONFLICT`. This is a completed risk-control disposition, not a fabricated resolution of their prices. Future evidence may promote individual rows only after symbol/date/price-basis and corporate-action checks.

## 109 invalid candidates — investigation result

The full 109-row recovery queue was inspected. Every row fails the OHLC envelope because either the open is above the high (88 rows) or the open is below the low (21 rows). No row has a non-positive price, non-positive volume, high-below-low condition, or close outside the high/low range. The values remain in the quarantine artifact; no OHLC field is rewritten.

## 490 date shifts — audit result

All 490 entries are one-calendar-day offsets and split into two uniform batches:

- 238 records: raw date 2026-03-02 → derived target 2026-03-01. Sunday 1 March was a valid session under NEPSE's Sunday–Thursday trading week.
- 252 records: raw date 2026-07-25 → derived target 2026-07-24. Friday 24 July was a valid session under the Monday–Friday schedule introduced in April 2026.

The recovery artifact classifies all 490 as `ALREADY_RECOVERED_DATE_SHIFT`; each external value matches the existing derived row at the target date. No rows were inserted. Raw source dates remain unchanged, and the shifted date is retained only in the derived decision ledger with its provenance.

## Reproducible artifacts

The following immutable GitHub Actions artifacts contain the row-level evidence used for this closeout:

| Artifact | Run | Artifact ID | Contents |
|---|---:|---:|---|
| Equity external reconciliation | 45845443879 | 15132056272 | 87 conflict rows, 599 candidate rows, per-symbol summary and hashes |
| Missing equity recovery | 45846116991 | 15132011878 | 490 recovered date shifts and 109 invalid quarantine rows |
| Provisional market equity build | 45845805778 | 15131697026 | Per-row decision ledger and provisional derived OHLCV files |

The artifacts are review-only. They do not constitute a primary-source confirmation or authorize mutation of raw source archives.

## P4.23 — next priority target

**Build the official NEPSE EOD evidence adapter and primary-source reconciliation gate.**

1. Capture the 2026-11-19 RHGCL official EOD row while it remains inside NEPSE's rolling 365-day window; persist the raw response, retrieval timestamp, source URL, payload hash, upstream total count and parsed row.
2. Reconcile official EOD OHLCV against the two RHGCL source rows and the incomplete floorsheet capture. Promote only after identity, session, corporate-action basis and volume checks pass.
3. Add row-level evidence export for all conflict/quarantine classes, with deterministic reason codes and immutable source hashes.
4. For 2025-07-28, do not promise an official re-fetch: retain the 86 UNKNOWN rows unless a permitted historical primary record is supplied or found.
5. Add tests proving no secondary-only row is silently labelled official and no UNKNOWN row becomes NO_TRADE.

## Acceptance

P4.22 closeout is accepted when this report and the three referenced artifacts are retained, raw archives remain unchanged, all 87 conflicts are safely dispositioned, all 109 invalid rows remain quarantined, all 490 shifts are auditable, and the RHGCL derived value is clearly marked secondary-source corroborated rather than official.
