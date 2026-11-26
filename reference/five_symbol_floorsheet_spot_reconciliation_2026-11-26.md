# Floorsheet spot reconciliation for five disputed OHLCV archives — 2026-11-26

## Scope and method

A targeted check compared the two available daily floorsheet CSV snapshots dated 2026-11-19 and 2026-11-20 with the five OHLCV archives previously flagged for calendar and repeated-row review: NESDO, SYPNL, ULBSL, USLB and YMHL.

Both floorsheet CSVs contain exactly 500 data records. Their presence and matching transaction dates establish positive contract observations where a symbol is present. The 500-row files have not been demonstrated to be complete day-wide extracts, so absence from either file is **not** evidence of no trade. These are repository-held third-party records, not a claim of direct NEPSE-authenticated source provenance.

## Positive contract observations

| Date | Symbol | Contracts in available 500-row file | Disposition |
|---|---|---:|---|
| 2026-11-19 | NESDO | 1 | TRADED — positive contract observed |
| 2026-11-19 | SYPNL | 38 | TRADED — positive contracts observed |
| 2026-11-20 | SYPNL | 4 | TRADED — positive contracts observed |
| 2026-11-20 | YMHL | 2 | TRADED — positive contracts observed |

No contracts for ULBSL or USLB appeared in these two 500-row samples. No NESDO or YMHL contracts appeared in the other sample date. Because completeness and full-day coverage are not established, all such absences remain **UNKNOWN**, not NO_TRADE.

## Interpretation

- A matching, date-stamped contract is positive evidence that the symbol traded on that date in the supplied floorsheet record.
- A missing symbol in a capped or otherwise unverified extract cannot establish zero contracts.
- The OHLCV archive rows dated on calendar-closed dates remain flagged for reconciliation. The partial calendar itself may have incorrect scope or status; the flag is not an automatic data rejection.
- Adjacent identical OHLCV rows remain review candidates. They may be carried-forward values or genuine repeated values; no row is deleted or reclassified without provenance.
- The available 2026-11-19/20 floor files do not resolve historical closed-date flags across the 2024–2026 archive.

## Code change

The read-only archive audit now adds explicit `resolution_status=UNKNOWN` and a reason to:
- `row_on_verified_closed_date`
- `adjacent_identical_ohlcv_review`

This prevents downstream users from treating review flags as confirmed bad rows or confirmed no-trade observations. Raw OHLCV is not modified.

## Remaining evidence required

1. Full-day, date-matched floorsheet extracts with documented completeness and source provenance.
2. Exchange-confirmed session calendar and holiday/weekly-closure evidence for every flagged date.
3. Security-level trade/volume reconciliation between floorsheet aggregates and OHLCV rows.
4. Independent source and timestamp/hash lineage for each raw extract.

## Disposition

- Positive trade observations: established for NESDO/SYPNL on 2026-11-19 and SYPNL/YMHL on 2026-11-20 within the available samples.
- Negative trade conclusions: none supported.
- ULBSL and USLB on these sample dates: UNKNOWN.
- Closed-date and repeated-row flags: UNKNOWN pending full provenance.
- Canonical promotion and model training: **not allowed**.
