# P4.22 — External-provider OHLCV reconciliation correction and source audit
Date: 2026-11-26

## Executive decision

This report corrects the earlier summary that stated 1,000 OHLCV conflicts and 656 missing traded-symbol rows. Those two figures are not supported by the current repository's reproducible reconciliation runs and must not be carried forward as validated counts.

| Scope | Reproducible result | Interpretation |
|---|---:|---|
| Equity universe | 281/281 compared; no source files missing | Coverage of this pinned external archive only |
| Raw SMC rows | 246,129 | Source archive rows |
| Pinned external rows | 433,183 | Secondary external archive rows |
| Same-date exact matches | 173,548 | Exact five-field OHLCV matches |
| Same-date value conflicts | 87 | Quarantine; do not choose a side automatically |
| External-only dates within raw span | 599 | Candidate rows, not automatically valid missing trades |
| Date-shift candidates already recovered in provisional derived view | 490 | Raw sources unchanged |
| Invalid external candidate rows | 109 | Quarantined |
| External rows inserted into derived archive | 0 | No unsupported insertions |
| Provisional derived output | 172,794 rows | Source-matched provisional, not scanner-approved |

The 599-candidate disposition is 490 date-shift recoveries + 109 invalid external OHLCV quarantines. The workflow reports remaining=109 and inserted=0. This is not a count of 656 verified missing trades.

The separate pairwise repository audit covers 23 divergent archive pairs and 13,518 common dates. It found one numeric OHLCV mismatch: RHGCL on 2026-11-19. That is not the same metric as the 87 conflicts found in the broader 281-equity raw-versus-external archive comparison. The 1,329 OHLC invariant flags are also a different category from value conflicts.

## RHGCL 2026-11-19: secondary-source corroboration

SMC raw row: O 252.10, H 259.50, L 252.10, C 256.00, V 4,216.
History-starter row: O 252.10, H 259.50, L 252.10, C 258.00, V 9,054.
ShareSansar-derived daily archive: O 252.10, H 259.50, L 252.10, C 258.00, V 9,054.

Additional public source checks:
- Hamroshare RHGCL historical technical page lists the 2026-11-19 row as 252.10 / 259.50 / 252.10 / 258.00 / 9,054. https://hamroshare.com.np/company/RHGCL/technical
- Stock Nepals RHGCL historical price table lists the same row and volume. https://www.stocknepals.com/stock-details/RHGCL
- NEPSE Demo Trading RHGCL history lists close 258.00 and volume 9,054 for 19 Nov. https://nepsedemotrading.com/stocks/RHGCL
- QuantNepal RHGCL history lists close 258.00 and volume 9,054 for 19 Nov. https://www.quantnepal.com/nepse/RHGCL
- Punji RHGCL page confirms 25 Nov 2026 current data and monthly aggregate data; the public page evidence retrieved here does not expose the exact 19 Nov daily row. https://punji.app/stocks/RHGCL
- Merolagani exposes datewise share-price and floorsheet search interfaces, but the public page retrieval in this run did not return the exact RHGCL 19 Nov row. https://merolagani.com/StockQuote.aspx and https://merolagani.com/Floorsheet.aspx
- NEPSE Alpha exposes a historical-price export interface, but the public retrieval in this run did not return the exact RHGCL 19 Nov row. https://nepsealpha.com/nepse-data/

### Decision

The history-starter / ShareSansar-derived value is supported by at least three additional public secondary displays (Hamroshare, Stock Nepals, NEPSE Demo Trading), and agrees with QuantNepal. This is strong secondary corroboration for Close=258.00 and Volume=9,054. It is not an authenticated NEPSE raw payload or a primary-source floorsheet proof.

- Keep SMC raw OHLCV unchanged.
- Keep history-starter raw OHLCV unchanged.
- Record the RHGCL row as SECONDARY_SOURCE_CORROBORATED_PRIMARY_CONFIRMATION_PENDING.
- A versioned derived correction may use the history-starter/ShareSansar value only with its provenance and non-primary status attached.
- Do not promote the row to fully canonical until primary exchange data or a complete, date-matched floorsheet reconciliation is captured.

## Provider access and lineage

| Provider | Publicly verifiable capability | Evidence in this run | Limitation / policy |
|---|---|---|---|
| NEPSE Alpha | Historical price export UI with daily/weekly/monthly filters and OHLCV/turnover columns | Interface and current index history visible | Exact RHGCL 2026-11-19 record not retrieved; no authenticated raw payload captured |
| Merolagani | Datewise share-price and datewise floorsheet interfaces | Both public interfaces confirmed | Exact RHGCL row not retrieved; floorsheet pagination/completeness not established |
| Hamroshare | Methodology says price history is NEPSE end-of-day data; raw/adjusted chart modes are distinguished | Exact RHGCL 2026-11-19 OHLCV row visible in search result | Secondary display of NEPSE-origin data; not independent of NEPSE upstream |
| Punji | Terms say data is sourced from public NEPSE endpoints; stock page provides daily latest and monthly aggregate views | RHGCL page and terms inspected | Exact 19 Nov row not exposed; terms prohibit systematic extraction/redistribution, so do not build a scraper or mirror from Punji |

Do not count four sites as four independent sources when they share NEPSE or another upstream provider. Persist provider lineage, exact URL, retrieval time, source payload hash where available, adjusted/unadjusted basis, and evidence tier.

## Why 599 candidate rows are not verified missing trades

The existing reconciliation code identifies external-only rows within the raw archive date span. It does not establish that each row is a verified executed trade. It then compares candidates with the derived output and classifies:
- 490 ALREADY_RECOVERED_DATE_SHIFT: represented in the provisional derived series at a calendar-justified target date and matching the external value.
- 109 QUARANTINE_INVALID_EXTERNAL_OHLCV: external candidate row fails numeric/OHLC validity.

The recovery workflow explicitly reports zero inserts. No new historical bar was added by that run.

## Unresolved work queue

1. Reconcile the 87 same-date value conflicts individually against date-matched NEPSE official EOD data and complete floorsheets. Keep both source values until evidence chooses a result.
2. Investigate the 109 invalid external candidates; retain raw source values and quarantine. Do not infer corrected OHLCV.
3. Audit all 490 date-shift decisions against the exact exchange session calendar and source timestamps. A shifted derived date is not permission to alter a raw date.
4. Obtain date-scoped NEPSE Alpha and Merolagani records for conflict cases. For Punji, use only permitted manual/public display verification; no systematic scraping or redistribution.
5. Keep Hamroshare raw-vs-adjusted price basis explicit and check corporate actions before using a series for return calculations.
6. For absent symbols, NO_TRADE remains forbidden unless verified-open session + complete floorsheet + exact file hash + completeness evidence all pass. Otherwise use UNKNOWN.

## CI evidence

- Equity external reconciliation: https://github.com/jaljala044/nepse-smc-data/actions/runs/45845443879
- Missing equity recovery: https://github.com/jaljala044/nepse-smc-data/actions/runs/45846116991
- Provisional market equity build: https://github.com/jaljala044/nepse-smc-data/actions/runs/45845805778

All three runs completed successfully. Outputs are provisional/review-only, not canonical scanner data.

## Final disposition

- 1,000 conflicts: unsupported by current run evidence; replace with 87 same-date value conflicts in the external archive comparison, plus one numeric mismatch in the separate 23-pair repository comparison.
- 656 missing traded-symbol rows: unsupported by current run evidence; replace with 599 external-only candidates, of which 490 were already reconciled as date shifts and 109 invalid external candidates remain quarantined. Zero rows were inserted.
- RHGCL 2026-11-19: secondary-source corroborated; primary confirmation pending.
- Canonical promotion / model training / BUY scoring remains blocked for rows lacking complete provenance, session/floorsheet validation, and corporate-action/price-basis clearance.