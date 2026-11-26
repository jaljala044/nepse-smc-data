# Mid-2026 Low-Overlap Equity Archive Boundary Review — 2026-11-26

## Scope

Inspected the first and last records in the pinned `nepse-history-starter/03_stock_charts_ohlcv` files for PCIL, SIPD, SKHEL, RLEL, SKHL, BJHL, SOHL, HFIN, SABBL, RSML and UNL. First rows are archive observations with positive volume; they are not independent floorsheet verification.

## Archive boundary observations

| Symbol | First row | First-row volume | Last row | Interpretation |
|---|---|---:|---|---|
| PCIL | 2026-04-10 | 250 | 2026-11-20 | Matches published trading commencement (10 Apr). |
| SIPD | 2026-04-10 | 140 | 2026-11-20 | Matches published trading commencement (10 Apr). |
| SKHEL | 2026-03-29 | 80 | 2026-11-20 | Matches reported first special pre-open trade (29 Mar). |
| RLEL | 2026-03-29 | 190 | 2026-11-20 | Matches reported first special pre-open trade (29 Mar). |
| SKHL | 2026-03-25 | 90 | 2026-11-20 | Archive first row is one day after the published 24 Mar listing/commencement reference; confirm exact first execution. |
| BJHL | 2026-03-22 | 80 | 2026-11-20 | Archive boundary requires reconciliation against the published March 19 listing/commencement reference; do not assume intervening trade days. |
| SOHL | 2026-03-15 | 860 | 2026-11-20 | Archive begins after the 12 Mar listing/commencement reference; confirm exact first executed date. |
| HFIN | 2026-03-12 | 150 | 2026-11-20 | Archive begins after the 11 Mar listing reference; confirm 12 Mar commencement and first execution. |
| SABBL | 2026-02-16 | 180 | 2026-11-20 | Archive starts after the 13 Feb listing reference; first execution date requires confirmation. |
| RSML | 2026-02-16 | 130 | 2026-11-20 | Archive starts after the 13 Feb listing reference; first execution date requires confirmation. |
| UNL | 2024-03-05 | 20 | 2026-11-20 | Long-established issuer but archive begins only in Mar 2024; dedicated historical coverage/source audit required. |

## External lifecycle evidence located

- PCIL: ShareSansar notice says trading commencement 2026-04-10: https://www.sharesansar.com/eventdetail/listing-ipo-share-of-palpa-cement-industries-limited-pcil-2026-04-09
- SIPD: ShareSansar notice says trading commencement 2026-04-10: https://www.sharesansar.com/index.php/eventdetail/listing-ipo-share-of-shikhar-power-development-limited-sipd-2026-04-09
- SKHEL and RLEL: Merolagani reports first special pre-open transactions on 2026-03-29: https://www.merolagani.com/NewsDetail.aspx?newsID=124637
- SKHEL: listing/trading notice reported 2026-03-26 / 2026-03-29: https://www.displtd33.com/category/news/page/11/
- RLEL: listing/trading notice reported 2026-03-25 / 2026-03-26: https://www.displtd33.com/category/news/page/11/
- SKHL, BJHL, SOHL, HFIN, SABBL and RSML: IPO/listing date index records are available in NEPSE Insights and NepsezAI; these are secondary index records and are not treated as proof of first executed trade: https://nepseinsights.com/ipo-fpo-right ; https://nepsezai.com/en/ipo
- UNL: ShareSansar documents a prior trading suspension and resumption in September 2018, but this does not explain why the current project archive starts in March 2024: https://www.sharesansar.com/newsdetail/nepse-resumes-trading-of-unilever-nepal-advises-the-company-to-follow-the-regulations

## Findings

1. PCIL and SIPD archive first rows align with published commencement.
2. SKHEL/RLEL have direct secondary reports of first pre-open trades on 29 March, matching the archive first rows.
3. SKHL, BJHL, SOHL, HFIN, SABBL and RSML have first archive rows after published listing or scheduled commencement references. A listing date is not necessarily a first execution date; retain these as boundary-review exceptions pending dated trade evidence.
4. UNL is not a new listing. Its March 2024 archive start is a source-history boundary issue and must not be interpreted as the company's listing date or lifecycle start.
5. No dates/rows were inserted, deleted, or normalized. No zero-volume candles were created. No canonical/training promotion.

## Next actions

- Obtain date-specific floorsheet or independent EOD evidence for SKHL, BJHL, SOHL, HFIN, SABBL and RSML around the archive boundaries.
- Confirm no-trade vs archive omission on intervening sessions; do not infer from weekend/weekday alone.
- Audit UNL across alternate providers and repository history to identify whether pre-March-2024 OHLCV is available, its provenance, and any missing period.
- Continue full row-level OHLCV validation across both source archives and all 281 target equities.
