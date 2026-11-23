# Supplemental NEPSE scanner data

Prepared for the November 20, 2026 session. Use these inputs with the existing ShareSansar price history. The supplements have separate paths and provenance.

| Input | Coverage |
| --- | --- |
| `broker_summary/YYYY-MM-DD.csv` | Gross buy/sell quantity and value by symbol, broker and session across 20 complete trading sessions, October 12–November 20. |
| `price_gap_fills/2026-07-24.csv` | 219 validated OHLCV rows for the archive's missing July 24 session. |
| `sectors.csv` and `sector_data.csv` | 281 dated ordinary-equity classifications and 1,534 daily sector bars across 12 sectors. |
| `benchmark_daily.csv` | 128 NEPSE benchmark bars through November 20. Volume is zero when unavailable in the benchmark export. |
| `corporate_actions.csv` | Three documented actions for LBBL, DORDI, and BNHC, with reference prices and factors. |
| `audit/` | Per-session reconciliation, July 24 exclusions, the pinned Aabishkar2 file audit, adjustment samples, the NLIC split review, and source versions. |

## Use in the Master Ranking Scanner

From the cloned `nepse-history-starter` repository, point the helper at the extracted scanner data folder containing `daily_prices.csv`:

```bash
python3 scanner_inputs/prepare_scanner_inputs.py /path/to/existing/data /path/to/new-data
```

The helper creates a new directory, combines the 20 broker partitions into `broker_summary.csv`, and inserts price records only when their symbol and date are missing. It supplies sector and corporate-action files where absent. Existing user-supplied CSVs for these datasets take precedence, including an existing floorsheet or broker table. When stock prices are added, weekly and monthly CSVs in the new copy are rebuilt by the scanner from daily candles so the recovered session is reflected in both periods. Run the master scanner with `--data-dir /path/to/new-data --as-of 2026-11-22` to use the November 20 close, include the completed week, and exclude November's unfinished monthly bar.

## Validation and provenance

**Broker data.** Each market-day source matches published totals for distinct contracts, shares, turnover to NPR 0.01, and traded symbols. Contract IDs stayed strings. All normalized row values use shares times trade price rather than rounded display amounts. Broker summaries retain both sides and aggregate per symbol per day. The raw sources, session statistics, and immutable blob identifiers are in `audit/floorsheet_reconciliation.csv` and `audit/source_coverage.json`. The November 20 source is the reconciled T+2 project tape. The other 19 are from the SocrateAI snapshot, supplied under the included MIT notice. Raw executions and time fields can be retrieved from those pinned sources. The 20-day market tape does not imply every symbol traded on all 20 dates.

**Viking gaps and Aabishkar2.** All 20 Viking floorsheets tested had fewer trades than the published session totals. The pinned Aabishkar2 commit contains 124 company files. Validation of all 233,328 rows identified 29,090 invalid OHLCV or turnover rows and 686 duplicate symbol-date rows, with those categories able to overlap. The latest date in that pin is November 26, 2024. Its current default branch has 372 company files, outside this pinned audit. Neither source entered the scanner inputs.

**July 24, 2026 price gap.** The exchange held a session and the starter archive had no stock prices for it. Of 353 symbols in the dated EOD file, 219 passed all checks. The symbol had to match existing archive coverage, all four prices had to match the independent unadjusted price export, and traded high, low, volume, and turnover had to match the reconciled raw tape. The tape supplies the trade count. The remaining 134 stayed out of the backfill. See the per-symbol reasons in `audit/price_gap_exclusions_2026-07-24.csv`. [July 24 session report](https://www.sharesansar.com/newsdetail/nepse-index-edges-up-by-788-points-on-last-trading-day-of-this-week-2026-07-24)

**Adjustments and splits.** The vendor-adjusted export lacks a documented event-level methodology. The sample includes a BNHC rights event where the adjusted and raw pre-event rows are identical and a DORDI case where the adjusted close moved to the declared base on the notice date while the raw session had already closed on the earlier basis. A dated bonus/rights notice plus a matching archived reference close supports each of the three rows in `corporate_actions.csv`. The event date is the first observed ex-adjustment trading bar in the starter archive. The factor is the announced adjusted base divided by the reference close. The file is a verified sample with incomplete event coverage and does not reprice history. Nepal Life’s proposed 2-for-1 split is in the audit only. The subsequent 2024/25 issuer report still reports NPR 100 par value, and an effective split was not verified.

**Sector data.** Classification uses a dated YONEPSE security list cross-checked against the November 20 security reference. The mapping records both sources row by row. Daily index bars use YONEPSE history and closing candles from Nepse Decode where available. Historical sector memberships before November 20 remain unverified. [Sector archive](https://github.com/Shubhamnpk/yonepse/tree/e5798a24549ef80d37c6531c690c7a16120971e5/data/indices/monthly) · [Closing index candles](https://github.com/srijankarki07/nepse-data/tree/e6e6fe77cd3378204c7938e66601cee2339a8b7a/data/indices)

## November 22, 2026 backfill

The most recent verified market date is November 20, 2026. This pass added **20 broker session files** from July 24 and September–October, based on 1,062,269 reconciled trades. A follow-up review resolved the September 16 discrepancy against the dated per-security export and independent GCIL trades. The broker folder now contains 41 reconciled sessions. [September 16 reconciliation](audit/reconciliation_2026-09-16.json). Brokers are aggregated by date, symbol and broker; count the buy side or the sell side when reconciling market totals.

- `market_summary_daily.csv` has 195 sessions in 2026 with exact shares, turnover and traded-security counts cross-checked against dated EOD exports or complete tapes. Transaction counts appear only on tape-reconciled dates. November 20 breadth is the official ordinary-equity universe of 279 symbols (89 advancing, 181 declining, 9 unchanged), cross-checked against published previous closes. Breadth for the other days is blank.
- `benchmark_daily.csv` and `sector_data.csv` have 10 and 24 additional bars, respectively. `index_history/ohlc.csv` holds 105 full bars for Sensitive, Float, Sensitive Float and Mutual Fund. Full OHLC requires both sources to agree to two decimal places. `index_history/closes_only.csv` holds 1390 other verified closing levels. Those rows are distinct from all OHLC files. They should be used for close-based analysis. They carry no assumed open, high, low or volume.
- Two verified debenture OHLCV rows were added to July 24 after exact OHLC comparison and matching the trades for high, low, volume and turnover. All existing price records were compared on symbol/date keys before backfill. 132 July 24 candidates and the four out-of-range November 20 debenture candles remain unfilled. Earlier gaps outside the 40 stock dates checked in this pass are still open.
- `audit/backfill_manifest_2026-11-22.json` pins the sources and counts. Companion CSVs detail broker and stock rejections and the market reconciliation. The existing raw archive remains a historical source. The original scanner extraction excludes non-session records according to its pinned session calendar.

Data candidates checked: `ghimiresunil/Nepse-Web-Scraper` has an undated price snapshot with no opening prices. The 11 published `sujanchhetri/NEPSE_scraper` JSON snapshots have no session-date field. `polymorphisma/nepse_scraper` and its PyPI release distribute software. Pepy reports software downloads. SocrateAI's metadata folder only contains `.gitkeep`. Older data from the [Hugging Face floorsheet and index archive](https://huggingface.co/datasets/urekmazino69/Nepse-floorsheet-and-indices) and [AnkitSanjyal's dataset](https://huggingface.co/datasets/AnkitSanjyal/nepse-market-data) were considered by their published coverage. This backfill uses pinned files with independently checked records.
