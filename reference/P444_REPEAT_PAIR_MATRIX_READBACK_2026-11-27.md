# P4.44 matrix artifact read-back verification

## Latest verification — workflow run 298

- Workflow run: 45989435991
- Workflow URL: https://github.com/jaljala044/nepse-smc-data/actions/runs/45989435991
- Workflow commit: 5b00a706c3e81513d41e71e67763f81554ba34dd
- Artifact: `p443-strict-content-audit` (ID 15193057360)
- Artifact ZIP SHA-256 (GitHub artifact digest): `854749be4c7c01cb405dff747bed35821ea989bde1a0746df4704546bbc59017`
- Matrix CSV: `P444_UNCOVERED_REPEAT_PAIR_EVIDENCE_2026-11-27.csv`
- Matrix CSV SHA-256 (downloaded artifact bytes): `9193f99f1bd2e77949544a87b4c9d15b2c0be3bda81e574849296dff4139f0b8`
- Read-back audit JSON SHA-256: `c1ef5ac69e7cfeecc4b056be68c1713edc5b99d4b23eeb5c3a14cbaba7273d64`

## Read-back results

- Rows: 23,377
- Distinct symbols: 209
- Distinct pair IDs: 23,377
- Date span: 2024-03-05 through 2026-11-20
- Every row has a 40-character source Git blob SHA and `source_pair_tuple_equal=true`.
- Every row disposition is `HOLD_UNKNOWN_NO_INFERENCE`.
- Every row has `promotion_allowed=false`.
- Identity scopes: 21,082 current-snapshot-only; 2,295 unresolved; 0 historically effective-dated stable IDs.
- Previous-date session evidence: 979 all-market-closed, 22,398 unknown.
- Current-date session evidence: 1,503 all-market-closed, 21,874 unknown.
- No per-security positive execution evidence was joined in this artifact.
- The workflow's independent read-back auditor returned `valid=true` and `issues=[]`.
- No canonical OHLCV data was changed.

## Interpretation

The artifact is complete for the specified 23,377-pair / 209-symbol scope and preserves all uncertainty. A market-closed flag is calendar evidence, not a historical instrument identity. Missing session or execution evidence is not evidence of no trade. The repeated tuple is not proof of a duplicate execution. This read-back validates matrix structure and safeguards; it does not adjudicate any pair or authorize promotion.

## Prior verification

- Workflow run: 45988011831 (run 295), commit: 253c120147ef70e3080a6d162231d7a64547e0df
- Artifact ID: 15192053831
- Artifact ZIP SHA-256: `60edb3058215189ea739b362641d7b756f6ca03e0cb42cb13299a4425ece930d`
- Matrix CSV SHA-256: `9193f99f1bd2e77949544a87b4c9d15b2c0be3bda81e574849296dff4139f0b8`

The matrix bytes are identical across the two artifact read-backs; run 298 independently reproduces the same 23,377-row result.
