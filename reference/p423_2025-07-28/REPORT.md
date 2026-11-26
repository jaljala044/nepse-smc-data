# P4.23.2 — 2025-07-28 floorsheet reconstruction evidence report

## Result

All 86 target symbols have at least one mapped floorsheet transaction. The 170,726-row archive parses with no malformed rows, invalid numeric rows, duplicate contract IDs, duplicate complete rows, or contract IDs outside the 2025-07-28 date prefix. Quantity totals reconcile exactly to the archive header (44,124,924). Turnover reconciles to NPR 19,360,873,034.29 within binary floating-point accumulation tolerance (raw sum 19,360,873,034.29009; round to 2 decimals).

The archive's transaction `time` field is blank on all 170,726 rows. Therefore opening and closing prices are UNKNOWN for every symbol. Contract-ID ordering is not assumed to be chronological.

## Source provenance

- Repository: `Shubhamnpk/yonepse`
- Pinned commit: `d26f543b0b88d38a47020235aef66ccecf3d11c1`
- Path: `data/floor_sheet/daily/2025-07-28.json`
- Git blob SHA: `94187a43992467c1d3799e34dc352a98f4c6a4f8`
- Downloaded size: 8,563,784 bytes
- SHA-256: `4b37929a86d1f2a3f09526afc874186dd716e90eec2736904ef5ec37d4dd71e0`
- Immutable URL: https://raw.githubusercontent.com/Shubhamnpk/yonepse/d26f543b0b88d38a47020235aef66ccecf3d11c1/data/floor_sheet/daily/2025-07-28.json
- Symbol lookup: `data/floor_sheet/lookups/stocks.json`, blob `a33d1efb61a77cdfcc0b6a4f6fdbcc1a3c5d31ed`

The source README attributes the feed to the NEPSE Official API. This is source attribution, not independent proof of complete official capture. The file's own transaction count and aggregate totals are internally consistent; no independent NEPSE `totalElements`/pagination receipt or official daily control total was available in this audit.

## Aggregation semantics

Each transaction row is interpreted using the declared columns: `contractId, stockId, buyer, seller, qty, rate, amount, time`. Per-symbol high/low are the extrema of `rate`; volume is the sum of `qty`; turnover is the sum of `amount`. Open/close require chronological first/last trades, which cannot be established because every `time` is blank. No inferred ordering is used.

## Comparison snapshot provenance

- Canonical SMC source: `jaljala044/nepse-smc-data` at main commit `77992c29c6f3936da92170e240638789b8c5cf00`; 86 date-matched rows read from `03_stock_charts_ohlcv/{symbol}_OHLCV.csv` and preserved in `canonical_snapshot.csv`.
- Secondary counterpart: `srijankarki07/nepse-data` at commit `688d59c03915dcee73ecad4230d2083a41c61764`, path `data/daily/2025/2025-07-28.csv`; the 86-row pinned copy is `external_counterpart.csv`.

## Reconciliation

- Floorsheet quantity matches canonical chart volume for all 86 symbols.
- Floorsheet quantity matches the pinned secondary counterpart volume for all 86 symbols.
- Floorsheet turnover matches the pinned secondary counterpart turnover for all 86 symbols.
- High/low are compared individually in `results.csv` and `results.json`; the floorsheet extrema do not agree with every canonical/secondary row.
- Open and close are UNKNOWN against both comparison sources because chronological ordering is absent.
- Canonical chart files do not expose turnover in the captured OHLCV row, so that comparison is UNAVAILABLE.

## Coverage and anomalies

- Target symbols: 86; symbols with trades: 86; absent: 0.
- Transaction rows: 170,726; declared rows: 170,726.
- Malformed rows: 0; invalid numeric rows: 0; duplicate contract IDs: 0; duplicate complete rows: 0.
- Contract-date prefix failures: 0; null field values: 0.
- Blank timestamps: 170,726.
- One stock ID in the whole archive is not present in the pinned lookup; it is outside the 86-symbol target set.

## Disposition

All 86 remain `CONFLICT_UNRESOLVED_PRIMARY_PENDING`. This archive supports candidate extrema, quantity and turnover evidence, but cannot independently reconstruct complete OHLC candles. No canonical OHLCV, production scoring, or conflict status has been changed.

## Reproducibility

Run:

```bash
python reference/p423_2025-07-28/fetch_source.py /tmp/yonepse_floorsheet_2025-07-28.json
python -m unittest discover -s reference/p423_2025-07-28/tests
python reference/p423_2025-07-28/reconstruct.py \
  --archive /tmp/yonepse_floorsheet_2025-07-28.json \
  --lookup reference/p423_2025-07-28/source/stocks.json \
  --canonical reference/p423_2025-07-28/canonical_snapshot.csv \
  --external reference/p423_2025-07-28/external_counterpart.csv \
  --out reference/p423_2025-07-28/recomputed
```

The raw archive duplicate could not be committed because the GitHub upload transport rejected the 8.56 MB request. The exact immutable upstream blob and SHA-256 above are preserved as the authoritative input pointer; the PR does not claim a duplicate archive copy exists.
