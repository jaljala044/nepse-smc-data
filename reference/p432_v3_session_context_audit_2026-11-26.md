# P4.32 — v3 adjacent-repeat and session-context audit

Date: 2026-11-26  
Status: complete for the current v3 dataset; unknown session/corporate-action evidence remains explicit.

## Coverage

- 281 securities
- 246,238 derived OHLCV rows
- Adjacent-repeat and calendar diagnostics recomputed on v3 after the 11 P4.30 Open corrections
- No rows changed, repaired or deleted by this audit

## Adjacent identical OHLCV rows

| Classification | Rows |
|---|---:|
| Unclassified adjacent repeat | 52,891 |
| Closed-session repeat candidate | 18,910 |
| Open-session repeat review | 5 |
| **Total adjacent identical pairs** | **71,806** |

An identical adjacent OHLCV tuple is not automatically a zero-trade candle. The classifications reflect the current calendar evidence only. The 52,891 unclassified repeats must not be treated as confirmed closed sessions.

## Calendar alignment

| Flag | Rows |
|---|---:|
| Outside calendar evidence window | 166,733 |
| Row on verified closed date | 18,910 |
| **Total calendar flags** | **185,643** |

The 166,733 rows have unknown session status because the canonical calendar evidence does not cover those dates. They are not asserted to be open or closed. The 18,910 rows are candidates on dates marked closed by the current calendar and remain available for per-security reconciliation.

## Corporate actions and splits

- 3 corporate-action event records across 3 symbols.
- 278 securities have no corporate-action record in the current file. This is not evidence that they had no bonus, rights, split or other action.
- 1 split proposal remains without a verified effective date.
- No split factor or corporate-action price adjustment was applied by this audit.

## Files and validation

- Audit: `tools/audit_derived_ohlcv_v3_context.py`
- Tests: `tools/tests/test_audit_derived_ohlcv_v3_context.py`
- Outputs: `derived/ohlcv_v3/quality_audit/adjacent_repeat_flags.csv`, `calendar_alignment_flags.csv`, `corporate_action_coverage.csv`, `split_review_flags.csv`, and `context_audit_totals.json`.
- Successful CI run: [45871393740](https://github.com/jaljala044/nepse-smc-data/actions/runs/45871393740).

## Disposition

The v3 OHLCV release remains suitable only where the individual row has acceptable OHLCV and source evidence. The 1,368 historical invariant flags from P4.31 remain unresolved. Calendar gaps, repeat candles and corporate-action absence are not silently normalized.

## Next priority — P4.33

Start historical anomaly recovery in bounded, evidence-first batches. Prioritize AHPC (607 invariant flags), SKBBL (381), API (123), MERO (105), SPDL (73), CHL (48) and HIDCL (32). For each batch, classify exact dates into official-source-retrievable, historical-source-only, corporate-action review, or unresolved UNKNOWN. Do not repair any row unless a source proves the exact security/date/value.
