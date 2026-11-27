# P4.44 — three cancellation-notice provenance review

Date: 2026-11-27  
Branch: `p443-global-integrity-audit`

## Exchange-notice leads and date interpretation

| Symbol | NEPSE notice statement recorded in evidence ledger | Gregorian interpretation | Current evidence limit |
|---|---|---|---|
| NICAD8283 | Cancellation after trading on BS 2082-06-02; maturity BS 2082-06-03 | 2025-09-18 | NEPSE signed letter was previously visually reviewed; original PDF bytes and hashes not captured; historical ID and full trade history absent |
| NICGF | Cancellation from BS 2081-11-26; maturity BS 2081-11-28 | 2025-03-09 | NEPSE signed letter was previously visually reviewed; original PDF bytes and hashes not captured; historical ID and full trade history absent |
| SBLD2082 | Cancellation after trading on BS 2082-09-24 | 2026-01-08 | One-page NEPSE PDF was previously visually reviewed; original PDF bytes and hashes not captured |

These dates are preserved as notice statements and calendar conversions. They are not treated as proof of historical security IDs or complete execution histories.

## Provenance gap

For all three leads, the repository does not yet contain the original unmodified PDF bytes with reproducible UTC retrieval timestamp, byte length, SHA-256 and Git blob SHA. The prior visual reviews support notice content but do not satisfy raw-payload provenance. No new raw payload was obtained in this pass.

## Disposition

**Work package #7 is PARTIAL.** The three NEPSE notice leads and printed BS cancellation dates are catalogued; original-byte provenance and historical ID/trade-history joins remain incomplete. All affected lifecycle rows remain `HOLD_UNKNOWN`; no OHLCV, canonical or scanner-input row was changed or promoted.

Next evidence: capture each original NEPSE PDF byte-for-byte, record retrieval metadata and hashes, then link the notice's security identity to a verified historical stable ID and date-matched execution evidence.
