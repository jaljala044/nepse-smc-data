# P4.45 — cross-repository wrong-session ingestion guard

Date: 2026-11-28  
Repository: `jaljala044/nepse-smc-data`  
Base branch: `p443-global-integrity-audit`  
Working branch: `fix/p445-cross-repository-session-guard`

## Scope

A bounded regression-hardening change for four preserved market-wide control responses that were requested for 2024 dates but contain 2026-11-26 trades. This work is separate from the broader date-lineage and footprint inventories.

## Verified source evidence

The four raw files are:

- `control_marketwide_2024-05-16_page0.json`
- `control_marketwide_2024-05-19_page0.json`
- `control_marketwide_2024-08-14_page0.json`
- `control_marketwide_2024-08-18_page0.json`

All four return the same Git blob SHA `732e3365b4304f7696a9d30dcd2e94451535caf8`. Each contains 500 rows and 500 unique `contractId` values; all rows have `businessDate=2026-11-26`, not the requested date. The raw payloads are preserved and are not deleted or rewritten.

## Engineering change

`scanner_inputs/prepare_scanner_inputs.py` now detects a long numeric contract ID with a valid YYYYMMDD prefix and rejects it when that prefix disagrees with the row's declared date. This closes a direct staging path where `validate_floorsheet` previously checked the row date but did not compare it with an available contract-session prefix.

The canonical publication path already requires the contract ID to start with the requested session date. New tests exercise both the staging validator and the canonical publisher against all four manifest date mappings.

Non-date-coded contract identifiers are not reinterpreted. The check does not infer a date from a nonnumeric or short contract ID.

## Regression coverage

A dedicated GitHub Actions workflow runs the five new tests plus the existing scanner-quarantine, canonical-publication, historical-quarantine and lifecycle-identity regression suites:

1. Pin all four raw payload hashes, row counts, unique contract counts and actual dates to the manifest.
2. Reject all four historical requested-date labels in staged floorsheet CSVs.
3. Reject all four requested-date labels in the canonical publication path before writing output.
4. Accept a contract prefix when it matches the actual 2026-11-26 session.
5. Preserve compatibility for a non-date-coded contract identifier.

## Validation result

- Focused workflow: [Run 3](https://github.com/jaljala044/nepse-smc-data/actions/runs/46113726363) — **success**.
- Five new P4.45 tests plus existing scanner-quarantine, canonical-publication, historical-quarantine and lifecycle-identity suites: **69 tests passed** (`Ran 69 tests ... OK`).
- Python compilation of `scanner_inputs/prepare_scanner_inputs.py` and `scanner_inputs/canonical_publication.py`: **success**.
- The separate P4.43 global audit workflow Run #343 was still in progress at the time of this read-back; it is not counted as a P4.45 test result.

## Safety and limitations

- No raw evidence, canonical OHLCV, floorsheet archive, scanner input, or user-finalized record was modified.
- No date was relabeled and no row was promoted.
- This guard detects valid date prefixes in long numeric contract IDs. It does not prove session identity for non-date-coded contract IDs or transformed data that loses its original contract identifier.
- Source licensing, archive completeness, and upstream independence remain separate acceptance gates.
- The 281-equity / 47-mutual-fund effective-dated universe and 120-day / one-year coverage matrix remain unfinished.

## Next action

Run the focused regression workflow, inspect its exact result, then extend source-lineage preservation so transformations cannot silently discard the original source hash and requested-versus-actual session metadata.
