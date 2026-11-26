# RHGCL 2026-11-19 unresolved OHLCV conflict — secondary-source check

Date checked: 2026-11-26  
Symbol/date: RHGCL / 2026-11-19

## Repository conflict

- `nepse-smc-data`: Open 252.10, High 259.50, Low 252.10, Close 256.00, Volume 4,216.
- `nepse-history-starter`: Open 252.10, High 259.50, Low 252.10, Close 258.00, Volume 9,054.

## Secondary-source findings

Three currently indexed third-party price-history sources report the Starter-side close and volume:
- ArthaKendra RHGCL price history: Nov 19, 2026 — Open 252.1, High 259.5, Low 252.1, Close 258, Volume 9,054. https://arthakendra.com/stock-market/company/RHGCL/price-history
- QuantNepal RHGCL page: Nov 19, 2026 — Close 258, range 252.10–259.50, volume 9,054. https://www.quantnepal.com/nepse/RHGCL
- StockNepals RHGCL price history: 2026-11-19 — Open 252.10, High 259.50, Low 252.10, Close 258.00, Volume 9,054. https://www.stocknepals.com/stock-details/RHGCL

These sources agree with `nepse-history-starter` and conflict with the `nepse-smc-data` row. They are secondary websites and may share upstream data; this is not proof of three independent primary records.

## Disposition

**Do not overwrite the SMC row or promote the Starter row as official.** Preserve both repository versions and keep the record quarantined until a dated official NEPSE daily-price record or contract-level floorsheet evidence is acquired. Secondary-source consensus is a lead for the next acquisition step, not an official resolution.

## Archived NEPSE security-history response

The [P1 evidence capture commit](https://github.com/jaljala044/nepse-elite-ai-scanner-pro/commit/a6fb03d8d1f5788fb11ba0f138eabfd1191713fd) contains the response for NEPSE security ID `8108`. The raw response has SHA-256 `bdef0c738c4fd53d814b2c525b0202f36be36479e1cd3d7b5a109e8311aad700`, matching the capture manifest. Parsing the response yielded exactly one row for 19 November 2026.

| Field | Captured value |
| --- | ---: |
| High (NPR) | 259.50 |
| Low (NPR) | 252.10 |
| Close (NPR) | 258.00 |
| Traded quantity | 9,054 |
| Trades | 47 |
| Turnover (NPR) | 2,332,952.50 |

The captured close and quantity match History Starter. The independently calculated totals from the existing floorsheet extract match the 47 trades, quantity and turnover. The NEPSE security-history response does not include an opening price. Both repositories report an open of NPR 252.10, which has not been independently verified from the captured primary response. Preserve both source rows and keep the complete candle out of canonical use until the opening price and evidence acceptance are reviewed.
