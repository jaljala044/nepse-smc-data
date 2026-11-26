# P4.33 — historical OHLCV invariant evidence triage

Date: 2026-11-26  
Status: 1,368 historical flags classified; all remain UNKNOWN; no unsupported correction.

## Evidence coverage result

The v3 audit contains 1,368 remaining OHLCV invariant flags, all dated 2009–2020. The pinned primary-source coverage currently available does not reach these dates.

| Evidence source | Verified coverage | Flag rows covered |
|---|---|---:|
| Official NEPSE EOD rolling history | 365-day window begins 2025-11-26 | 0/1,368 |
| Pinned floorsheet archive | 226 daily files, 2025-11-25 to 2026-11-20 | 0/1,368 |
| Exact-date validated secondary history | No exact symbol/date record validated in this batch | 0/1,368 |
| Corporate-action records | No record matched any flagged symbol/date | 0/1,368 |

The floorsheet archive inventory is pinned to source commit `70324524df83eaa7c2964441ad4026d6ab00cc7e`. The inventory proves file presence for 226 dates only; it is not evidence of older floorsheet coverage or complete-session status for every date.

## All 1,368 rows remain UNKNOWN

| Field | Rows |
|---|---:|
| Official EOD outside current window | 1,368 |
| No pinned floorsheet file for date | 1,368 |
| No corporate-action record — not proof of none | 1,368 |
| Exact-date secondary history validated | 0 |
| Promoted or repaired | 0 |

Each row in the [1,368-row evidence disposition matrix](p433_1368_historical_invariant_evidence_triage_2026-11-26.csv) records symbol/date, invariant type, official-window status, floorsheet inventory status, corporate-action status, secondary-source status and final UNKNOWN disposition.

## Remaining flags by type

| Invariant | Rows |
|---|---:|
| OPEN_OUTSIDE_RANGE | 1,314 |
| CLOSE_OUTSIDE_RANGE | 28 |
| HIGH_BELOW_LOW | 22 |
| NONPOSITIVE_PRICE | 4 |
| **Total** | **1,368** |

## Largest symbol concentrations

| Symbol | Flags |
|---|---:|
| AHPC | 607 |
| SKBBL | 381 |
| API | 122 |
| MERO | 104 |
| SPDL | 72 |
| CHL | 48 |
| HIDCL | 32 |
| RADHI | 1 |
| UNHPL | 1 |

These are data-quality counts, not trading recommendations. No historical Open/High/Low/Close value has been inferred from the next day's row, adjusted by an unverified split factor, or copied from a secondary chart.

## Reproducibility

- Triage tool: `tools/triage_p433_historical_invariant_evidence.py`
- Tests: `tools/tests/test_triage_p433_historical_invariant_evidence.py`
- Pinned floorsheet coverage manifest: `reference/p419_observed_date_floorsheet_archive_inventory_2026-11-26.csv`
- Historical floorsheet validation report: `reference/p420_226_historical_floorsheet_validation_results_2026-11-26.md`
- Successful CI run: [45871850255](https://github.com/jaljala044/nepse-smc-data/actions/runs/45871850255)

## Disposition and next priority — P4.34

Do not attempt a bulk numerical repair from this evidence set. Start a bounded historical-source acquisition for AHPC and SKBBL first, then API, MERO and SPDL. For every exact symbol/date, compare available ShareSansar, Merolagani, NepseAlpha or other archived OHLCV with the raw source and any corporate-action record. Require exact date and security identity, independent corroboration where possible, and a provenance record. If no source is retrievable or sources conflict, retain UNKNOWN.
