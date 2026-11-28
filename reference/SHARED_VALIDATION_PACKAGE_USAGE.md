# Consuming the shared validation package

The package is published from `jaljala044/nepse-smc-data`.

Install from a pinned commit or reviewed branch (do not float production deployments to `main`):

```bash
python -m pip install "git+https://github.com/jaljala044/nepse-smc-data.git@project/shared-validation-foundation"
```

Use the registry from a data pipeline:

```python
from nepse_shared_validation import ValidationRegistry

registry = ValidationRegistry("/shared/nepse/validation/registry.sqlite3")
key = registry.make_key(
    "/data/incoming/session.csv",
    dataset_kind="daily_floorsheet",
    schema_version="floorsheet-csv-v1",
    validator_version="floorsheet-validator-v1",
)
cached = registry.lookup(key)
if cached is None:
    # Run the existing deterministic validator; do not bypass it.
    report = run_existing_validation("/data/incoming/session.csv")
    registry.record(key, "passed" if report["valid"] else "failed", report)
else:
    # Reuse only the technical result. Independently evaluate source evidence,
    # authorization, lineage, coverage and cross-source reconciliation.
    report = cached["report"]
```

## Shared database requirement

Every process that is expected to reuse results must connect to the same durable database path or a future centralized registry service. A local runner can use a mounted shared volume. Separate GitHub-hosted runners do not share local files; do not assume this SQLite path alone provides cross-runner or cross-repository persistence. Until a durable shared store is deployed, CI tests verify the package behavior only, not global cache reuse.

Do not use a GitHub Actions cache as an authoritative evidence store. Cache eviction and scope rules make it unsuitable as the only copy of validation evidence.
