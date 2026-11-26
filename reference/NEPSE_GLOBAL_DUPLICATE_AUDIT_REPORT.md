# P4.43 global duplicate and data-integrity audit — inventory checkpoint

**Status:** metadata inventory captured; content-level duplicate scan not yet complete.  
**Pinned repository ref:** `main` at `56362fb4f65b91fdcca8f50b50e53ad80e703649`  
**Inventory file:** `reference/NEPSE_GLOBAL_DUPLICATE_AUDIT_INVENTORY.csv`

## Inventory scope

The inventory is a deduplicated Git-tree listing of the relevant OHLCV, floorsheet, calendar, market-summary, scanner-input, and reference/provider/archive paths. Each entry records repository, ref, commit SHA, path, Git blob SHA, byte count, category, format, and scan status.

- Files inventoried: **928**
- Total bytes: **60662491**
- OHLCV symbol files: **525**
- Floorsheet/reconciliation artifacts: **33**
- Calendar/session artifacts: **32**
- Provider/audit archive files: **226**
- Scanner input archive files: **63**
- Market/floorsheet summaries: **13**
- Related named project artifacts: **36**

## Category counts

- `related_project_artifact`: 36
- `session_calendar`: 32
- `market_or_floorsheet_summary`: 13
- `floorsheet_or_reconciliation`: 33
- `ohlcv_symbol_archive`: 525
- `provider_or_audit_archive`: 226
- `scanner_input_archive`: 63

## Limitations at this checkpoint

- This file is a **metadata inventory**, not a completed content scan. Structured CSV/JSON/GZIP files are marked `metadata_indexed_content_scan_pending`; PDFs, Markdown, and other formats are marked inventory-only.
- No file is counted as content-scanned yet. Content scan results and parse failures must be reported separately in the next stage.
- No duplicate counts, OHLCV corrections, row deletions, date shifts, or canonical promotions are claimed.
- Existing P4.27/P4.29–P4.37/P4.42 findings will be cross-referenced rather than added together as independent counts.

## Safety

Read-only. No source file was modified. Inventory blob SHAs and byte sizes pin the exact inputs for subsequent reproducible scanning.
