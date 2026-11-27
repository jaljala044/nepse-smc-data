# P4.44 — repeated-pair matrix schema and execution-evidence audit

Date: 2026-11-27  
Branch: `p443-global-integrity-audit`

## Pinned artifact

- Workflow run: `45989435991`
- Artifact ID: `15193057360`
- Matrix: `P444_UNCOVERED_REPEAT_PAIR_EVIDENCE_2026-11-27.csv`
- Matrix SHA-256: `9193f99f1bd2e77949544a87b4c9d15b2c0be3bda81e574849296dff4139f0b8`
- Rows / symbols / unique pair IDs: 23,377 / 209 / 23,377.

## Work package #12 — matrix expansion

The matrix has 36 columns and contains:
- source path, source Git blob SHA, previous/current source row numbers and tuple-equality flag;
- identity scope, historical stable-ID slot, current-snapshot ID/status/name and instrument-class candidates;
- previous/current session evidence status and source fields;
- previous/current per-security execution evidence source, security ID, trade count, quantity, value and retrieval-time fields;
- disposition and promotion gate.

All 23,377 rows have source row identifiers, source blob SHA and `source_pair_tuple_equal=true`. All rows retain `HOLD_UNKNOWN_NO_INFERENCE` and `promotion_allowed=false`.

**Limitation:** the per-security execution fields are present structurally but empty on all 23,377 rows. Historical stable IDs are also empty on all 23,377 rows. Current-snapshot IDs are populated on 21,082 rows only.

**Work package #12 is PARTIAL:** matrix schema and source-row/session/identity slots are present and read-back validates, but per-security execution evidence and historical stable IDs are not joined.

## Work package #11 — per-security execution evidence

A direct null-count audit of all ten previous/current execution fields found:
- previous execution source, security ID, trade count, quantity and value: 0/23,377 populated;
- current execution source, security ID, trade count, quantity and value: 0/23,377 populated.

Therefore no positive per-security execution payload is joined to either endpoint date for any repeated pair. Market-wide session status is not a substitute for security-level execution evidence. Missing execution evidence is not proof of no trade.

**Work package #11 remains BLOCKED.** It requires date-matched primary execution payloads joined through verified historical security identity. No row can be promoted from the current artifact.

## Data safety

This audit read the downloaded artifact only. It did not modify raw captures, OHLCV, canonical data, lifecycle ledgers, scanner inputs or the source matrix. No disposition or promotion flag changed.
