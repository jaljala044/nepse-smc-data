# First-Trade Boundary Reconciliation — APHL, KHPL and Mid-2026 Equities — 2026-11-26

## Outcome

The apparent one-session archive-boundary discrepancies are now resolved for APHL and KHPL by dated reports describing the actual first matched transaction. Six other mid-2026 candidates align with reported first-trading/debut dates. These are secondary-source lifecycle validations plus project archive comparison, not exchange-authenticated raw floorsheet evidence.

## Boundary exceptions resolved

| Symbol | Published scheduled commencement | Actual first executed trade / debut | Project OHLCV first positive-volume row | Result |
|---|---|---|---|---|
| APHL | 2026-06-09 | 2026-06-10 | 2026-06-10, 110 shares | Match. Merolagani explicitly reports that no match occurred on 9 June and first trade matched on 10 June at Rs 299.70. |
| KHPL | 2026-05-25 | 2026-05-26 | 2026-05-26, 40 shares | Match. Merolagani reports first special pre-open transaction on 26 May at Rs 300. The 25 May date was scheduled commencement, not proof of execution. |

Evidence:
- APHL first transaction and failed match on scheduled day: https://www.merolagani.com/NewsDetail.aspx?newsID=127276
- APHL listing record: https://cdn.merolagani.com/AnnouncementDetail.aspx?id=66015
- KHPL first special pre-open transaction: https://eng.merolagani.com/NewsDetail.aspx?newsID=126700
- KHPL scheduled commencement: https://www.sharesansar.com/eventdetail/listing-ipo-share-of-kalinchock-hydropower-limited-khpl-2026-05-22

## Six mid-2026 candidates reconciled

| Symbol | Reported first-trading / debut date | Project archive first positive-volume row | Volume | Result |
|---|---|---|---:|---|
| SKHL | 2026-03-25 | 2026-03-25 | 90 | Match |
| BJHL | 2026-03-22 | 2026-03-22 | 80 | Match |
| SOHL | 2026-03-15 | 2026-03-15 | 860 | Match |
| HFIN | 2026-03-12 | 2026-03-12 | 150 | Match |
| SABBL | 2026-02-16 | 2026-02-16 | 180 | Match |
| RSML | 2026-02-16 | 2026-02-16 | 130 | Match |

Evidence:
- SKHL commencement notice: https://www.sharesansar.com/eventdetail/listing-ipo-share-of-super-khudi-hydropower-limited-skhl-2026-03-24
- BJHL debut: https://nepsebajar.com.np/news/enthusiastic-start-to-the-business-of-bhujung-hydropower
- SOHL debut: https://eng.merolagani.com/NewsDetail.aspx?newsID=124171
- HFIN debut: https://eng.merolagani.com/NewsDetail.aspx?newsID=124080
- SABBL and RSML debut: https://eng.merolagani.com/NewsDetail.aspx?newsID=123213

## Interpretation

- All eight symbols in this reconciliation have archive first positive-volume rows aligned with the actual first executed trade/debut date described by a dated secondary report.
- APHL and KHPL illustrate why scheduled commencement must not be treated as a guaranteed first execution date. A first-trade/no-match event may shift the actual debut.
- Earlier no-row dates before actual first execution must not be counted as missing OHLCV.
- This does not prove completeness of every later session, raw source lineage, contract-level floor sheets, corporate-action adjustments, or canonical/training eligibility.
- No raw OHLCV was changed, no missing rows were synthesized, and no canonical/training promotion was made.

## Next

1. Dedicated UNL historical source-coverage audit (project archive starts 2024-03-05 despite long-established listing).
2. Reconcile the remaining low-overlap group with symbol-specific executed-trade evidence.
3. Run full row-level OHLCV validation (date duplicates/order, OHLC bounds, zero/negative volume, price/volume/turnover anomalies, source hashes and timestamp provenance).
