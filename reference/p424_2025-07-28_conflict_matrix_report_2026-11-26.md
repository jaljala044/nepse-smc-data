# P4.24 — 2025-07-28 historical close-conflict matrix

Date: 2026-11-26  
Scope: 86 same-date OHLCV conflicts  
Status: row-level comparison complete; primary-source resolution unavailable in NEPSE's rolling history API

## Result

The deterministic matrix compared all 86 counterpart rows against the SMC raw symbol files.

| Test | Result |
|---|---:|
| Counterpart rows | 86 |
| SMC raw rows found | 86 |
| Open differences | 0 |
| High differences | 0 |
| Low differences | 0 |
| Close differences | **86** |
| Volume differences | 0 |
| Rows with exact O/H/L/Volume match | 86 |
| Secondary-only rows promoted | 0 |
| Canonical disposition | 86 × `UNKNOWN_SOURCE_CONFLICT` |

The disagreement is isolated to the Close field. All 86 pairs have identical Open, High, Low and Volume. The external close minus SMC close ranges from -24.11 to +274.06; 73 external closes are higher and 13 are lower (median delta +3.505). This is a measured pattern, not proof of which close convention is correct.

## Source provenance

- External archive: `srijankarki07/nepse-data`
- Pinned commit: `688d59c03915dcee73ecad4230d2083a41c61764`
- Daily file: `data/daily/2025/2025-07-28.csv`
- External archive file SHA-256: `1ecbd3539784d212c87da54bf9ab18ca4ed8d6c6e5aaf28f29bf58b63e9abd9d`
- External archive README explicitly identifies ShareSansar as its source, not NEPSE directly. ShareSansar republishes exchange EOD figures; this is secondary-source evidence.
- Every SMC raw counterpart file has its own SHA-256 in the matrix.

NEPSE's official EOD API is documented and measured to clamp historical queries to a rolling 365-day window. On 2026-11-26, 2025-07-28 is outside that window. No official NEPSE payload for this date was recovered. Do not claim the secondary archive's values are exchange-authenticated.

## Disposition

All 86 rows remain `UNKNOWN_SOURCE_CONFLICT` and excluded from canonical scoring/training until primary evidence is found. The matching O/H/L/Volume values are useful corroboration, but do not authorize selecting either close. Do not infer a close methodology, apply a uniform offset, overwrite raw files, or convert UNKNOWN to NO_TRADE.

## Reproducibility

- Builder: `tools/build_p424_conflict_matrix.py`
- Tests: `tools/tests/test_build_p424_conflict_matrix.py`
- CI run: [45862707787](https://github.com/jaljala044/nepse-smc-data/actions/runs/45862707787)
- Generated matrix: [p424_2025-07-28_conflict_matrix_2026-11-26.csv](p424_2025-07-28_conflict_matrix_2026-11-26.csv)
- Matrix artifact: [GitHub Actions artifact 15139400460](https://github.com/jaljala044/nepse-smc-data/actions/runs/45862707787/artifacts/15139400460)

## Next investigation

Inspect the 86 close differences by source-page evidence, source scraper commit history and any permitted contemporaneous exchange records. Group outliers by absolute/percentage difference and symbol category. No promotion occurs until an individual row has primary evidence, instrument identity and corporate-action basis validated.
