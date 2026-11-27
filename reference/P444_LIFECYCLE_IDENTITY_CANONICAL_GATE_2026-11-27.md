# P4.44 lifecycle identity holds in canonical ingestion — 2026-11-27

## Implementation

The P4.44 lifecycle register is now consumed by both canonical ingestion entry points:

- `scanner_inputs/canonical_publication.py` — daily floorsheet publication
- `scanner_inputs/prepare_scanner_inputs.py` — scanner input staging and validation

New module: `scanner_inputs/lifecycle_identity_holds.py`.

The module loads the existing 26-symbol P4.44 register and returns a symbol-wide wildcard hold for each row. Because no historical stable IDs or verified effective intervals have been established, the gate conservatively holds every listed symbol on every date. It does not infer a date boundary from an issuer integration date, notice date, maturity date, or current symbol mapping.

The shared `reject_held` check now recognizes these wildcard lifecycle holds in addition to the existing exact security/date and session holds. The same check is used by daily OHLCV row validation, floorsheet validation, and broker-summary validation.

## Fail-closed rules

The lifecycle loader rejects:
- missing ledger files or malformed/duplicate columns;
- missing or duplicate symbols;
- a symbol set different from the pinned 26-symbol scope;
- any row not explicitly marked `HOLD_UNKNOWN`;
- any row with `verified` effective-date confidence, pending explicit gate review.

No symbol can be silently removed from the expected set, and no row is promoted by this integration.

## Regression coverage

New tests in `test_p444_lifecycle_identity_holds.py` cover:
- all 26 register symbols loading as symbol-wide holds;
- non-listed symbols not being blocked by this lifecycle register;
- missing and incomplete ledgers failing closed;
- non-hold/verified records failing closed;
- OHLCV, floorsheet, and broker-summary validation paths rejecting a held symbol.

The publication workflow now runs the P4.44 lifecycle test module alongside the existing P4.43 publication, historical-quarantine, scanner-quarantine and Drive-retrieval regression suites.

## CI result and limitation

Workflow run: https://github.com/jaljala044/nepse-smc-data/actions/runs/46009933829  
Test step: **success** (combined unittest command).  
Python compile step: **success**.  
Overall workflow: **failure at the private Drive quarantine verification step**. The P4.44 regression step itself passed; the workflow is not green end-to-end.

The overall failure is an external evidence/credential gate and must not be described as a P4.44 test failure. No private Drive artifact was retrieved in this run.

## Scope and non-effects

- All 26 lifecycle symbols remain held; zero historical stable IDs are assigned.
- No lifecycle event date was changed or adjudicated.
- No OHLCV, floorsheet, broker-summary, canonical, or session data rows were modified.
- No quarantine was released and no canonical publication was performed.
- This integration closes the previously identified code-coverage gap for the P4.44 register at the two reviewed ingestion entry points. It does not complete the broader P4.43/P4.44 acceptance criteria or resolve primary-source evidence blockers.
