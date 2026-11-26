# P4.43 execution acceptance and quarantine disposition

**Status:** reproducible audit baseline and targeted corroboration workflows are passing; full historical adjudication and production acceptance remain **BLOCKED**.

**Pinned audit input:** `main` at `56362fb4f65b91fdcca8f50b50e53ad80e703649`.

## Current validated evidence

- Strict audit Run 205 (45899093388) passed all stages. The next current-head strict run 213 (45899542346) was still in progress at the time of this update; do not count it as passed until GitHub reports success.
- Priority floorsheet recovery Run 11 (45899542388) passed all 10 selected partitions.
- Secondary priority comparison Run 2 (45899542326) passed all five selected contract comparisons.
- The strict inventory covers 928 files: 784 structured files parsed, 138 inventory-only/unsupported, six non-JSON responses, 1,668,641 parseable records, zero file failures.
- Strict findings: 94,543 adjacent repeated OHLCV tuple pairs; 1,331 invalid-OHLCV flags (1,329 exact historical exception-register matches plus two non-equity instruments, KDBY and KEF); ten exact repeated JSON summary objects. After transaction-shape gating, zero trade-shaped missing-session flags and zero missing-trade-identity flags remain. Finding classes overlap and are not additive.
- The 58,972 evidence-review pairs were compared against pinned official per-security EOD history: 58,535 have no security/date capture on either side; 437 have only a previous-date HLCV/positive-execution match; zero have both dates matched. No rows were promoted.
- The 35,571 pair quarantine-review queue and 58,972 independent-evidence queue remain unresolved. Unique row holds from recorded closures and authenticated holiday listings total 28,476, but remain candidate holds pending security-specific adjudication.

## Targeted priority floorsheet evidence

Ten daily partitions for BNL, BNT, ENL and UNL passed download, Git blob/size, schema, date, arithmetic and target-row checks. Each selected symbol/date has one observed 10-share transaction at the expected rate. The exact rows and source hashes are preserved in `P443_PRIORITY_FLOORSHEET_CONTRACT_OBSERVATIONS_2026-11-27.csv`.

A second public archive comparison produced five exact matches for BNT (2026-06-29, 2026-07-01), UNL (2026-08-24) and ENL (2026-08-25, 2026-08-26), matching contract number, buyer/seller broker IDs, quantity, rate and amount. Evidence is in `P443_SECONDARY_PRIORITY_CONTRACT_EVIDENCE_2026-11-27.csv`.

Both archives remain third-party datasets. File completeness, independent upstream lineage and authoritative exchange provenance are unproven. All 15 observations remain `promotion_allowed=false`; none validates a complete OHLCV candle or authorizes canonical promotion.

The expanded full-session comparison passed for all **22** first-batch dates. Twenty-one sessions had exact parity across **1,664,647** contract rows. The 2026-04-10 session had 87,399 primary rows and 97,480 secondary rows: all primary rows matched, with **10,081 secondary-only rows** and zero primary-only rows. Those extra rows passed uniqueness and arithmetic checks but remain a source discrepancy; neither archive is established as complete or authoritative. Five secondary files had one leading apostrophe on numeric contract IDs; the parity check normalized 353,596 such IDs for comparison only and preserved source bytes. Timestamps and independent upstream lineage were not verified. Results are in `P443_FULL_SESSION_PARITY_BATCH01_2026-11-27.json`; row-level differences are in artifact 15155284907. No promotion was authorized.

The current strict workflow **Run 263 (45902069156)** passed all 32 steps, including bulk-recovery tests and a bounded first batch. The first batch validated 22 pinned daily partitions (1,752,046 trade rows, zero invalid rows) and checked 5,235 P2 security/date requests: 3,177 H/L/volume matches, 2,058 H/L/volume conflicts, and 63,538 requests without a matching pinned partition in this archive inventory. Among the available requests, high matched 5,074, low 3,365, and volume 5,018. Open/close, archive completeness and upstream independence remain unverified. No rows were promoted. Summary is in `P443_BULK_EQUITY_FLOORSHEET_BATCH01_2026-11-27.json`; row-level 68,773-row disposition and per-field flags are in strict workflow artifact 15155667000.

## Quarantine disposition (policy record, not full canonical-ingestion enforcement)

| Path | Git blob SHA | Rows | Repeated contract occurrences | Disposition |
|---|---|---:|---:|---|
| `reference/p433_floorsheets/floorsheet_2024-08-14.csv.gz` | `0dd938bc5e6bfd50fa09bf85f0836d443ab15983` | 244,019 | 219,615 | `BLOCK_CANONICAL` |
| `reference/p433_floorsheets/floorsheet_2024-08-18.csv.gz` | `49d6498b30681b7896b6c5c824b518e50f941d` | 300,918 | 270,825 | `BLOCK_CANONICAL` |

The pinned P4.33 capture report records 544,937 unique archive-local source record IDs and zero exact repeated rows. Repeated contract-number values are collisions, not confirmed duplicate exchange contract IDs. Preserve all rows; do not invent identifiers or substitute archive-local IDs for exchange contract IDs. The two P4.35 marketwide control responses share blob `732e3365b4304f7696a9d30dcd2e94451535caf8` and contain 2026-11-26 trades, not the requested 2024 dates; they are not historical evidence.

The scanner-preparation validator is fail-closed for the protected paths/fingerprints and validates supported daily/floorsheet inputs before publishing to a new output directory. It does not mutate source data, filter or repair rows, and is **not** a complete canonical-ingestion gate. Nested/cross-file canonical ingestion still needs explicit protection and tests.

## Outstanding acceptance items

1. Complete independent historical session, security-identity, execution and OHLCV adjudication for the repeat queues and invalid-price exceptions.
2. Complete date-shift/misdated-candidate reconciliation across the full 928-file scope; historical session evidence does not cover the entire 2011–2026 period.
3. Establish source provenance, file/session completeness and independent upstream lineage for the third-party floorsheet archives; absence from an archive is not proof of no trade.
4. Implement and test canonical-ingestion quarantine enforcement across nested and cross-file ingestion paths, or explicitly split that implementation into a separate tracked issue.
5. Validate complete-period point-in-time replay, monthly consumers, SMC/ICT and authentic IDPAT V3 requirements before enabling production scoring or recommendations.
6. Confirm strict CI after the latest report/decision refresh; Run 263 passed on the latest executable-code revision, and the report refresh will trigger another strict run.

No raw or canonical rows were changed, shifted, deleted, deduplicated, corrected or promoted. Production recommendations and training labels remain disabled. PR #80 remains draft and unmerged.
