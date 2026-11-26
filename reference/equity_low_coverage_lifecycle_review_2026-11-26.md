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
| NLO | 3.11% (7/225) | Merolagani announcement dated 2026-11-25 reports NLO bonus shares listed in NEPSE. ShareSansar has a historical 2018 trading suspension notice; this does not establish a current suspension. | Archive contains only 43 rows and ends 2026-09-30, despite a later 2026-11-25 corporate-action listing notice. | **High-priority archive freshness/provenance exception.** Do not label NLO delisted or currently suspended. Obtain current NLO EOD/floorsheet and establish why the archive stops at 2026-09-30. |
| BNL | 50.67% (114/225) | ShareSansar reports NEPSE suspended BNL on 2024-12-17 and lifted the suspension on 2024-12-18. | Archive has no row on 2024-12-17/18; first nearby row after 2024-12-16 is 2024-12-23. Archive continues to 2026-11-19. | **Event partially explained; remaining low overlap unresolved.** The two-day suspension is not sufficient evidence to explain all missing reference dates. Do not infer a missing-price defect from absent rows alone. |
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

**Partial milestone progress — 1 merger-suspension window corroborated; 1 current archive-staleness exception identified; 1 temporary suspension documented but low coverage remains unresolved.** No symbol is promoted to canonical/training status by this review.
