# P4.23.2 — Independent ShareSansar OHLCV cross-check

## Finding

The dated ShareSansar archive contains 320 daily symbol rows for 2025-07-28. All 86 P4.23.2 conflict symbols are present. The extracted 86-row snapshot matches the canonical SMC OHLCV snapshot exactly for Open, High, Low, Close and Volume (86/86 for each field). ShareSansar turnover also matches the per-symbol floorsheet turnover sum (86/86).

This independently corroborates the canonical daily OHLCV values. It does **not** mean the floorsheet itself has been fully reconstructed: the original floorsheet has no timestamps, so first/last trades cannot be established from transaction order. The floorsheet's extrema also disagree with the independent daily archive for some symbols.

## Source provenance

- Repository: `OmitNomis/ShareSansarScraper`
- Pinned commit: `524442d518d2f2705ade0680c9d2e3f90738e3d6`
- Path: `docs/Data/2025_07_28.csv`
- Git blob SHA-1: `28b5edf90ea5ebfe7e419c5162eedd0f30a9ce82`
- Repository README describes daily scraping of ShareSansar's share-price table into date-stamped CSVs. This is a secondary published archive, not a direct NEPSE exchange feed.
- The 86-row extracted snapshot records the pinned repository, commit, path and blob SHA on each row.

## Reconciliation

| Check | Exact matches |
|---|---:|
| ShareSansar Open vs canonical | 86/86 |
| ShareSansar High vs canonical | 86/86 |
| ShareSansar Low vs canonical | 86/86 |
| ShareSansar Close vs canonical | 86/86 |
| ShareSansar Volume vs canonical | 86/86 |
| ShareSansar Volume vs floorsheet quantity | 86/86 |
| ShareSansar Turnover vs floorsheet sum | 86/86 |
| ShareSansar High vs floorsheet-derived high | 85/86 |
| ShareSansar Low vs floorsheet-derived low | 53/86 |

The single high mismatch is ANLB. The 33 low mismatches are ADBL, CITY, CYCL, CZBIL, DLBS, DORDI, EBL, GBIME, HHL, JBLB, KBL, KDL, LSL, MBL, NABIL, NBL, NESDO, NICA, NIMB, NMB, PCBL, PRVU, PURE, SARBTM, SBI, SCB, SNLI, SRLI, TAMOR, TPC, ULBSL and UNLB.

These discrepancies are retained, not normalized away. Because all transaction quantities reconcile, the mismatching extrema need targeted investigation for rate-field anomalies, symbol mapping or source publication differences.

## Disposition

- Canonical daily OHLCV: independently corroborated by a second published daily archive for all 86 symbols.
- Floorsheet volume and turnover: reconciled against the independent archive.
- Floorsheet open/close: not reconstructable from transaction order because timestamps are blank; independently corroborated daily open/close values are available as reference values.
- Floorsheet high/low: unresolved for ANLB high and the 33 low mismatches above.
- No production OHLCV values, scanner scores or conflict labels are modified by this evidence-only update.

## Reproduction

```bash
python reference/p423_2025-07-28/compare_sharesansar.py \
  --snapshot reference/p423_2025-07-28/sharesansar_snapshot.csv \
  --results reference/p423_2025-07-28/results.csv \
  --out reference/p423_2025-07-28/sharesansar_comparison.json
```
