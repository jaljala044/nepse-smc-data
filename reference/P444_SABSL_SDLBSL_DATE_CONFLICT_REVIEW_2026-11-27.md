# P4.44 — SABSL / SDLBSL merger-date conflict review

Date: 2026-11-27  
Branch: `p443-global-integrity-audit`

## Conflicting date claims retained

Two predecessor symbols, SABSL and SDLBSL, have a disputed joint-operations date for successor SMPDA (Sampada Laghubitta):

1. Existing Priority97 / secondary chronology records BS 2081-03-30, Gregorian 2024-07-14.
2. The NEPSE-hosted issuer-notice lead in the lifecycle evidence register is transcribed as BS 2082-03-30, Gregorian 2025-07-14.

The one-year difference is material. The current source pass does not independently adjudicate it.

## Primary-source status

The NEPSE-hosted endpoint resolves to a two-page PDF, but the prior capture attempt yielded no readable text for that PDF and did not capture original bytes. No retrieval timestamp, byte length, SHA-256 or Git blob SHA is available for the original PDF. Consequently the stated BS 2082-03-30 text remains a prior transcription recorded in the evidence ledger, not a newly re-inspected raw document in this pass.

The secondary date and NEPSE-hosted notice lead are not interchangeable. Neither joint-business date establishes the last exchange trading day, suspension effective date, or historical stable security IDs.

## Disposition

- Keep both claims visible: 2024-07-14 (BS 2081-03-30) and 2025-07-14 (BS 2082-03-30).
- Date adjudication: unresolved.
- Last-trade / exchange suspension boundary: unverified.
- Historical stable IDs: absent.
- Both symbols remain `HOLD_UNKNOWN`; no promotion is permitted.

**Work package #6 is PARTIAL — the conflicting claims and evidence limitations are now explicitly documented, but the conflict is not resolved.** No lifecycle, OHLCV, canonical or scanner-input records were changed.

Next evidence: capture and visually inspect the original NEPSE-hosted PDF bytes with hashes, obtain the official trading suspension / resumption notices, and reconcile the dates against exchange records rather than secondary chronology.
