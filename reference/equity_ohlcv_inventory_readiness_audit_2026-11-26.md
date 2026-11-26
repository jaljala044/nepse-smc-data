# Equity OHLCV Inventory Readiness Audit — 2026-11-26

## Scope

Equities only. Mutual funds, debt instruments, bonds, debentures, and promoter-share classes are excluded from the target common-equity coverage set. No NICEF work is included.

## Source snapshots

1. Candidate universe: `reference/nepse_target_universe_candidates_2026-11-26.csv`
   - Blob SHA: `45f71a3a81dbe883c8562cf6d7d9e8da9bf51bc4`
   - 325 unique symbols: 278 classified as Equity and 47 as Mutual Fund.
   - No duplicate symbols.
   - All 278 candidate Equity rows have `ohlcv_file_present=true` and a populated security ID.
2. Security snapshot: `reference/nepse_security_id_snapshot_2026-11-25.csv`
   - Blob SHA: `ed548857eb550fbb237910eb903fc202751c63a1`
   - Snapshot date: 2026-11-25.

## Newly identified active-equity omissions

The active security snapshot contains the following ordinary equity names with OHLCV files that are absent from the 278-row candidate Equity list:

| Symbol | Security ID | Security name | Snapshot status | OHLCV file |
|---|---:|---|---|---|
| NESDO | 8041 | NESDO Sambridha Laghubitta Bittiya Sanstha Limited | A | yes |
| ULBSL | 8063 | Upakar Laghubitta Bittiya Sanstha Limited | A | yes |
| YMHL | 9342 | Yambaling Hydropower Limited | A | yes |

YMHL is the additional third equity omission previously unidentified. This resolves the arithmetic gap in the current candidate snapshot (278 candidates + 3 active equity omissions = 281), but does **not** by itself prove that the intended 281-symbol universe is historically complete or that all three securities were active throughout the entire historical period.

## Inventory metrics

- Candidate Equity symbols: 278
- Candidate Equity symbols with an OHLCV file flag: 278 / 278
- Candidate Equity symbols without an OHLCV file flag: 0
- Additional active equity omissions found in the security snapshot: 3
- Provisional equity inventory after adding the three omissions: 281
- Candidate Mutual Funds: 47 (excluded from this equity audit)

## Important limitations

The `ohlcv_file_present` field is an inventory-presence flag only. It does not establish:
- earliest or latest available trading date;
- number of daily rows per symbol;
- missing sessions or internal date gaps;
- whether the OHLCV series is unadjusted and source-consistent;
- whether the file contains only the common-equity instrument class;
- whether the current active status applies to the full historical period.

Therefore this audit is an **inventory readiness check**, not a completed per-symbol historical coverage report. No missing dates, prices, or candles have been inferred.

## Next equity-only validation steps

1. Add NESDO, ULBSL, and YMHL to the candidate equity manifest only after their common-equity classification and lifecycle dates are evidenced.
2. Enumerate the actual OHLCV archive files and calculate, per symbol: first date, last date, row count, duplicate dates, invalid OHLC relationships, and gaps against the verified exchange session calendar.
3. Reconcile each equity file against approved provider evidence (ShareHub, Chukul, ShareSansar, or NepseAlpha), preserving source and capture provenance.
4. Keep promoter shares, mutual funds, and debt instruments out of the common-equity OHLCV universe unless the project explicitly defines a separate instrument class for them.
