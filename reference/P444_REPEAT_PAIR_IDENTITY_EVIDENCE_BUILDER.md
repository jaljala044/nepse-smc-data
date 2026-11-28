# P4.44 repeat-pair identity evidence builder

The script `tools/audit_p444_repeat_pair_identity_evidence.py` builds a review
matrix from three explicitly supplied CSV exports:

- repeat-pair findings, including source path/blob/row identity;
- a rights-cleared, effective-dated security master;
- rights-cleared per-security execution evidence.

Example:

```bash
python tools/audit_p444_repeat_pair_identity_evidence.py \
  --repeat-pairs /evidence/repeat_pairs.csv \
  --security-master /evidence/security_master.csv \
  --executions /evidence/security_executions.csv \
  --output data/reports/p444_repeat_pair_identity_matrix.csv
```

The input schemas are enforced by the script. Identity evidence must have a
stable security ID, symbol, instrument type, effective interval, source URL,
retrieval timestamp, SHA-256, authorization status and evidence tier.
Execution evidence must carry the exact security ID and business date,
traded quantity, source URL, retrieval timestamp, SHA-256, authorization
status and evidence tier. Pair rows retain their source path, blob SHA and row.

Only an exact, unique, effective-dated identity joined to exactly one
rights-cleared positive-quantity execution row on the same date is marked
`IDENTITY_AND_EXECUTION_EVIDENCE_MATCHED`. Every ambiguous, unsupported,
unauthorized, unhashable, zero-volume, or date-mismatched row remains `HOLD`.
The output summary includes a SHA-256 of the generated matrix.

This is an evidence-preparation result only. It does not change canonical
OHLCV, resolve a repeated pair automatically, authorize a source, or permit
canonical promotion. Reviewers must still verify the source and source rights.
