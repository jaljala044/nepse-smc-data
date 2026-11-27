# P4.44 — 209-symbol repeated-pair identity reconciliation

Date: 2026-11-27  
Working branch: `p443-global-integrity-audit`

## Source and reproducibility

- Source workflow artifact: strict content audit, artifact ID `15193057360`, workflow run `45989435991`.
- Artifact ZIP SHA-256: `854749be4c7c01cb405dff747bed35821ea989bde1a0746df4704546bbc59017` (independently recomputed; matches the recorded digest).
- Matrix: `P444_UNCOVERED_REPEAT_PAIR_EVIDENCE_2026-11-27.csv`.
- Matrix SHA-256: `9193f99f1bd2e77949544a87b4c9d15b2c0be3bda81e574849296dff4139f0b8` (independently recomputed; matches the recorded digest).
- Matrix rows: 23,377; unique symbols: 209; unique pair IDs: 23,377; date span: 2024-03-05 through 2026-11-20.
- Reconciliation uses the matrix's explicit identity-scope and current-snapshot join fields. It does not infer identity from ticker similarity.

## Reconciliation result

| Scope | Symbols | Pair rows | Interpretation |
|---|---:|---:|---|
| Current-snapshot-only | 183 | 21,082 | A current security ID/name/status is joined; historical stable ID and effective interval remain absent |
| Unresolved | 26 | 2,295 | No current snapshot identity joined; keep the unresolved symbol set explicit |
| **Total** | **209** | **23,377** | All rows accounted for |

For the 183 current-snapshot-only symbols:
- 183 distinct current security IDs; no duplicate ID assignments in this matrix grouping.
- All joined snapshot status values are `A`.
- These are point-in-time snapshot associations, not historical ID verification.

The 26 unresolved symbols are:
`CMF1`, `CMF2`, `GBD80/81`, `HBLD83`, `JALPA`, `KLBSL`, `KLBSLP`, `LEMF`, `MKLB`, `MMFDB`, `NIBD2082`, `NICAD8182`, `NICAD8283`, `NICD83/84`, `NICGF`, `NLBBL`, `NMB50`, `SABSL`, `SAEF`, `SAMAJ`, `SBLD2082`, `SBLD83`, `SDLBSL`, `SFCL`, `SFCLP`, `SRD80`.

This set agrees in cardinality and membership with the existing 26-symbol residual reconciliation register. The register contains mixed instrument-class candidates and partial issuer/lifecycle leads, but it does not supply historical stable IDs. Even where a NEPSE-hosted notice supports a ticker/company or successor relationship, it does not establish the historical ID or last-trade boundary.

## Integrity and disposition checks

- All 23,377 rows have `source_pair_tuple_equal=true`.
- All 23,377 rows remain `HOLD_UNKNOWN_NO_INFERENCE`.
- `promotion_allowed=false` for every row.
- No historical stable ID is established by this reconciliation.
- No OHLCV, raw evidence, canonical, scanner-input or matrix source rows were modified.

## Conclusion / remaining acceptance gap

**Work package #3 is PARTIAL, not complete.** The current-snapshot reconciliation is now explicit and the 26-symbol unresolved set is verified. The acceptance criterion—effective-dated symbol/name/ID mapping for all 209 symbols—remains unmet because the available crosswalk/snapshot is point-in-time and does not include effective intervals or historical stable IDs. Do not release holds or promote repeated-pair rows based on this result.

Next dependency: obtain archived NEPSE security lists or official effective-dated security-ID history, then reconcile the 26 residual symbols (#4) and validate historical identity intervals across all 209 symbols.


## Successor-alias correction (2026-11-27)

The 26 symbols without a direct current-snapshot row are not all unresolved current identities. The lifecycle evidence ledger plus the 2026-11-25 NEPSE security snapshot establish five predecessor-to-successor current-identity links:

- JALPA → MATRI (current security ID 694)
- KLBSL → MATRI (current security ID 694)
- SABSL → SMPDA (current security ID 2896)
- SDLBSL → SMPDA (current security ID 2896)
- SAMAJ → GBLBS (current security ID 583)

The successor IDs are from the 2026-11-25 snapshot blob `eed3bbb3152e83d4abcb0ee8d03d720c33c63cef`. Full row-level mapping and evidence limits are in `P444_MERGER_SUCCESSOR_CURRENT_ID_CROSSWALK_2026-11-27.csv`. This updates the current-identity interpretation: 5 of the 26 residual predecessor symbols map to 3 current successor identities; 21 residual symbols still lack a supported successor/current mapping. Historical predecessor stable IDs remain unverified, and the SABSL/SDLBSL effective date remains disputed. Preserve predecessor OHLCV under the old ticker; use the successor ticker/current ID for current-security lookups only.
