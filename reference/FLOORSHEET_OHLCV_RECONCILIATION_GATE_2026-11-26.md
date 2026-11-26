# Evidence-gated floorsheet to OHLCV reconciliation

## Files

- Engine: `tools/reconcile_floorsheet_ohlcv.py`
- Regression tests: `tools/tests/test_reconcile_floorsheet_ohlcv.py`
- CI: `.github/workflows/floorsheet-reconciliation-tests.yml`
- Manifest template: `reference/floorsheet_reconciliation_manifest_template.csv`

## Run

```bash
python tools/reconcile_floorsheet_ohlcv.py \
  --floorsheet-dir 02_floorsheet_daily \
  --ohlcv-dir 03_stock_charts_ohlcv \
  --calendar reference/nepse_canonical_session_calendar_2025-2026.csv \
  --manifest reference/floorsheet_reconciliation_manifest.csv \
  --output audit-output/floorsheet_ohlcv_reconciliation.csv
```

The manifest is date-specific and must contain:

- `trading_date`
- `floorsheet_complete` (`true` only after full-day completeness is independently checked)
- `completeness_evidence` (specific audit record, page/contract count reconciliation, and end-of-pagination confirmation)
- `source_uri`
- `source_sha256` (SHA-256 of the exact local floorsheet CSV)

An empty template or absent manifest entry never authorizes `NO_TRADE`.

## Status rules

| Status | Required evidence |
|---|---|
| `TRADED` | At least one valid, date-matched contract for the symbol in the supplied floorsheet file |
| `NO_TRADE` | Zero contracts for the symbol, valid floorsheet file, calendar status `verified_open`, manifest completeness set to true, non-empty evidence and source URI, and exact file SHA-256 match |
| `UNKNOWN` | Any other case, including absent symbols in partial/capped files, unverified session status, malformed records, missing provenance, or hash mismatch |

A positive contract is positive evidence even if the file's day-wide completeness is not proven. A missing symbol is not negative evidence unless every `NO_TRADE` gate passes.

The engine emits every symbol with an OHLCV archive file, including symbols with no bar on that date, so missing bars cannot silently disappear. It reports contract count, total shares, turnover calculated as quantity × rate, VWAP, OHLCV volume and volume-match status. It does not overwrite source OHLCV.

## Important limitation

The current repository's 2026-11-19 and 2026-11-20 files are 500-record samples without verified full-day completeness. They can support positive `TRADED` observations where valid contracts appear, but they cannot support `NO_TRADE` for omitted symbols. Do not mark those dates complete in the manifest.

The 2026-11-23/24 audit JSONs describe larger Chukul page captures and cross-check metadata, but do not automatically prove that the corresponding checked-in 500-row CSV is the same complete dataset. A manifest entry must hash the exact reconciled file and identify evidence establishing its full-day coverage.

## Validation

Run:

```bash
python -m unittest discover -s tools/tests -p 'test_reconcile_floorsheet_ohlcv.py' -v
```

Regression cases cover positive trades in incomplete files, unknown absence, the full `NO_TRADE` gate, closed-session fail-closed behavior and securities without a dated OHLCV bar.

Canonical data promotion and model training remain blocked until complete independent floorsheet/session evidence and full-universe reconciliation pass.
