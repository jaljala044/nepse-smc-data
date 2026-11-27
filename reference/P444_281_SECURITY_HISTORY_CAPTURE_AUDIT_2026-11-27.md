# P4.44 — 281-security NEPSE history capture inventory and payload audit

Date: 2026-11-27

## Scope and source pin

Repository: `jaljala044/nepse-elite-ai-scanner-pro`  
Branch: `main`  
Reviewed Git tree commit: `889f28be685385e27b2fc5350d5a744a32880c80`

Capture directory:

`data/evidence/raw/nepse/security-history/2026-10-05_to_2026-11-26/symbols/`

## Inventory / manifest result

- Raw response files found in Git tree: **281**
- Unique symbol directories: **281**
- Total stored response bytes (Git tree sizes): **1,477,676**
- SHA256SUMS symbol-response entries: **281**
- Duplicate manifest symbol entries: **0**
- Tree files without manifest entries: **0**
- Manifest entries without tree files: **0**
- SHA256SUMS Git blob SHA: `40c2d4d6b482c0aacf0f6cb0baf8083e0b3d37`

This establishes exact file-inventory coverage and the presence of a per-file SHA-256 manifest. It is not a claim that all 281 payloads have been independently downloaded and re-hashed in this pass.

## Payload parse audit: three previously selected symbols

| Symbol | Current ID snapshot | Rows | Git blob SHA | Byte size | SHA-256 |
|---|---:|---:|---|---:|---|
| NESDO | 8041 | 29 | `d90113631f9e79b3980e57eeb2663e907e4eae1a` | 5,263 | `fb04ba036bb87e98c746073d38aacc9eb047e7aea14c22e25b968fef7cd05234` |
| ULBSL | 8063 | 29 | `1bad39084328c5b9646a59a658a923135229733f` | 5,251 | `076dd89b3d40c4622bb3119d491f3003a83f609b3e3b86f18cad64e59dc4da50` |
| YMHL | 9342 | 29 | `e186ad125b7c794b8517ebb768258ae57b517588` | 5,276 | `3ba51676e7c7ea047e32432ca3d933d5921de337f52c3dd568cdcf8661cb1a3b` |

All three parsed payloads cover business dates 2026-10-05 through 2026-11-26. Each has the same seven fields:

- `businessDate`
- `totalTrades`
- `totalTradedQuantity`
- `totalTradedValue`
- `highPrice`
- `lowPrice`
- `closePrice`

No Open field is present. The SHA-256 values above match the corresponding entries in the repository's SHA256SUMS manifest and the prior P4.44 three-symbol parity register.

## Interpretation and limitations

1. **281/281 inventory-to-manifest parity is verified.** All symbol response paths in the Git tree have exactly one corresponding SHA256SUMS entry.
2. **Only 3/281 payloads were parsed and field-audited in this pass.** The other 278 payloads remain to be schema-parsed and checked for valid date ordering, row counts, required fields, duplicate dates, and manifest digest.
3. The current security IDs are those associated with the selected captures/current snapshot. They do not prove that the same IDs applied across the historical OHLCV archive.
4. The 2026-10-05 to 2026-11-26 capture window does not adjudicate repeated pairs outside that window. The earlier parity audit found no repeated-pair endpoints within this window for these three symbols.
5. The endpoint does not provide Open, so it cannot establish full OHLCV parity.

## Disposition

**PARTIAL — inventory and manifest coverage verified for all 281 captures; payload parsing verified for 3 captures only.**

No raw response, OHLCV, floorsheet, lifecycle ledger, canonical row, date, or scanner input was changed. No row was shifted, deleted, deduplicated, corrected, promoted, or released from HOLD.


## Related work package #2 — current security-list response audit

The same pinned capture archive includes `security-list-response-01.bin`. It parses as a JSON array of **573 instruments** with five fields: `id`, `symbol`, `securityName`, `name`, and `activeStatus`.

- All 573 rows have all five fields populated.
- Duplicate IDs: 0.
- Duplicate symbols: 0.
- Status values: `A` = 546 rows; `S` = 27 rows.
- Git blob SHA: `0891e10b56de572816680c8065718ecd4420bd03`.
- SHA-256 from the archive's SHA256SUMS manifest: `5495d99a73aeb44e573936f59fc6a6d8dbf9ffc45c5a8ba62e672f0b0c6fa2f7`.

This is useful **current-snapshot instrument identity evidence**, not a complete all-instrument master satisfying the acceptance criteria. The response has no instrument-class field, no documented status-code semantics in the payload, and no effective dates or historical change log. It cannot establish past symbol/ID continuity or classify all instruments as equity/debt/fund/etc. without a separate authoritative classification source.

Work package #2 therefore advances from BLOCKED to **PARTIAL — 573-row current snapshot parsed and uniqueness-checked; instrument class and effective-dated history absent**. No historical identity inference or promotion is authorized.
