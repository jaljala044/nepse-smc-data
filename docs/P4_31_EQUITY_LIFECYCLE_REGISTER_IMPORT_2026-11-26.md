# P4.31 — current equity lifecycle candidate register import

This folder-level register is mirrored from the companion scanner repository at immutable commit `c88a3d84e1b2becd150bc0f1d3160109f5e398df`.

Imported:
- `reference/nepse_equity_lifecycle_coverage_input_2026-11-26.csv`
- `reference/nepse_security_lifecycle_events_2026-11-26.csv`

The 281-row equity lifecycle input has 44 dated starts and 237 blank starts. Its evidence-status counts are: {"unverified":237,"verified_secondary_first_trade_archive_match":30,"verified_secondary_notice":14}. All 281/281 security ID/symbol pairs match the current official 2026-11-25 security-list snapshot.

The separate event ledger has 6 typed events. It intentionally distinguishes merger joint-operations dates, listing/trading-release dates, and reported listing dates from first executed trades.

**Evidence tier:** candidate lifecycle context only. The dated starts are secondary-evidence records, not official exchange first-trade proof. Blank dates remain UNKNOWN. The current ID match is point-in-time only and does not prove historical identity continuity.

No canonical lifecycle, OHLCV, session calendar, scoring, training, or BUY eligibility fields are promoted.
