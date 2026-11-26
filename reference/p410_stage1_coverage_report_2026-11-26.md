# P4.10 — 281-equity Stage 1 evidence coverage matrix (2026-11-26)

## Disposition

**NOT READY FOR STAGE 1 PROMOTION.** This is an evidence inventory, not a BUY scan or canonical-data admission.

The supplied universe target is **281 equities**, but the current candidate register contains **278 rows classified as Equity** plus 47 Mutual Fund rows (325 rows total). The three-security difference is unresolved. No symbols are fabricated to fill the gap. The attached matrix covers all 278 identifiable current Equity candidates; the 281-target reconciliation remains OPEN.

## Reproducible source inputs

- `reference/nepse_target_universe_candidates_2026-11-26.csv` — 325 rows: 278 Equity candidates and 47 Mutual Fund rows; all 278 Equity rows are labelled `current_candidate_not_lifecycle_verified`.
- `reference/nepse_security_id_snapshot_2026-11-25.csv` — 573 instrument rows, with current security IDs/status; this is a snapshot, not an effective-dated lifecycle master.
- `reference/nepse_ohlcv_active_instrument_crosscheck_2026-11-26.csv` and `reference/nepse_ohlcv_current_company_list_comparison_2026-11-26.csv` — 525 OHLCV-file symbols cross-checked against captured current lists.
- `reference/nepse_session_calendar_2026.csv` — official holiday/closure evidence; it is not a complete per-security positive-open-session calendar.
- `reference/nepse_primary_observed_open_sessions_2025-2026.csv` — 225 observed positive-trade dates for one captured security ID (8108); not a 281-security calendar.
- `reference/third_party_full_session_floorsheet_candidate_audit_2026-11-26.md` — 2026-11-20 third-party file is internally consistent but not independently proven complete; absence cannot establish NO_TRADE.
- `reference/shareSansar_source_corroboration_ohlc_flags_2026-11-26.md` — 13 sampled OHLC invariant violations match the ShareSansar-derived archive; retain anomalies, do not auto-correct.

## Coverage summary

| Dimension | Current evidence | Status |
|---|---|---|
| Universe identity | 278 Equity candidates carry snapshot IDs; cross-checks match captured current list | Partial pass for current identity only |
| Listing/lifecycle | All 278 candidates still labelled not lifecycle verified | UNKNOWN |
| Daily sessions | Holiday calendar exists; per-security open-session and no-trade reconciliation is incomplete | UNKNOWN |
| Floorsheet | One full-session third-party candidate audited; completeness not authenticated across dates/universe | UNKNOWN |
| OHLCV files | 278/278 candidates have a symbol-named file in the candidate register | File presence only |
| OHLCV provenance | Historical rows lack complete admitted row-level provenance/finality/available-at contract | UNKNOWN |
| OHLC anomalies | 1,329 structural invariant flags reported in audit; 13 sampled rows source-corroborated | Preserve and quarantine unresolved rows |
| Corporate actions | No per-security cleared event register linked to price basis in this matrix input set | UNKNOWN |
| Price basis | No per-row adjusted/unadjusted action-chain clearance | UNKNOWN |
| Liquidity | No validated per-security turnover/trade-frequency/spread/depth gate evidence | UNKNOWN |
| Overall Stage 1 | Required hard gates are not all PASS | BLOCKED |

## Interpretation rules

- `PRESENT_FILE_ONLY` is not a valid OHLCV data-quality pass.
- `PASS_CURRENT_ID_MATCH` means only that the candidate security ID matches the captured current snapshot. It does not prove listing date, historic symbol continuity, or lifecycle.
- `UNKNOWN` is not equivalent to FAIL or NO_TRADE. A zero-trade conclusion requires a verified open session and a demonstrably complete floorsheet.
- Corporate-action clearance and price-basis clearance must be explicit, effective-dated and linked to the affected OHLCV rows.
- Liquidity is not inferred from file presence or occasional volume.

## Per-security matrix

See `reference/p410_stage1_coverage_matrix_2026-11-26.csv` (278 symbol-level records). Each row includes current identity match, listing/lifecycle, session/floorsheet, OHLCV provenance/anomaly, corporate action, price basis, liquidity, blockers and next acquisition task.

## Required next actions (ordered)

1. **Resolve the 281 vs 278 universe discrepancy.** Reconcile the prior 281-equity structural-audit roster against the 278 current Equity candidates. Determine whether the three are omitted active equities, lifecycle-changed securities, or prior misclassifications. Keep them as unresolved slots until symbols and source records are evidenced.
2. Capture an effective-dated NEPSE instrument master plus listing/delisting/rename notices and map stable security IDs over time.
3. Build the per-security expected session calendar from verified NEPSE open-session evidence; reconcile each symbol/date to official price-volume history and complete floorsheet evidence. Preserve UNKNOWN where source completeness is not established.
4. Admit OHLCV rows only with source URL/endpoint, raw payload SHA-256, retrieval timestamp, `available_at`, finality, stable security ID, date, and explicit adjusted/unadjusted price basis.
5. Reconcile bonus, rights, split, merger and other corporate actions using NEPSE/CDSC notices; never back-adjust without a documented event and factor.
6. Compute liquidity only from validated trades and reliable market data; report turnover, active-session ratio, trade frequency and spread/depth coverage. Missing depth remains UNKNOWN.
7. Re-run the Stage 1 gate over the completed matrix. No BUY eligibility until every required hard gate is PASS and the evidence quality threshold is met.

## Data quality

**LOW CONFIDENCE for Stage 1 eligibility.** Source artifacts are useful discovery/reconciliation inputs, but do not yet provide a complete, point-in-time, per-security evidence chain. This report deliberately does not convert missing evidence into neutral scores or eligibility.
