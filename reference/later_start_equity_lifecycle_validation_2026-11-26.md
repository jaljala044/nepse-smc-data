# Later-Start Equity Lifecycle Validation — 2026-11-26

## Scope and evidence standard

Reviewed the 11 later-start candidates in the low-overlap triage register against dated secondary-provider listing/debut notices and the pinned `nepse-history-starter` OHLCV CSVs. Listing/commencement notices establish the published start date; the first positive-volume OHLCV row is a project-archive observation, not independent contract-level verification. No raw OHLCV was edited and no rows were synthesized.

## Results

| Symbol | Published trading commencement / debut | First positive-volume OHLCV row | Match / disposition |
|---|---|---|---|
| SAPIL | 2026-08-13 | 2026-08-13 (70 shares) | Match; ShareSansar commencement and Merolagani debut corroborate. |
| MEPDL | 2026-08-12 | 2026-08-12 (150) | Match; ShareSansar listing notice. |
| ECL | 2026-07-17 | 2026-07-17 (50) | Match; ShareSansar listing notice. |
| KAHL | 2026-07-02 | 2026-07-02 (200) | Match; ShareSansar commencement and Merolagani debut. |
| SGHL | 2026-07-02 | 2026-07-02 (410) | Match; ShareSansar commencement and Merolagani debut. |
| SNORL | 2026-06-26 | 2026-06-26 (70) | Match; secondary report explicitly describes first pre-open trade. |
| TPKHL | 2026-06-22 | 2026-06-22 (260) | Match; ShareSansar listing notice. |
| YMHL | 2026-06-22 | 2026-06-22 (140) | Match; ShareSansar listing notice. |
| APHL | 2026-06-09 | 2026-06-10 (110) | One-session discrepancy; commencement notice and archive first row differ. Verify 9 June executed trade / no-trade status using floorsheet or another independent daily record. |
| SOPL | 2026-06-08 | 2026-06-08 (390) | Match; ShareSansar notice and Merolagani debut. |
| KHPL | 2026-05-25 (notice) | 2026-05-26 (40) | One-session discrepancy; Merolagani reports debut on 26 May, consistent with archive. Preserve both the published scheduled commencement and observed first execution; 25 May execution status needs floorsheet confirmation. |

## Source evidence

- SAPIL: ShareSansar listing notice (2026-08-12; trading from 2026-08-13): https://www.sharesansar.com/eventdetail/listing-ipo-share-of-sarvottam-paints-industries-limited-sapil-2026-08-12 ; Merolagani debut (2026-08-13): https://merolagani.com/NewsDetail.aspx?newsID=129634
- MEPDL: ShareSansar listing notice (2026-08-11; trading from 2026-08-12): https://www.sharesansar.com/eventdetail/listing-ipo-share-of-mount-everest-power-development-limited-mepdl-2026-08-11
- ECL: ShareSansar listing notice (2026-07-16; trading from 2026-07-17): https://www.sharesansar.com/eventdetail/listing-ipo-share-of-everest-colour-limited-ecl-2026-07-16
- KAHL: ShareSansar listing notice (2026-07-01; trading from 2026-07-02): https://www.sharesansar.com/index.php/eventdetail/listing-ipo-share-of-kalanga-hydro-limited-kahl-2026-07-01 ; Merolagani debut: https://eng.merolagani.com/NewsDetail.aspx?newsID=128111
- SGHL: ShareSansar listing notice (2026-07-01; trading from 2026-07-02): https://www.sharesansar.com/eventdetail/listing-ipo-share-of-sanigad-hydro-limited-sghl-2026-07-01 ; Merolagani debut: https://eng.merolagani.com/NewsDetail.aspx?newsID=128111
- SNORL: first pre-open transaction report (2026-06-26): https://nepalisharemarket.com/news/IPO/snow-rivers-limited-snorl-commences-secondary-market-trading-with-first-transaction-in-pre-open-session
- TPKHL: ShareSansar listing notice (2026-06-19; trading from 2026-06-22): https://www.sharesansar.com/index.php/eventdetail/listing-ipo-share-of-taksar-pikhuwa-khola-hydropower-limited-tpkhl-2026-06-19
- YMHL: ShareSansar listing notice (2026-06-19; trading from 2026-06-22): https://www.sharesansar.com/index.php/eventdetail/listing-ipo-share-of-yambaling-hydropower-limited-ymhl-2026-06-19
- APHL: ShareSansar listing notice (2026-06-08; trading from 2026-06-09): https://www.sharesansar.com/eventdetail/listing-ipo-share-of-appolo-hydropower-limited-aphl-2026-06-08
- SOPL: ShareSansar listing notice (2026-06-05; trading from 2026-06-08): https://www.sharesansar.com/eventdetail/listing-ipo-share-of-sopan-pharmaceuticals-limited-sopl-2026-06-05 ; Merolagani debut (2026-06-08): https://cdn.merolagani.com/NewsDetail.aspx?newsID=127198
- KHPL: ShareSansar listing notice (2026-05-22; scheduled trading from 2026-05-25): https://www.sharesansar.com/eventdetail/listing-ipo-share-of-khpl-kalinchock-hydropower-limited-khpl-2026-05-22 ; Merolagani debut on 2026-05-26: https://merolagani.com/NewsDetail.aspx?newsID=126700

## Interpretation and controls

- Nine of 11 symbols have archive first positive-volume rows matching the published first-trading/debut date.
- APHL and KHPL remain one-session exceptions, not silently normalized. A scheduled commencement is not proof that an execution occurred that day.
- The project archive first row is not a substitute for contract-level floorsheet evidence. Keep all dates as secondary/project observations until independently corroborated.
- Earlier dates before verified/supported trading commencement should not count as missing OHLCV for these newly listed equities.
- This review does not certify exchange-session calendar completeness, all-row OHLCV quality, source lineage, data rights or canonical/training eligibility.
- No BUY eligibility or liquidity assessment is implied by lifecycle validation.

## Outcome

**Partial completion:** 9/11 lifecycle starts align with the project OHLCV first positive-volume row; APHL and KHPL require one-session floorsheet reconciliation. The 11 symbols can be removed from the generic low-overlap "unexplained archive gap" bucket for dates before their evidenced commencement, while the two boundary exceptions remain quarantined.
