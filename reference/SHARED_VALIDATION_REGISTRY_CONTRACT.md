# Shared validation registry — implementation contract

Status: initial reusable cache module added on branch `project/shared-validation-foundation`.

## Objective

Avoid repeating deterministic technical validation when the exact same file is imported into more than one repository. The cache is content-addressed and independent of repository path, so byte-identical files can reuse one result.

## Cache identity

A cache entry is reusable only when all four values match:

1. SHA-256 of the complete file bytes.
2. Dataset kind (for example, `daily_ohlcv` or `daily_floorsheet`).
3. Schema version.
4. Validator implementation/version.

A byte change, schema change, or validator upgrade forces a fresh validation. Both passed and failed technical results are cached, preventing repeated processing of unchanged bad inputs.

## Safety boundary — not an approval system

A cache hit means only that the same bytes passed or failed the same deterministic technical checks before. It does **not** prove:

- the source is authorized or licensed;
- the source identity or capture date is correct;
- the dataset covers every expected trading session or equity;
- ShareHub, ShareSansar, Chukul, Mero Lagani or NEPSE sources agree;
- a record is eligible for canonical promotion.

Those evidence, coverage, cross-source reconciliation and approval gates must still be evaluated and retained as source-specific lineage. The user's finalized five-symbol records for 2025-07-28 remain authoritative and must not be overwritten by conflicting provider data.

## Integration contract for all five repositories

- `nepse-smc-data`: owns the canonical validation implementation and registry contract.
- `nepse-history-starter`: computes the file digest and asks the shared registry for a reusable technical result before running its importer checks; it still submits provenance and source evidence.
- `nepse-automation`: uses the same registry contract for newly acquired files; a changed payload naturally gets a new key.
- `nepse-elite-ai-scanner-pro`: consumes only records carrying the required evidence/approval metadata; it does not re-run source acquisition checks.
- `Nepse-master-data`: provides versioned instrument identity/schema inputs; changes to the schema version invalidate relevant cached checks.

The SQLite registry must be hosted in a shared, durable location or published as a versioned validation manifest/artifact for cross-run reuse. A SQLite file committed separately into each repository would recreate the duplication problem.

## First implementation

`tools/shared_validation_registry.py` provides streaming SHA-256, a SQLite result cache and a versioned cache key. Unit tests cover cross-path identical files, modified bytes, schema/validator upgrades and failed-result reuse.

## Rollout gates

1. Run the unit tests and existing repository suites.
2. Integrate one OHLCV validator and one floorsheet validator without weakening their existing rules.
3. Publish the registry database or signed/versioned manifest as one shared artifact.
4. Add consumers one repository at a time and verify cache-hit behavior.
5. Keep per-repository code tests and integration tests independent.
