# P4.43 execution acceptance and quarantine disposition

Run [55](https://github.com/jaljala044/nepse-smc-data/actions/runs/45891996012) passed on head b47d34864dffc8c2f88ab8b019e579c8d57a0712; input 56362fb4f65b91fdcca8f50b50e53ad80e703649.
Strict audit: 928 inventoried, 784 parsed, 138 inventory-only, 6 non-JSON responses, 1,668,641 parsed records, zero file failures. Findings: 94,543 unresolved adjacent tuples, 1,331 invalid OHLCV, 30 missing contract sessions, 490,440 conflicting keys, 10 repeated records. Categories overlap. Standard and strict artifacts: 15151049769 and 15152680020. These totals are from logs, not a new independent source audit.

## Quarantine disposition (policy record, not runtime enforcement)
| Path | Git blob SHA | Rows | Repeated contract occurrences | Disposition |
|---|---|---:|---:|---|
| reference/p433_floorsheets/floorsheet_2024-08-14.csv.gz | 0dd938bc5e6bfd50fa09bf85f0836d443ab15983 | 244019 | 219615 | BLOCK_CANONICAL |
| reference/p433_floorsheets/floorsheet_2024-08-18.csv.gz | 49d6498bfb30681b7896b6c5c824b518e50f941d | 300918 | 270825 | BLOCK_CANONICAL |

Pinned reference/p433_floorsheets/capture_report.json reports all 544937 source record IDs unique and zero exact repeated rows. Contract collisions suggest precision loss but exact cause and original IDs are unverified. Preserve all rows; do not invent identifiers or use archive-local IDs as exchange contract IDs. Both p435 marketwide control responses share blob 732e3365b4304f7696a9d30dcd2e94451535caf8 and contain 2026-11-26 trades, not requested 2024 dates; reject as historical evidence.

## Open acceptance items
Reconcile 1331 invalid rows with existing exception ledger; classify 94543 adjacent tuples using verified session evidence; investigate 30 missing session findings and six non-JSON responses; confirm ten repeated summary records from current artifact; integrate quarantine rules into canonical ingestion and test. No independent data validation, corrections, raw mutation, or production promotion. PR #80 remains draft pending these checks. AI recommendations disabled. P4.40 postponed.
