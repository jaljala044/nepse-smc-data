# Cross-repository duplicate-data audit

Audit date: 2026-11-28
Scope: default-branch recursive Git trees for the five NEPSE project repositories.
Method: compare Git blob SHA values across repositories. A shared blob SHA means byte-identical file content, regardless of filename or directory.

## Inventory

| Repository | Blob/file entries | Tree entries |
|---|---:|---:|
| `nepse-smc-data` | 1,014 | 36 |
| `nepse-history-starter` | 625 | 15 |
| `nepse-elite-ai-scanner-pro` | 1,913 | 645 |
| `nepse-automation` | 215 | 21 |
| `Nepse-master-data` | 1 | 0 |

All five recursive tree responses reported `truncated=false`.

## Exact byte-identical content found

There are **587 distinct blob SHA groups** whose content appears in more than one repository:

| Repository pair | Shared blob SHA groups |
|---|---:|
| `nepse-smc-data` ↔ `nepse-history-starter` | 564 |
| `nepse-smc-data` ↔ `nepse-elite-ai-scanner-pro` | 14 |
| `nepse-elite-ai-scanner-pro` ↔ `nepse-automation` | 9 |

The 564 shared groups between SMC and History Starter include the same `03_stock_charts_ohlcv/*.csv` paths and EOD audit JSON files stored under different directories. This confirms the two repositories are materially duplicating historical data. The count is distinct shared blob identities, not row count, dataset count, or a claim that all 564 are market-data files.

## Preliminary file-role inventory

| Repository | OHLCV/chart-like paths | Floorsheet/trade/broker-like paths | Validation/audit/reconciliation-like paths |
|---|---:|---:|---:|
| `nepse-smc-data` | 558 | 105 | 173 |
| `nepse-history-starter` | 527 | 52 | 19 |
| `nepse-elite-ai-scanner-pro` | 621 | 130 | 127 |
| `nepse-automation` | 0 | 207 | 4 |
| `Nepse-master-data` | 0 | 0 | 0 |

These are filename/path keyword counts, not semantic classification or unique data counts. The scanner repository also contains raw staging and third-party archives, so its path counts must not be interpreted as canonical records.

## Decisions

1. Do not delete or move duplicate files based on hashes alone.
2. Treat `nepse-smc-data` as the proposed canonical owner for normalized market datasets and shared validation contracts, subject to a content/lineage reconciliation before promotion.
3. Treat `nepse-history-starter` as an import/backfill utility and evidence source, not a second canonical OHLCV archive. Its existing files remain untouched until migration checks pass.
4. Keep raw source captures immutable and source-separated. Exact duplicates can reuse deterministic technical validation, but each source's authorization, capture lineage, coverage and cross-source reconciliation remain separate.
5. The main scanner should consume versioned approved datasets/manifests rather than maintaining a competing copy of the same canonical history.
6. `nepse-automation` should acquire and submit data, not own another canonical copy.
7. `Nepse-master-data` is currently only a 19-byte README in the inspected tree; do not assign it data ownership until a real schema and contents exist.

## Important validation policy

A SHA match is sufficient to reuse a prior *technical validation result* only when dataset kind, schema version and validator version also match. It is never sufficient to approve the source or promote data. Source authorization, source evidence, 3–5 year coverage, trading-calendar completeness and reconciliation against available authorized sources remain required. Preserve the user's authoritative 2025-07-28 values for BGWT, MEHL, RAWA, RHGCL and ULHC.

## Next work

- Run the new registry unit tests and the existing SMC test suite in CI.
- Integrate the registry into one OHLCV validator and one floorsheet validator.
- Publish one shared registry artifact or service; do not create five independent SQLite caches.
- Build a record-level reconciliation report for files that differ despite similar names/symbol coverage.
- Migrate consumers only after parity checks; retain rollback copies until acceptance.
