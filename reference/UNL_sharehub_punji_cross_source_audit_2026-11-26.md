# ShareHub and Punji UNL Data Cross-Check — 2026-11-26

## Scope
Point-in-time public-page comparison for UNL (Unilever Nepal Limited), prompted by the ongoing UNL historical-data quarantine. This is a source-quality audit, not a live trading signal and not a full historical OHLCV acquisition. No raw project data was changed and no provider data was ingested.

## Findings

### 1. Identity and listing metadata
- ShareHub and Punji both identify the instrument as UNL / Unilever Nepal Limited, Manufacturing and Processing, listed 1994-09-22.
- Both display 920,700 listed shares.
- This agrees with the company's published shareholder/registrar information.

### 2. Ownership: ShareHub fails its own consistency check
- Punji reports 85% promoter / 15% public.
- ShareHub's structured ownership widget reports 0 promoter / 100% public (920,700 public shares).
- On the same ShareHub page, the narrative says 80% Hindustan Unilever + 5% Sibkrim + 15% public, i.e. 85% promoter / 15% public. The same page therefore contradicts its own ownership widget.
- Unilever Nepal's official shareholder/registrar document states 85% promoter / 15% public, with 782,595 promoter shares and 138,105 public shares. Its 2024 annual report breaks promoter holding into 80% Hindustan Unilever and 5% Sibkrim.
- Disposition: accept 85% / 15% as the corroborated ownership structure for this audit. Reject ShareHub's 0% / 100% structured ownership fields. Do not use ShareHub's reported float market cap as a free-float measure until corrected.

### 3. Price snapshot: date alignment required
- ShareHub search-indexed page reports 2026-11-25 14:05 NPT: LTP/close Rs 47,500.10, open Rs 47,800, high Rs 47,800, low Rs 47,500.10, previous close Rs 48,600, volume 310, turnover Rs 14,815,001, 2 trades.
- Punji reports the 2026-11-26 close: Rs 47,500.10, open Rs 47,500.10, high Rs 47,750, low Rs 47,500.10, previous close Rs 47,500.10, volume 40.
- These are different session dates. They must not be treated as a same-day mismatch. The identical 47,500.10 close on adjacent dates is plausible but should be reconciled to date-keyed NEPSE EOD records/floorsheet before ingestion.
- Punji's monthly table reports November 2026 through 26 Nov: 14 sessions, 1,597 shares, month open 49,150, high 49,150, low 47,500, close 47,500.10. This aggregate is not a substitute for daily bars.
- ShareHub's indexed current page reports the 25 Nov snapshot, while an opened cached page returned stale 10 Aug 2026 data. This demonstrates that page/cache timestamps must be captured and validated; do not scrape an undated cached response as current.

### 4. Corporate actions and fundamentals
- Punji lists FY 2082/83 cash dividend 1540%, book close 25 Nov 2026, and FY 2081/82 cash dividend 1842%, book close 28 Oct 2025.
- ShareHub's indexed page shows the 1540% cash dividend for FY 2082/83 and the same 25 Nov 2026 book-close date.
- The dividend event is a price-adjustment / entitlement boundary for point-in-time return calculations. Confirm against official company/NEPSE notices before applying any adjustment. No adjustment or historical price rewrite is authorized by this audit.
- Current financial metrics differ between providers (e.g. EPS, PE, book value and yield). They may use different fiscal periods, trailing vs reported EPS, or adjustment methods. Do not combine fields without recording metric definition, fiscal period, publication date and calculation basis.

### 5. Broker flow and liquidity
- Punji displays Rs 16.48 crore across 43 brokers for its stated last-30-day window and explicitly warns that broker-level execution does not identify the underlying client/investor.
- This is an aggregated provider display, not verified client accumulation, ownership, or manipulation evidence. Do not infer operator activity or use it as a standalone broker-footprint BUY signal.
- The provider page's 30-day window and the page's broader 12-month record are different populations; preserve the exact window with every metric.
- No raw daily broker-level rows, contract-level floorsheets, or independently hashed response payloads were acquired in this check.

## Data-quality disposition
| Field | ShareHub | Punji | Audit decision |
|---|---|---|---|
| Symbol/name/sector/listing date | Consistent | Consistent | Reference metadata only |
| Listed shares | 920,700 | 920,700 | Consistent; verify against company record |
| Promoter/public split | 0/100 widget; narrative says 85/15 | 85/15 | Use 85/15 corroborated by company source; quarantine ShareHub widget |
| 25 Nov 2026 EOD | 47,500.10; volume 310; 2 trades | Not compared here | ShareHub third-party snapshot; verify raw exchange record |
| 26 Nov 2026 EOD | Not established by retrieved ShareHub snapshot | 47,500.10; volume 40 | Punji third-party snapshot; verify raw exchange record |
| Full-listing daily OHLCV | API documented; authenticated ALL retrieval not completed | No bulk raw export acquired | Not eligible as canonical historical feed |
| Dividend | 1540% / book close 25 Nov 2026 | Same | Corporate-action candidate; official notice required |
| Broker flow | Not independently acquired | Aggregated 30-day display | Context only; not a manipulation/ownership signal |

## Source provenance
1. ShareHub UNL page: https://sharehubnepal.com/company/UNL
2. ShareHub Data API documentation: https://sharehubnepal.com/data/nepse-data-documentation/
3. Punji UNL page: https://punji.app/stocks/UNL
4. Punji terms (market data sourced from public NEPSE endpoints and reformatted): https://punji.app/terms
5. Unilever Nepal shareholder/registrar information: https://www.unilevernepal.com/files/92ui5egz/production/62237a66ba2273e5d714506c42f583a864d314b1.pdf
6. Unilever Nepal 2024 annual report: https://www.unilevernepal.com/files/unilever-nepal-limited-annual-report-2024-english.pdf
7. Unilever Nepal annual compliance report 2025: https://www.unilevernepal.com/files/annual-compliance-report-on-corporate-governance-7th-october-2025.pdf

## Final disposition
- ShareHub and Punji are approved as secondary cross-check/reference sources, not yet approved as canonical raw-history feeds.
- ShareHub UNL ownership widget: REJECT / QUARANTINE due direct contradiction with the company disclosure and its own narrative.
- Punji ownership split: corroborated by official company disclosure.
- Price snapshots: date-keyed secondary observations only; reconcile each session to primary NEPSE EOD/floorsheet before canonical use.
- Punji broker-flow summary: contextual only; no ownership/manipulation inference.
- UNL historical OHLCV remains quarantined under the existing decision. No historical splicing, synthetic rows, or backtest/training promotion.
- This source audit does not block eligible non-UNL equities from progressing.
