# NEPSE AI autonomous engineering work log — 2026-11-26

## Scope

This run resumed from the current GitHub repositories and the 2026-11-26 handover package. It selected a bounded, read-only data-integrity task: re-check the current OHLCV repository inventories and protect the seven user-finalized OHLCV rows with an automated regression test. No production signal behavior or raw market data was changed.

## Work completed

### 1. Current cross-repository OHLCV inventory re-check

Pinned current main-branch snapshots inspected:

- `jaljala044/nepse-smc-data`: `03180b8b581eaa78fe51f68d38d070aabc3106f1`
- `jaljala044/nepse-history-starter`: `2bd6976cbbb0d40cf60f77c0f712e0b708dc4dbe`

Results for `03_stock_charts_ohlcv/`:

- 525 CSV files in each repository.
- 525 matching filenames; no file exists in only one of these two directories.
- 500 matching Git blob IDs and 25 differing blob IDs.
- No `NICEF_OHLCV.csv` in either directory.
- The 25 differing files are: AHPC, API, BGWT, CHL, HDHPC, HIDCL, HLI, HRL, KDBY, KEF, MEHL, MEL, MERO, NIFRA, NRIC, RADHI, RAWA, RHGCL, SKBBL, SMJC, SOHL, SPDL, UAIL, ULHC, UNHPL.

This is a file-manifest comparison, not a full row-level reconciliation of all 25 files. Different Git blobs do not by themselves prove different OHLCV rows. The earlier 2026-11-24 exception ledger remains separate: 1,331 invalid-OHLC rows plus 8 cross-source conflict keys (1,339 exception records), all still quarantined. No automatic repair or promotion is authorized.

The accessible 525-file inventory does not establish the target universe. It includes mixed instrument classes and must not be treated as 281 active equities plus 47 mutual funds.

### 2. Seven user-finalized OHLCV rows re-read

Fetched the exact dated rows from the current `nepse-smc-data/main` CSV files. All seven match the user-finalized project values:

| Symbol | Date | Open | High | Low | Close | Volume |
|---|---|---:|---:|---:|---:|---:|
| BGWT | 2025-07-28 | 824.56 | 870.18 | 818.77 | 839.62 | 14,028 |
| MEHL | 2025-07-28 | 471.10 | 480.50 | 460.00 | 475.63 | 29,753 |
| RAWA | 2025-07-28 | 796.00 | 811.00 | 780.30 | 796.90 | 3,165 |
| RHGCL | 2025-07-28 | 346.70 | 362.00 | 341.40 | 357.05 | 296,715 |
| ULHC | 2025-07-28 | 509.00 | 515.00 | 495.00 | 510.75 | 32,288 |
| API | 2026-11-19 | 331.00 | 334.20 | 330.00 | 331.80 | 105,340 |
| HRL | 2026-11-19 | 483.00 | 488.00 | 483.90 | 483.90 | 49,184 |

The same dated rows in `nepse-history-starter/main` retain alternate source observations. They were not overwritten. This separation is intentional: source snapshots remain immutable, while the project-finalized values are retained in `nepse-smc-data`.

Important evidence distinction:

- For the five 2025-07-28 records, the official primary capture attempt did not produce usable dated price evidence: the today-price endpoint returned HTTP 500 for the old date, per-security history returned an empty collection outside the observed retention window, and the tested company-floorsheet route returned HTTP 403. Secondary MeroLagani LTP and ShareSansar-derived daily-board values differ in close-field semantics. Keep the user-finalized rows as project inputs, but do not label them independently exchange-verified.
- For HRL 2026-11-19, the user-finalized project row has Low=483.90. A captured NEPSE official EOD response reports Low=480.00 and matches the alternate history-starter row. Preserve the user-finalized row as instructed, retain the official observation separately, and keep the record out of canonical training pending an explicit adjudication/price-basis review.
- For BGWT 2025-07-28, the user-finalized chart values and secondary unadjusted LTP observations differ materially. An adjusted/unadjusted basis difference is a hypothesis only; the adjustment factor and corporate-action basis remain unverified.

### 3. Added a regression guard and verified it in CI

On branch `test/user-finalized-ohlcv-regression-2026-11-26`:

- Added `test_user_finalized_ohlcv.py`. It uses exact Decimal comparisons, requires one row per symbol/date, checks the CSV header, and protects all seven user-finalized OHLCV+volume tuples.
- Updated `.github/workflows/nepse-reference-validation.yml` to include the new test file in path filters and run it with the existing reference/calendar tests.
- The test is explicitly a project-input regression guard, not a claim of official NEPSE verification.

GitHub Actions run **45761564074** completed successfully: **17 tests passed, 0 failed** (9 reference-data tests, 6 session-date tests, 2 user-finalized OHLCV regression tests).

Branch commits:
- `f3da2c4ea1de84e8b0a70705fd94a8ae737fe89f` — add regression test.
- `e5f68749bf88a310769c7a202a2854def69eb442` — update CI workflow.

No production OHLCV row was changed by this work unit. No data was promoted to canonical training.

## Current evidence-backed backlog state

| Area | Status | Evidence / limitation |
|---|---|---|
| Target universe: 281 equities + 47 mutual funds | **Blocked / unverified** | Current NEPSE stock-list snapshot supports 7/7 symbol-presence checks only; it does not provide the full stable-ID, instrument-type and effective-lifecycle register. The `Nepse-master-data` repository currently contains only README.md. |
| NICEF file | **Missing in inspected OHLCV trees** | No NICEF CSV in either 525-file directory. Do not infer whether it is in-scope until the dated instrument register is available. |
| 2026 session calendar | **Partial** | 41 official holiday-API closure records (40 verified_closed, 1 verified_exceptional_closed); no open-session dates. Not a complete historical calendar. |
| 120-day / one-year OHLCV readiness | **Unverified** | File-level manifests exist, but there is no verified session calendar plus 281+47 dated universe to calculate per-security expected coverage. |
| Floorsheet archive candidate | **Metadata-only / blocked for ingestion** | The Hugging Face candidate is documented as a 759-MB floorsheet folder covering 2024-01-02 through 2026-08-26. Viewer/schema notes show contract numbers must be treated as strings and the time column appears null. Full raw-file acquisition and row-level validation were not completed. |
| Other floorsheet archives | **Partial** | SocrateAI has 661 dated files and SamirWagle 179 in the inspected manifests. The 2026-11-24 sample reconciles 52,369 shared contracts, 18 SocrateAI-only contracts, zero Samir-only contracts and zero shared-row field conflicts; this is one-day evidence only. Source lineage and reuse rights remain open. |
| 1-year / 6-month floorsheet windows | **Unverified** | Current report counts are 228/179 one-year date files (157 shared) and 115/119 six-month date files (107 shared). These are filenames, not confirmed sessions or per-security completeness. |
| OHLCV exceptions | **Quarantined** | 1,331 invalid OHLC rows and 8 cross-source conflict keys remain unresolved in the 2026-11-24 exception ledger. |
| Broker/floorsheet identity | **Partial** | A one-day 91-code directory-number crosswalk exists, but effective-dated legal-entity identity and source rights are not established. |
| Scanner no-lookahead | **Partial / integration gap** | A point-in-time helper filters on `available_at <= decision_time`, but the current `/v1/scan` route filters by candle date only. The route does not demonstrate enforcement of source-availability timestamps or session-close cutoffs. |
| IDPAT, SMC/ICT, multi-layer scanner, footprint memory, relationship layer, prediction tracking, backtesting, frontend/backend integration | **Partial / unverified end-to-end** | Modules and phase artifacts exist, but current repository evidence does not establish a fully integrated, validated, production-safe pipeline. Keep signals disabled. |
| Live providers / deployment | **Blocked / unverified** | Licensed credentials, server allowlisting, production database/provider integration and deployment validation are not established. |

The >1-GB Google Drive ZIP was not accessible in this workflow and was not inspected or imported.

## Related P1 capture status

In `jaljala044/nepse-elite-ai-scanner-pro`, PR #12 (`Fix P1 NEPSE conflict response classification`) remains open and draft. Its capture workflow now commits evidence to its dispatch branch rather than main. The 2026-11-25 capture run passed its capture regression tests, acquired and archived responses, and uploaded an artifact, but the final gate correctly failed because 2 conflict records remained partial/unresolved. The artifact is retained; this is a fail-closed evidence result, not a successful full reconciliation. The latest PR head has no reported combined status checks in the inspected status response.

## Next actions

1. Obtain a permitted primary NEPSE/SEBON instrument-register response with stable security IDs, instrument types and effective listing/suspension/delisting dates. Preserve raw bytes, retrieval time and SHA-256. Do not use the ShareHub schema description as canonical data.
2. Reconcile the 25 differing OHLCV file pairs row-by-row at pinned commits; retain both source observations and attach the existing invalid/conflict ledger.
3. Expand primary calendar evidence beyond 2026 closure records; do not infer open sessions from weekdays.
4. Complete corporate-action and price-basis review for the seven user-finalized records, especially the BGWT basis question and the HRL official Low discrepancy.
5. After the dated universe and calendar exist, calculate per-security coverage for 120-day, one-year and longer windows, distinguishing no-trade, suspended, pre-listing, delisted and unresolved.
6. Wire availability-time and session-close validation into the actual scanner request path before any historical signal replay or model training.
7. Acquire and parse the floorsheet archive only after source-lineage and reuse-rights review; preserve contract IDs as strings and missing timestamps as null.

## Safety / disposition

This branch changes only tests, CI test wiring and this work log. It does not modify production market data, enable trading signals, or authorize data promotion. Keep all unresolved rows quarantined and preserve source-specific copies.
