# Positive open-session evidence — 2025-11-26 to 2026-11-25

**Status:** additive evidence capture; not a complete historical session calendar.  
**Source:** official NEPSE per-security EOD history responses captured in P4.37.

## Result

There are **228 distinct dates** with positive official equity-trade evidence in this window. Each date is supported by at least one official NEPSE security-history response with `totalTrades > 0` and `totalTradedQuantity > 0`.

- 227 dates use ACLBSL (security ID 2790), which has a positive trade count on every date except 2026-03-09.
- 2026-03-09 uses AHPC (security ID from the official P4.37 security-list capture), with 103 trades and 42,929 shares. ACLBSL's row on that date is a zero-trade record, so it is not used as the positive witness.
- All 228 dates are unique and span 2025-11-26 through 2026-11-25.
- No positive-open date overlaps the 2026 official holiday API closure snapshot.
- The P4.37 report records complete, one-page, 228-row EOD responses for 24 symbols; this calendar deliberately selects one positive-trade witness per date rather than treating weekday patterns as evidence.

## Data file

[`nepse_positive_open_sessions_2025-11-26_2026-11-25.csv`](nepse_positive_open_sessions_2025-11-26_2026-11-25.csv) contains one row per date with:
- `verified_open` status and explicit equity positive-trade scope;
- official NEPSE API URL and raw-response SHA-256;
- source symbol, security ID, local capture file, and observed trade/quantity/value totals.

The raw response files and per-symbol response hashes are preserved under `reference/p437_cross_sector_date_audit/` and indexed in `capture_report.json`.

## Validation boundaries

- A positive official equity trade is direct evidence that the equity market was open on that date.
- The calendar does **not** infer open dates from weekdays, absence from the holiday list, or carry-forward OHLCV.
- The 2026 holiday API remains a closure-only source. Its 41 explicit closure records remain separate and unchanged.
- This establishes positive open-session evidence for 228 dates only. It does not classify every other date in the full historical OHLCV period.
- The official schedule-transition notice is still not byte-preserved. A third-party notice-index record is only a discovery lead; the linked NEPSE PDF could not be retrieved, so the schedule transition is not promoted to primary-evidence status.
- No raw, v1, v2, v3, or scanner-input OHLCV rows were changed.
