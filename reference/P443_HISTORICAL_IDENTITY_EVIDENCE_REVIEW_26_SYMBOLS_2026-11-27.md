# P4.43 — historical identity evidence review (26-symbol residual)

Review date: 2026-11-27  
Global audit base: `56362fb4f65b91fdcca8f50b50e53ad80e703649`  
Evidence source: `jaljala044/nepse-elite-ai-scanner-pro` at `5a8768828d58bdcebb82393262726d1d030b7ec4`, file `data/reference/nepse_historical_identity_evidence_2026-11-26.json`, blob `589f4ac19451f3faecee41727b44fc62cdeeb818`.

## Result

All 26 residual symbols absent from the dated 2026-11-25 security snapshot were individually matched to existing historical-identity evidence records. Class counts: **9 equity, 9 debenture, 6 mutual fund, 2 promoter-share**. This closes the register-coverage reconciliation only; it does not establish exchange-certified historical security IDs or lifecycle boundaries.

- Historical stable IDs verified: **0/26** (all null).
- Effective dates / lifecycle boundaries verified: **0/26**.
- NEPSE-primary historical security-master or exchange-certified lifecycle records newly obtained: **0**.
- All rows remain `HOLD_UNKNOWN_NO_INFERENCE`; `promotion_allowed=false`.
- Linked reports and project archive boundary observations are secondary-source corroboration, not proof of historical security-ID continuity or authoritative effective dates.
- OHLCV boundary observations, where present, are not proof of an exchange trading boundary. File-row dates and forward-filled rows remain distinct from actual trading sessions.

## Symbol coverage

- `CMF1` — mutual_fund; reported matured; reported 2026-05-20; no successor recorded; stable ID null; effective date unverified.
- `CMF2` — mutual_fund; liquidation completed; reported 2026-11-17; no successor recorded; stable ID null; effective date unverified.
- `GBD80/81` — debenture; instrument identity confirmed; reported date unavailable; no successor recorded; stable ID null; effective date unverified.
- `HBLD83` — debenture; delisting reported; reported 2026-08-19; no successor recorded; stable ID null; effective date unverified.
- `JALPA` — equity; merger completed; reported 2024-07-11; successor: Matribhumi Laghubitta; stable ID null; effective date unverified.
- `KLBSL` — equity; merger completed; reported 2024-07-11; successor: Matribhumi Laghubitta; stable ID null; effective date unverified.
- `KLBSLP` — promoter_share; ticker identity confirmed; reported 2021-01-03; no successor recorded; stable ID null; effective date unverified.
- `LEMF` — mutual_fund; reported matured; reported 2026-05-20; no successor recorded; stable ID null; effective date unverified.
- `MKLB` — equity; acquisition completed; reported 2024-08-02; successor: Samata Gharelu Laghubitta; stable ID null; effective date unverified.
- `MMFDB` — equity; merger completed; reported 2024-05-17; successor: Nerude Mirmire Laghubitta; stable ID null; effective date unverified.
- `NIBD2082` — debenture; redemption notice; reported 2026-06-09; no successor recorded; stable ID null; effective date unverified.
- `NICAD8182` — debenture; delisting reported; reported 2025-01-13; no successor recorded; stable ID null; effective date unverified.
- `NICAD8283` — debenture; delisting reported; reported 2025-09-18; no successor recorded; stable ID null; effective date unverified.
- `NICD83/84` — debenture; delisting reported; reported 2026-08-26; no successor recorded; stable ID null; effective date unverified.
- `NICGF` — mutual_fund; reported matured; reported 2026-05-20; no successor recorded; stable ID null; effective date unverified.
- `NLBBL` — equity; merger completed; reported 2024-05-17; successor: Nerude Mirmire Laghubitta; stable ID null; effective date unverified.
- `NMB50` — mutual_fund; delisting reported; reported 2026-08-26; no successor recorded; stable ID null; effective date unverified.
- `SABSL` — equity; merger completed; reported 2024-08-15; successor: Sampada Laghubitta; stable ID null; effective date unverified.
- `SAEF` — mutual_fund; reported matured; reported 2026-05-20; no successor recorded; stable ID null; effective date unverified.
- `SAMAJ` — equity; merger-related trading suspension; reported 2025-10-17; successor: Grameen Bikas Laghubitta; stable ID null; effective date unverified.
- `SBLD2082` — debenture; delisting reported; reported 2026-01-09; no successor recorded; stable ID null; effective date unverified.
- `SBLD83` — debenture; instrument identity confirmed; reported date unavailable; no successor recorded; stable ID null; effective date unverified.
- `SDLBSL` — equity; merger completed; reported 2024-08-15; successor: Sampada Laghubitta; stable ID null; effective date unverified.
- `SFCL` — equity; merger-related trading suspension; reported 2026-07-09; successor: Pokhara Finance; stable ID null; effective date unverified.
- `SFCLP` — promoter_share; instrument identity confirmed; reported date unavailable; no successor recorded; stable ID null; effective date unverified.
- `SRD80` — debenture; delisting reported; reported 2024-05-14; no successor recorded; stable ID null; effective date unverified.

## Disposition

The evidence-register matching gap is closed for these 26 symbols. The historical identity gate remains open. Do not backdate current IDs, infer aliases, assign validity intervals, splice histories, or alter OHLCV rows from these reports. The remaining evidence requirement is an exchange/issuer primary record that explicitly identifies the historical security ID and effective validity/suspension/delisting date. Until then, retain HOLD/UNKNOWN.

Machine-readable detail: `P443_HISTORICAL_IDENTITY_EVIDENCE_REVIEW_26_SYMBOLS_2026-11-27.csv` and `.json`.
