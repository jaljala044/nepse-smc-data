# NEPSE instrument-symbol reconciliation — 2026-11-26

## Disposition

The requested instrument-symbol check is completed for the seven user-finalized discrepancy symbols. All seven symbols are present in the current NEPSE public stock-list snapshot available during this review:

- `API`
- `BGWT`
- `HRL`
- `MEHL`
- `RAWA`
- `RHGCL`
- `ULHC`

The source page displays an “As of Oct 15, 2026” timestamp. This is a **current symbol-presence check**, not a complete effective-dated instrument master.

## Official source

- NEPSE public stock list: https://www.nepalstock.com.np/stocklist
- Official NEPSE homepage / corporate information links: https://www.nepalstock.com.np/
- Retrieved/reviewed: 2026-11-26
- Source page's displayed data timestamp: 2026-10-15
- Capture method: publicly rendered/indexed page content reviewed; no raw HTTP response bytes were obtained in this workflow, so no raw-payload checksum is claimed.

## Reconciliation scope and result

- Historical OHLCV directory contains 525 symbol-named CSV files.
- Seven symbols in the manually finalized discrepancy set were checked against the NEPSE public stock list.
- Result: 7/7 current symbol-presence matches.
- Detailed machine-readable rows: `reference/nepse_instrument_symbol_reconciliation_2026-11-26.csv`.

## Important limits

The public stock-list page is a useful official discovery source, but it does not provide, in the retrieved evidence, the stable security IDs, complete instrument classifications, effective listing/delisting dates, or historical symbol-change mappings required for a canonical instrument master. It also cannot establish that each symbol was active on every historical OHLCV date.

The 525-file OHLCV universe includes non-common-share instruments (for example debt, mutual-fund, preference, and other instrument-like tickers); the current stock-list page is not sufficient to classify all of them. Therefore this report does **not** claim that all 525 files have been fully reconciled to an official master.

## User-finalized OHLCV data

User-provided values remain authoritative project inputs for the seven flagged records. Source disagreement does not reopen these records. The 2025-07-28 BGWT chart row was manually corrected in `03_stock_charts_ohlcv/BGWT_OHLCV.csv` to:

`2025-07-28,824.56,870.18,818.77,839.62,14028.0`

API and HRL on 2026-11-19 and MEHL, RAWA, RHGCL, ULHC on 2025-07-28 were read back from the repository during this review and match the user-finalized OHLCV values. Floorsheet aggregate quantity/turnover values remain separately recorded as user-supplied aggregates; they are not represented as independently captured contract-level NEPSE evidence.

## Final status

- User-finalized discrepancy records: **closed as project inputs**.
- Seven-symbol current NEPSE stock-list presence check: **passed**.
- Full 525-symbol official instrument-master reconciliation: **not established**.
- Historical lifecycle / stable-ID mapping: **not established**.
- Canonical promotion of the entire instrument register: **not approved by this evidence**.

This is the completed and auditable disposition for the requested manual data adjustment and seven-symbol instrument check. Broader historical calendar and full instrument-master requirements remain separately open under issue #4.
