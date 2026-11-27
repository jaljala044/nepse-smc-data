# P4.43 global audit count reconciliation

Date: 2026-11-27

Pinned input: `main` at `56362fb4f65b91fdcca8f50b50e53ad80e703649`.

## Resolution

The apparent 17,758-record difference between the strict audit summary and the global scan report is a difference in JSON counting units, not a source-data discrepancy.

| Component | Strict parsed-record count | Global report count |
|---|---:|---:|
| CSV + CSV.GZ data rows | 1,650,790 | 1,650,790 |
| JSON | 17,851 parsed record elements | 93 JSON documents |
| Total | **1,668,641 parsed records** | **1,650,883 rows + documents** |

The strict artifact's `coverage.json` contains 928 inventory entries, with 784 parsed files, 138 inventory-only files, and six non-JSON provider responses. Its 93 parsed JSON files contain 17,851 parsed record elements in total.

Arithmetic:

- CSV + CSV.GZ rows: 1,650,790
- JSON parsed record elements: 17,851
- Strict parsed records: 1,650,790 + 17,851 = **1,668,641**
- Global report's document-based count: 1,650,790 + 93 = **1,650,883**
- Difference: 17,851 - 93 = **17,758**

## Canonical reporting rule

Use **1,668,641 parsed records** for the strict audit total, defined as CSV/CSV.GZ data rows plus parsed JSON record elements. If JSON document count is shown, report it separately as **93 JSON documents**; do not substitute document count for parsed JSON record count or add the two units together.

The PR body total of 1,668,641 is consistent with the strict artifact. The prior interpretation that the 17,758 difference represented an unresolved discrepancy is superseded by this reconciliation.

## Distinct finding definitions

- 94,543 consecutive repeated OHLCV tuple pairs.
- 95,356 repeated OHLCV tuples across rows, not assumed erroneous.

These are different scopes/definitions and must not be added as unique affected records.

## Safeguards and remaining status

This is a reporting-definition reconciliation only. No raw, canonical, or user-finalized OHLCV, floorsheet, calendar, or scanner rows were changed, deleted, shifted, deduplicated, corrected, or promoted.

This reconciliation does not close P4.43. Independent adjudication of review queues, full-scope date-lineage reconciliation, independent floorsheet provenance/completeness, canonical-ingestion quarantine enforcement, and production acceptance remain outstanding.
