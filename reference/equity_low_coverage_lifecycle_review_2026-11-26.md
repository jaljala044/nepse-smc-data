# Equity Low-Coverage Lifecycle Review — 2026-11-26

## Scope

Supplement to `equity_observed_date_coverage_audit_2026-11-26.md`. This review investigates three high-priority low-overlap symbols (NLO, BNL, PFL) against the pinned OHLCV archive and dated secondary-provider notices. It is not a full session-completeness audit and does not modify raw OHLCV.

## Evidence reviewed

- `jaljala044/nepse-history-starter/03_stock_charts_ohlcv/NLO_OHLCV.csv`: 43 data rows; latest row 2026-09-30.
- `jaljala044/nepse-history-starter/03_stock_charts_ohlcv/BNL_OHLCV.csv`: 605 data rows; latest row 2026-11-19.
- `jaljala044/nepse-history-starter/03_stock_charts_ohlcv/PFL_OHLCV.csv`: 889 data rows; latest row 2026-11-20.
- Existing 281-symbol observed-date overlap report and CSV.
- ShareSansar and Merolagani dated notices linked below.

## Findings

| Symbol | Observed-date overlap | Lifecycle / event evidence | OHLCV observation | Disposition |
|---|---:|---|---|---|
| NLO | 3.11% (7/225) | Merolagani, ShareSansar and ShareHub report bonus-share listing on 2026-11-25. Hamroshare, Sajilo Trading and QuantNepal report zero trades/volume on later sessions and last executed trade 2026-09-30. | 43 executed-trade rows; latest 2026-09-30, volume 60. Project 2026-11-25 EOD/floorsheet summaries show 356 traded securities and NLO absent from broker and price-gap-fill rows. | **Reclassified: sparse-trading / no-recent-execution exception (medium confidence), not proven stale collector.** Do not pad OHLCV with zero-volume candles. Exclude from BUY eligibility until repeated execution/liquidity returns. Bonus quantity/ratio conflict remains unresolved; no price adjustment. See [NLO review](NLO_sparse_trading_vs_archive_staleness_review_2026-11-26.md). |
| BNL | 50.67% (114/225) | ShareSansar reports NEPSE suspended BNL on 2024-12-17 and lifted suspension on 2024-12-18. NepView and Sajilo independently report a 2026-11-23 trade (NPR 14,600, volume 10); Hamroshare and Sajilo report no trade on 2026-11-25. | Project archive ends 2026-11-19. A 2026-11-23 trade is absent; ArthaKendra additionally reports a 2026-11-24 trade (volume 10), but that row is single-source. | **Confirmed archive freshness/coverage gap on 2026-11-23;** 2026-11-24 remains provisional. BNL is active but very illiquid; exclude from ordinary BUY eligibility. See [BNL reconciliation](BNL_sparse_history_and_missing_trade_reconciliation_2026-11-26.md). |
| PFL | 78.67% (177/225) | ShareSansar reports PFL/SFCL trading suspension effective 2026-07-10 for merger integration. ShareSansar reports post-merger PFL shares listed on 2026-09-15, with first-transaction open price range NPR 366.58. | PFL archive has rows through 2026-07-09, then next row 2026-09-16; the gap aligns with the reported merger suspension and relisting sequence. | **Merger interval corroborated by secondary notices.** Preserve the raw history; tag the 2026-07-10 to 2026-09-15 interval as a documented corporate-action/trading-suspension window for review. Do not splice SFCL prices into PFL or assume the old PFL series is fully comparable without corporate-action review. |

## Source links

- NLO bonus-share listing announcement, Merolagani, 2026-11-25: https://merolagani.com/AnnouncementDetail.aspx?id=68565
- NLO historical trading suspension report, ShareSansar, 2018-12-03: https://www.sharesansar.com/index.php/newsdetail/trading-of-nadep-laghubitta-and-nepal-lube-oil-has-been-suspended-by-nepse-due-to-delay-in-notification-of-dividend-decision
- BNL suspension, ShareSansar, 2024-12-17: https://www.sharesansar.com/newsdetail/nepse-suspends-bottlers-nepal-limited-shares-calls-for-response-in-3-days-2024-12-17
- BNL release, ShareSansar, 2024-12-18: https://www.sharesansar.com/newsdetail/bottlers-nepal-limited-resumes-securities-trading-following-regulatory-compliance-2024-12-18
- PFL/SFCL suspension, ShareSansar, 2026-07-09: https://www.sharesansar.com/newsdetail/nepse-suspends-trading-of-pokhara-finance-and-samriddhi-finance-shares-ahead-of-merger-2026-07-09
- PFL post-merger listing, ShareSansar, 2026-09-15: https://www.sharesansar.com/index.php/eventdetail/listing-shares-of-pokhara-finance-limited-pfl-after-merger-2026-09-15

## Controls and unresolved work

1. Keep all source OHLCV files immutable. Any corrected or normalized date series must be a separate derived artifact with source hash, raw row, correction rationale, and review status.
2. Do not equate no OHLCV row with a closed exchange session. It may reflect no trade, instrument suspension, source omission, or an incomplete archive.
3. Do not use the sampled security ID 8108's 225 observed dates as a universal expected-session denominator for every equity.
4. NLO requires a current provider extract and archive provenance investigation.
5. BNL requires a symbol-specific trading/activity history to explain the broader sparse overlap.
6. PFL's merger suspension window is supported by secondary notices, but the historical series still requires corporate-action/price-continuity treatment before indicators, returns, or backtests cross the event.
7. Full row-level quality validation across all 281 target equities and both OHLCV repositories remains a separate gate.

## Outcome

**Partial milestone progress — PFL merger-suspension window corroborated; BNL's 2026-11-23 missing trade confirmed against two third-party sources (24 Nov provisional); NLO reclassified as sparse trading / no recent execution rather than a proven stale archive.** NLO's corporate-action ratio/quantity conflict remains unresolved. No symbol is promoted to canonical/training status by this review.
