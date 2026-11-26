# P4.15 — canonical session status reconciliation fix

**Date:** 2026-11-26  
**Scope:** Evidence-gated floorsheet-to-OHLCV trade-status classification.

## Defect found

The canonical date calendar uses `verified_open_observed` for a date with a positive NEPSE official price/volume observation (scoped to sampled security ID 8108). The daily floorsheet reconciler previously accepted only the internal token `verified_open` when deciding whether a complete, hash-matched full-session floorsheet could establish `NO_TRADE`.

As a result, passing the canonical calendar directly into the reconciler caused legitimate observed-open dates to remain `UNKNOWN`, even when the floorsheet passed the full completeness, file-integrity and market-total checks. This was a fail-closed false negative, not an unsafe false positive.

## Change

The no-trade gate now accepts either:
- `verified_open`: existing normalized input used by prior callers/tests;
- `verified_open_observed`: canonical calendar status backed by a positive NEPSE exchange-history observation.

It continues to reject:
- `candidate_open_weekday`: weekday logic is not proof that the exchange opened;
- `verified_closed`: closed dates cannot be classified as NO_TRADE;
- missing/unknown statuses;
- incomplete, invalid, non-hash-matched or market-total-mismatched floorsheets;
- any case with positive OHLCV volume for a symbol but no matching floorsheet contract.

## Preserved status contract

- `TRADED`: one or more valid, date-matched, unique contracts for the symbol in a structurally valid floorsheet. OHLCV volume mismatch remains an explicit reconciliation conflict.
- `NO_TRADE`: no symbol contracts in a valid, complete, SHA-256-matched full-session extract; all market totals reconcile; session status is verified open; and symbol OHLCV is absent or explicitly zero-volume.
- `UNKNOWN`: every other case, including absence from a partial/unverified floorsheet or absence of an OHLCV row by itself.

A positive observation for security ID 8108 is evidence that the market traded on that date; it is not evidence that every listed security was eligible or expected to trade. Symbol-level `NO_TRADE` still requires the complete full-session contract file and reconciliation checks above.

## Regression tests

Added:
1. Canonical `verified_open_observed` can support `NO_TRADE` only with full evidence.
2. `candidate_open_weekday` remains `UNKNOWN` even if a complete-looking manifest is supplied.

Existing tests continue to cover hash mismatch, invalid contracts, duplicate contracts, OHLCV conflicts, zero-volume rules, market-total mismatches, and closed sessions.

## Coverage limitation — not a 281-equity completeness pass

This patch fixes a status-vocabulary mismatch in the reconciliation gate. It does **not** create a complete per-security expected-session calendar, verify all 281 lifecycle boundaries, or prove zero-trade days for dates without full-session source files. The current 225 positive observed dates remain scoped to security ID 8108. Candidate weekdays remain candidates.

No raw OHLCV, canonical calendar, lifecycle input, or production/training data was changed. No scanner eligibility or BUY authorization is granted by this patch.
