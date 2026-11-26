# NLO Sparse-Trading vs Archive-Staleness Review — 2026-11-26

## Executive result

**The available evidence does not support classifying NLO's 2026-09-30 latest OHLCV trade as a stale-collector failure.** The 43-row NLO OHLCV file appears to be a trade-only series with very infrequent executed trades. Multiple third-party market views show zero trades / zero volume on later sessions while carrying forward the last traded close of NPR 279.40. NLO should be classified as an active but exceptionally illiquid / no-recent-trade equity, not delisted and not automatically missing OHLCV rows.

This is a source-reconciliation finding, not proof of every no-trade date. Do not manufacture zero-volume OHLC candles into the raw trade-only OHLCV archive.

## Repository evidence

- Current security snapshot row: `NLO, security ID 198, Nepal Lube Oil Limited, status A, snapshot date 2026-11-25`.
- Snapshot source SHA-256: `eed3bbb3152e83d4abcb0ee8d03d720c33c63cef`.
- Raw OHLCV path: `03_stock_charts_ohlcv/NLO_OHLCV.csv`.
- Raw OHLCV Git blob SHA: `c2b20336006365be07ab362a5e438427e689ee5b`.
- 43 executed-trade rows; latest dated trade: 2026-09-30, OHLC 279.40/279.40/279.40/279.40, volume 60.
- Same blob SHA appears in `jaljala044/nepse-history-starter` and `jaljala044/nepse-smc-data`; this confirms byte-identical copies, not independent source provenance.

## No-trade corroboration

1. Hamroshare's NLO page for 2026-11-25 reports close NPR 279.40, no trades, no volume and no turnover. Its recent-price history shows 30 September as the latest executed trade (volume 60), followed by older sparse trade dates.
2. Sajilo Trading's NLO page says no trade in the 25 November 2026 session and identifies 30 September as the last trade date, with close NPR 279.40 and volume 60.
3. QuantNepal's NLO daily history reports zero volume and unchanged NPR 279.40 on 1 October through the displayed November dates, including 25 and 26 November 2026.
4. The project archive's 2026-11-25 EOD audit reports 356 traded securities. NLO is absent from the 25 November price-gap-fill rows and broker-summary rows. The floorsheet audit records 52,669 contracts across 356 securities. These are consistent with no NLO execution that day, although absence in a summary is not a substitute for the raw exchange tape.
5. ShareSansar's 25 November bonus-share listing report states NLO closed at NPR 279.40; that does not establish a trade occurred that day.

## Corporate-action discrepancy — do not adjust prices yet

The listing event is independently visible across providers, but the quantity / ratio fields are inconsistent:
- ShareSansar reports 1,363,637 bonus units listed and describes the FY 2081/82 approved distribution as 20% bonus plus 1.05264% cash (total dividend 21.05264%).
- ShareHub and one Merolagani announcement rendering show 145,725.36 units; Merolagani renderings conflict between 15% and 20%.
- Hamroshare's company page currently describes FY 2082/83 as 15% bonus plus 6.053% cash, a different fiscal-year announcement context.

The source records may refer to different events / fiscal years or contain provider errors. The project must not infer a single adjustment factor or rewrite historical OHLCV from these inconsistent summaries. Obtain the actual NEPSE listing notice / company notice and reconcile fiscal year, book-close date, ratio, quantity and effective adjustment date before any adjusted-price series is produced.

## Classification and scanner controls

| Field | Decision |
|---|---|
| Security identity | Current active NLO, ID 198 (snapshot evidence) |
| Last verified trade in project OHLCV | 2026-09-30, volume 60 |
| Last close carried by secondary pages | NPR 279.40 |
| Subsequent session status | No-trade / zero-volume reported; not a new executed OHLCV bar |
| Liquidity | **Very poor / not suitable for ordinary scanner BUY eligibility** until repeated execution and adequate turnover return |
| Data quality | Medium for sparse-trading interpretation; low for corporate-action adjustment details |
| Canonical/training | No new promotion; retain raw trade-only history |
| Price adjustment | Blocked pending primary listing / corporate-action record |

Scanner rules:
- Preserve executed-trade OHLCV rows as-is.
- Represent no-trade session observations, if needed, in a separate session-status sidecar with source, timestamp, symbol, and explicit `no_trade_reported` status; do not copy prior close into Open/High/Low/Close as if it were a trade.
- Do not treat carried-forward last price as fresh momentum, a breakout, an executable quote, or evidence of liquidity.
- Exclude NLO from BUY candidate ranking while it lacks recent execution and reliable liquidity. Existing holders should treat exits as execution-risk constrained; do not promise a fill at the carried-forward price.
- Do not use the bonus listing date as a trading date or assume a price adjustment without resolving the corporate-action discrepancy.

## Sources

- Hamroshare NLO, 25 Nov 2026: https://hamroshare.com.np/company/NLO
- Sajilo Trading NLO: https://trading.sajiloapps.com/company/nlo
- QuantNepal NLO history: https://www.quantnepal.com/nepse/NLO
- ShareSansar bonus listing report, 25 Nov 2026: https://www.sharesansar.com/newsdetail/bonus-shares-of-nepal-lube-oil-limited-listed-on-nepse-2026-11-25
- ShareHub announcement, 25 Nov 2026: https://sharehubnepal.com/
- Merolagani announcement: https://merolagani.com/AnnouncementDetail.aspx?id=68565
- Project 25 Nov EOD audit: `jaljala044/nepse-history-starter/scanner_inputs/audit/eod_2026-11-25.json`
- Project 25 Nov floorsheet audit: `jaljala044/nepse-history-starter/scanner_inputs/audit/floorsheet_2026-11-25.json`
- Project NLO OHLCV: `jaljala044/nepse-smc-data/03_stock_charts_ohlcv/NLO_OHLCV.csv`

## Conclusion

**Reclassify NLO from suspected stale archive to confirmed sparse-trading / no-recent-execution exception (medium confidence).** The historical trade-only OHLCV file is not to be padded with zero-volume candles. The independent corporate-action quantity/ratio discrepancy remains open and must be resolved before adjusted-price research.
