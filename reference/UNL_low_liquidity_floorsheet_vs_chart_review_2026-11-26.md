# UNL low-liquidity chart and floorsheet review — 2026-11-26

## Question

Can some repeated UNL OHLCV rows or date gaps reflect days with no matched trades, rather than erroneous exchange sessions or fabricated data?

## Finding

**Yes — this is a credible explanation and must be tested before rejecting UNL rows.** UNL has sparse trade activity compared with ordinary liquid equities. A price-history chart may only display dates on which a transaction/bar was recorded, while a provider may separately fill missing dates with prior OHLCV values. A repeated row on an exchange-open date is therefore not automatically an executed trade or a bad trade record.

This review found public floorsheet-derived daily summaries that list only a subset of recent NEPSE sessions for UNL. That pattern is consistent with no-trade sessions, but the public page does not expose the complete 20-session date-by-date zero-trade ledger. Accordingly, zero trades are not yet conclusively assigned to each missing date.

## Public chart and floorsheet observations

### Recent UNL trade sessions (NEPSE Quant; floorsheet-derived)

Source: https://nepsequant.com/stocks/UNL/brokers
The page states "Last 20 sessions to 2026-11-25" and reports the following UNL sessions:

| Session | Shares | Value |
|---|---:|---:|
| 2026-11-25 | 310 | Rs 1.48 crore |
| 2026-11-24 | 72 | Rs 35.02 lakh |
| 2026-11-23 | 332 | Rs 1.58 crore |
| 2026-11-20 | 50 | Rs 24.09 lakh |
| 2026-11-19 | 80 | Rs 38.54 lakh |
| 2026-11-18 | 43 | Rs 20.71 lakh |
| 2026-11-17 | 30 | Rs 14.62 lakh |
| 2026-11-13 | 40 | Rs 19.44 lakh |
| 2026-11-06 | 340 | Rs 1.65 crore |
| 2026-11-05 | 100 | Rs 47.97 lakh |

The page's 20-session window contains only 10 UNL trade dates in its displayed recent-session list. The unlisted dates are **candidate no-trade sessions**, not yet certified no-trade sessions, because the page does not publish an explicit zero row or the complete date-level query response.

### Direct floorsheet contract evidence

Source: https://nepsequant.com/floorsheet
For 2026-11-25, the NEPSE floorsheet rendering shows an UNL contract:
- Buyer broker 34; seller broker 38
- Quantity 300
- Rate Rs 47,800
- Amount Rs 1.43 crore

This is direct contract-level third-party rendering of NEPSE floorsheet data. It independently establishes at least 300 shares traded on 25 Nov. The UNL daily total is 310 shares; the difference may consist of additional smaller contracts and must not be reverse-engineered without the complete contract list.

### 2026-11-26 cross-check

Punji's public UNL monthly/datewise data reports 40 shares for 26 Nov 2026, with open Rs 47,500.10, high Rs 47,750, low Rs 47,500.10 and close Rs 47,500.10. A separate UNL broker-activity rendering lists five brokers and a total of eight reported trades on that date. These are third-party representations of exchange activity, not a project-captured raw official response.

### Chart-date behaviour

- NEPSE Analysis describes its UNL chart as settled daily bars from NEPSE, with history back to 2012: https://nepseanalysis.com/chart/UNL
- NEPSEDATA's public UNL history is sparse by calendar date (for example, the visible recent date rows omit many intervening weekdays), consistent with a transaction-date rather than a calendar-day series: https://nepsedata.com/stock/UNL/
- A date omitted from a sparse chart is not sufficient on its own to prove the exchange was open and UNL had zero trades; exchange session status and full floorsheet completeness must also be known.

## Implications for the 845-row project archive

The earlier audit found:
- 845 rows and no duplicate date keys;
- 302 consecutive rows that repeat the preceding row's exact OHLCV;
- 226 dates that fall on non-session weekdays under the currently applied two-regime weekday rule.

The 302 repeated-value rows must now be split into separate hypotheses:
1. Genuine no-trade day with provider forward-filled prior OHLCV;
2. Duplicate/stale provider response assigned to a new date;
3. Real trade at exactly the same OHLC values (possible but requires floorsheet corroboration);
4. Other ingestion/date-label defect.

Do **not** automatically delete, shift, interpolate, or treat repeated rows as executed OHLCV. Do not infer that a row is valid merely because it is on a weekday. Do not infer no trade merely because it is absent from a chart.

## Required date-level verification procedure

For every UNL row in the 845-row archive:

1. Determine whether NEPSE was open on that exact date using the official session/holiday evidence layer.
2. Acquire the complete floorsheet for that date, with response status, pagination/record count, retrieval timestamp and raw-byte hash.
3. Search every page/record for exact symbol `UNL` (not UNLB or similarly named securities).
4. If at least one UNL contract exists, aggregate quantity, turnover, min/max price and contract count; compare to the project's daily OHLCV.
5. If the full session floorsheet is complete and contains zero UNL contracts, label `NO_UNL_TRADE_CONFIRMED`; a copied prior-day OHLCV row is then a provider carry-forward, not a traded daily bar.
6. If floorsheet is incomplete, inaccessible, or the session date is uncertain, label `UNVERIFIED`.
7. Preserve raw archive rows unchanged. Store the classification in a separate reconciliation table. Do not synthesize OHLCV bars for no-trade dates.

## Disposition

- Revised interpretation: low liquidity/no-trade dates are a plausible and important explanation for some UNL repeated OHLCV rows.
- Confirmed public trade evidence: 25 Nov 2026 (at least 300-share contract; daily aggregate 310); 26 Nov 2026 (third-party daily aggregate 40 shares).
- The 10 recent-session rows listed by NEPSE Quant are positive-trade evidence; the other dates in its 20-session window remain candidate no-trade dates pending complete floorsheet verification.
- Historical UNL archive remains QUARANTINE / LOW CONFIDENCE for canonical OHLCV, indicators, backtests and training until date-level reconciliation is complete.
- No raw rows changed, no price splicing, no synthetic bars, and no promotion authorized.
