# P4.43 — three official EOD close conflicts in the 490 date-shift candidate set

Review date: 2026-11-27

## Scope and reconciliation

The pinned P4.28 official EOD reconciliation contains 599 rows, including 490 rows marked `ALREADY_RECOVERED_DATE_SHIFT`. Exact tuple comparison yields 487 full OHLCV matches and three Close-only conflicts. All three conflicts are also present in the existing 112-row official correction ledger.

| Symbol | Business date | Candidate Close | Official Close | Other tuple fields |
|---|---|---:|---:|---|
| KBL | 2026-03-01 | 192 | 191.8 | Open/High/Low/Volume match |
| SAIL | 2026-03-01 | 1306 | 1329 | Open/High/Low/Volume match |
| ULBSL | 2026-03-01 | 3118 | 3178 | Open/High/Low/Volume match |

For all three, official turnover also matches the candidate. Official security IDs are KBL 142, SAIL 9301 and ULBSL 8063. All three rows share captured official payload SHA-256 `f95a54e751d3fe604c25e797e948831a35928166e2efea2319e244c9c359a5b5`, retrieved at `2026-11-26T23:00:15.162202+05:45`.

## Finding

This is not a newly discovered date-shift class. The three close conflicts were already recorded in `reference/p428_112_official_eod_corrections_2026-11-26.csv`. The audit confirms they are close-only differences; it does not explain whether they arise from the external candidate, a later source correction, or source-version timing.

## Disposition

- Keep all three rows in the official correction review ledger.
- Do not overwrite raw or canonical OHLCV.
- Do not infer that the official Close should automatically replace the candidate.
- No date relabels, corrections or promotions are authorized.

Source reconciliation blob: `bece4a5c50dd80d0836306944435dffc875a53a8`.
Correction ledger blob: `a6d507d0fb309c9d692b33211a6cf503d5a3cfc4`.
Pinned global input: `56362fb4f65b91fdcca8f50b50e53ad80e703649`.

The full 928-file date-shift scan remains incomplete; this bounded review closes only the three known official EOD close discrepancies within P4.27/P4.28.
