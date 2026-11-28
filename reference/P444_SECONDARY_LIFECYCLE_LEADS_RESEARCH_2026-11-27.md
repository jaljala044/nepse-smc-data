# P4.44 secondary lifecycle leads — research queue (not promotion evidence)

Research date: 2026-11-27

## Purpose and evidence rule

This note records useful leads found while searching for primary lifecycle documents for the 26 symbols absent from the current security snapshot. It is a discovery aid only. Secondary sources and search snippets do **not** establish historical stable security IDs, exact final trading dates, or effective-dated identity intervals. No row in the lifecycle ledger is promoted by this note. All 26 ledger dispositions remain `HOLD_UNKNOWN`.

## Five research workstreams completed

### 1. HBLD83 — locate the primary delisting letter

- Merolagani records an HBLD83 delisting announcement dated 2026-08-20 (BS 2083-05-04): https://www.merolagani.com/AnnouncementDetail.aspx?id=66735
- ShareSansar reports that 25,69,104 units were delisted and identifies maturity as Bhadra 8, 2083: https://www.sharesansar.com/newsdetail/10-himalayan-bank-limited-debenture-2083-delisted-from-nepse-2026-08-19
- Sajilo Trading reports last trading date 2026-08-04 (BS 2083-04-19): https://trading.sajiloapps.com/company/hbld83
- No NEPSE-hosted signed cancellation PDF was found in this search pass.
- **Disposition:** secondary corroboration only; retrieve NEPSE's original signed cancellation letter and raw bytes before ledger update.

### 2. NICAD8182 — distinguish maturity, last trade and cancellation

- ShareSansar reports maturity/delisting on 2025-01-13 (BS Poush 29, 2081): https://www.sharesansar.com/index.php/newsdetail/9-nic-asia-debenture-208182-delisted-from-nepse-2025-01-13
- Sajilo Trading reports last trading on 2025-01-08 (BS Poush 24, 2081): https://trading.sajiloapps.com/company/nicad8182
- These dates are not interchangeable: last execution, maturity, and exchange cancellation may each be different events.
- **Disposition:** no new date added to ledger; obtain NEPSE signed delisting notice and issuer maturity notice, then represent separate event types.

### 3. NICD83/84 — separate announcement, last execution and maturity

- Merolagani records a delisting announcement dated 2026-08-19 (BS 2083-05-03): https://merolagani.com/AnnouncementDetail.aspx?id=67084
- A separate Merolagani maturity/payment notice gives maturity as Bhadra 10, 2083: https://merolagani.com/AnnouncementDetail.aspx?id=66717
- Sajilo Trading reports last trading on 2026-08-24 (BS 2083-05-08): https://trading.sajiloapps.com/company/nicd83-84
- ShareSansar independently reports delisting on 2026-08-26: https://www.sharesansar.com/newsdetail/1025-nic-asia-debenture-208384-delisted-from-nepse-2026-08-26
- **Disposition:** useful chronology leads, not primary proof. Do not infer final trading date from the delisting announcement date.

### 4. NMB50 — identify scheme maturity and last eligible trading date

- NMB Capital's notice, reproduced by NEPSE Trading, states the scheme maturity date as 2083-05-12 and that units were eligible for trading through 2083-05-10; it also says trading stops after publication of the liquidation notice: https://nepsetrading.com/announcements/nmb-fifty-scheme-liquidation-and-trading-halt-notice?lang=en
- Merolagani lists the NMB50 de-listing announcement dated 2026-08-26 (BS 2083-05-10): https://merolagani.com/AnnouncementDetail.aspx?id=67152
- Search also found a NEPSE-hosted NMB Capital notice, but it concerns dividend and book closure, not scheme liquidation/delisting: https://www.nepalstock.com/api/nots/security/fetchFiles?fileLocation=rita_listing%2F2025-08-19%2FNMB_1755577256412.pdf
- **Disposition:** do not treat the unrelated NEPSE-hosted PDF as delisting evidence. Need the specific liquidation notice and exchange cancellation letter as raw primary documents.

### 5. Merger date cross-check — preserve conflicting records

- Nepali Paisa's completed merger table reports:
  - SABSL + SDLBSL to SMPDA: joint transaction 2081-03-30 (2024-07-14).
  - SFCL + PFL to PFL: joint transaction 2083-03-26 (2026-07-10).
  - NLBBL + MMFDB to NMLBBL: joint transaction 2080-11-30 (2024-03-13).
  - SAMAJ + GBLBS to GBLBS: joint transaction 2082-07-02 (2025-10-19).
  - URL: https://nepalipaisa.com/merger
- The SABSL/SDLBSL secondary date of 2024-07-14 agrees with the previously recorded Priority97 date but conflicts with the previously captured NEPSE-hosted issuer notice text that says joint business from 2082-03-30 (2025-07-14). Do not choose either date until the original notice bytes and exchange trading-suspension/resumption notices are inspected.
- ShareSansar reports PFL/SFCL integrated operations from 2083-03-26 (2026-07-10), with trading suspension requested from that date: https://www.sharesansar.com/index.php/newsdetail/pokhara-finance-and-samriddhi-finance-to-begin-unified-operations-from-ashadh-26-after-merger-approval-2026-06-26
- **Disposition:** all dates are leads only. Obtain issuer notices, NEPSE trading-suspension notices and final listing/renaming evidence. The operational integration date is not automatically the final trading date of each predecessor symbol.

## Symbols still without a direct primary URL in the lifecycle ledger

The current ledger has 16 rows with no source URL:
`CMF1, CMF2, GBD80/81, HBLD83, KLBSLP, LEMF, NIBD2082, NICAD8182, NICD83/84, NLBBL, NMB50, SAEF, SBLD83, SFCL, SFCLP, SRD80`.

This search produced secondary leads for HBLD83, NICAD8182, NICD83/84, NMB50, NLBBL and SFCL, but did not produce an authenticated primary NEPSE source file with raw-byte provenance for those rows. No new source URL has been written into the lifecycle ledger.

## Required evidence before any lifecycle promotion

For each instrument/event, capture:
1. Original issuer or NEPSE document bytes and the exact source URL.
2. Retrieval timestamp in UTC, HTTP metadata/status where available, byte length and SHA-256.
3. Git blob SHA for the committed raw payload.
4. Exact source statement, calendar basis, and a distinction between announcement, last eligible trading, maturity, cancellation, and joint-operation dates.
5. Stable security ID and evidence for the effective interval; current snapshot IDs are not historical continuity proof.
6. Independent corroboration where dates conflict.

No canonical OHLCV was changed, no date was shifted, no rows were removed or deduplicated, and no identity/date promotion was made.
