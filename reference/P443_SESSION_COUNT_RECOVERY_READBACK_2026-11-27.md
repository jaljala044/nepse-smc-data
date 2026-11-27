# P4.43 session-count recovery — artifact read-back (2026-11-27)

## Scope and execution

The dedicated **P443 session count recovery** workflow completed successfully on the current branch head:

- Commit: `880c2d9646d5e4334588b45de500faf0715fdd7d`
- Run: [45999394434](https://github.com/jaljala044/nepse-smc-data/actions/runs/45999394434)
- Run conclusion: `success`
- Pinned ShareSansarScraper source commit: `524442d518d2f2705ade0680c9d2e3f90738e3d6`
- Artifact ID: `15196818658`
- Artifact ZIP SHA-256: `379351b7d7a152de3dbd9aa2bf552cfdcffe7db2c56f8cecebc372d45eca1fde`
- CSV SHA-256: `12ccf192e9f4b4bfa1ed156ee0aaa1cd559fa69490e7958dd44f0d7e020a89e0`

The downloaded artifact was independently opened and read back. It contains 149 session rows, from 2026-01-01 through 2026-09-09.

## Read-back result

| Classification | Sessions |
|---|---:|
| Candidate totals match the pinned baseline | 148 |
| Baseline totals conflict | 1 |
| Total | 149 |

All 149 rows have `publication_allowed=false`. The workflow reports `promoted=0`.

### Isolated conflict: 2026-03-01

The recovered source partition contains:

- 13 symbols
- 364,868 quantity
- NPR 65,246,109.50 turnover
- 30 transactions

The independent published market summary for 2026-03-01 reports 341 companies, 13,193,462 shares, 55,206 transactions and NPR 5,648,319,041.36 turnover ([Ratopati, 2026-03-01](https://english.ratopati.com/story/51155/nepse-rises-by-072-percent)). This confirms that the recovered 13-symbol partition is not a complete session representation. The discrepancy is substantial and must not be treated as a small rounding or symbol-name difference.

**Disposition:** keep 2026-03-01 as `BASELINE_TOTALS_CONFLICT`; do not patch totals, infer missing rows, or promote the partition. Locate the exact missing/partial-source cause and recover the full session from a separately authenticated source before any use.

## Five active work items advanced in this pass

1. **Current-head workflow verification:** confirmed the narrow recovery workflow succeeded on the current branch head, not merely on an older commit.
2. **Artifact integrity/read-back:** downloaded and opened the run artifact; recorded ZIP and CSV SHA-256 values.
3. **149-session classification:** independently checked row count, date span, status distribution and publication gate.
4. **Conflict isolation:** identified 2026-03-01 as the sole conflict and compared its values with an independent contemporaneous published summary.
5. **Lifecycle-source queue review:** rechecked the residual lifecycle ledger and secondary-source leads. No newly authenticated NEPSE primary document with raw-byte provenance or historical stable ID was established; all 26 residual symbols therefore remain `HOLD_UNKNOWN`.

## Limits and next action

This is a session-count recovery result, not a completed P4.43 or P4.44 acceptance. The successful run is the dedicated session-recovery workflow; the latest full global-integrity workflow success still belongs to an earlier commit and does not validate the current branch head. The 23,377 repeat pairs remain unadjudicated, historical effective-dated stable IDs remain 0/26, and no canonical OHLCV rows or dates were changed.

Next: investigate the 2026-03-01 source partition defect; independently validate the other 148 matching sessions against their underlying source completeness; continue obtaining primary lifecycle documents and historical stable-ID intervals.