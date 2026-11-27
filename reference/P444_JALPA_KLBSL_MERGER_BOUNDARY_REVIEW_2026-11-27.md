# P4.44 — JALPA / KLBSL merger-date boundary review

Date: 2026-11-27  
Branch: `p443-global-integrity-audit`

## Primary notice evidence

A NEPSE-hosted, two-page issuer merger notice was visually reviewed at:

`https://www.nepalstock.com/api/nots/security/fetchFiles?fileLocation=klbsl_user%2F2024-06-24%2FJoint+Transaction+Notice-merged_1719213283816.pdf`

The readable notice identifies Kisan Laghubitta and Jalpa Samudayik Laghubitta and describes their merger into Matribhumi Laghubitta. It states:
- integrated business operations under Matribhumi from BS 2081-03-27, Gregorian 2024-07-11;
- banking transactions of both institutions were closed on BS 2081-03-26 for data migration.

This supports the successor/integrated-business date. It does **not** state an exchange-certified last executed trade date or an effective date for a historical stable security ID.

## Boundary separation

The existing secondary-source evidence review records 2024-07-10 as a last-recorded OHLCV date for JALPA and KLBSL. That is a file-boundary observation, not an exchange-issued trading boundary. The notice's statement that banking transactions were closed for migration on 2024-07-10 must not be conflated with a NEPSE trading suspension or last-trade event.

## Evidence gaps

- Original PDF bytes, retrieval timestamp, byte length, SHA-256 and Git blob SHA have not been captured; only the rendered notice was readable in the prior capture attempt.
- No separate NEPSE exchange trading suspension / last-trade notice has been obtained.
- Historical stable security IDs for JALPA and KLBSL remain null.
- The effective-dated lifecycle ledger continues to keep both records `HOLD_UNKNOWN`.

## Disposition

**Work package #5 remains PARTIAL.** The NEPSE-hosted notice supports the 2024-07-11 integrated-business date and Matribhumi successor relationship, but does not establish the last NEPSE trading date or historical IDs. Do not use 2024-07-10 as an exchange trading boundary solely from the banking-closure statement or OHLCV row presence. No lifecycle, OHLCV, canonical, or scanner-input records were changed or promoted.

Next evidence: original notice bytes and an exchange-issued trading suspension/last-execution boundary for each predecessor security.
