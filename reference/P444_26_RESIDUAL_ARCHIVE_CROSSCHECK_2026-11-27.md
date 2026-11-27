# P4.44 — residual 26-symbol security-list cross-check

Date: 2026-11-27  
Branch: `p443-global-integrity-audit`

## Scope

Cross-check the 26 unresolved symbols in the 23,377-pair matrix against the pinned NEPSE security-list snapshot and the existing historical-identity evidence review. This is a coverage/reconciliation pass, not a claim that an archived historical register was recovered.

## Inputs

- Current NEPSE security-list capture: `reference/nepse_official_security_list_2026-11-25.raw.json` and parsed snapshot `reference/nepse_security_id_snapshot_2026-11-25.csv`; source snapshot blob SHA recorded in the CSV: `eed3bbb3152e83d4abcb0ee8d03d720c33c63cef`.
- Exact unmatched-symbol review: `reference/nepse_unmatched_symbol_review_2026-11-26.csv`.
- Historical identity review: `reference/P443_HISTORICAL_IDENTITY_EVIDENCE_REVIEW_26_SYMBOLS_2026-11-27.csv`, 26 records.
- Repeated-pair reconciliation: `reference/P444_209_SYMBOL_CURRENT_SNAPSHOT_RECONCILIATION_2026-11-27.md`.

## Results

- All 26 residual symbols have an individual historical-identity evidence-review record.
- The 26 symbols remain absent from the 2026-11-25 exact-symbol security snapshot; none receives a current-snapshot security ID from that register.
- Class candidates: 9 equity, 9 debenture, 6 mutual fund, 2 promoter-share.
- Historical stable IDs verified: 0/26.
- Effective-dated lifecycle boundaries verified: 0/26.
- NEPSE-primary historical security-master or exchange-certified lifecycle records newly obtained in the prior review: 0/26.
- The available leads include secondary reports and a limited number of NEPSE-hosted issuer/exchange notices. Those notices can support specific issuer, successor, or cancellation statements but do not provide the missing historical stable IDs and complete effective intervals.
- All 26 remain `HOLD_UNKNOWN_NO_INFERENCE`; promotion remains disallowed.

## Explicit limitation

The available 2026-11-25 list is a dated current snapshot, not an archived historical sequence. The repository evidence reviewed here does not contain a verified archived NEPSE security list covering the historical effective dates for these 26 symbols. Therefore the requested historical-ID resolution is **not complete**. A ticker/company association, a reported merger date, or an issuer notice is not substituted for an exchange-issued historical security ID.

## Disposition

**Work package #4 is PARTIAL — evidence coverage is reconciled for 26/26, but historical IDs and effective dates are verified for 0/26.** No raw/canonical OHLCV, scanner-input, lifecycle disposition, or repeated-pair row was changed or promoted.

Next required evidence: dated NEPSE security-list snapshots or an official historical security register with stable IDs and validity intervals, plus exchange lifecycle notices that establish the relevant trading boundaries.
