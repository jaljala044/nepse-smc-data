# P4.44 initial NEPSE per-security history parity — three uncovered-repeat equity symbols

Date: 2026-11-27

## Result

Parsed the existing NEPSE raw per-security history response files for the three symbols that the P4.43 uncovered-repeat triage matches to the current equity crosswalk:

| Symbol | Current security ID | Source rows | Adjacent repeated pairs (all dates) | Official history rows | Overlap with source | Exact H/L/C/volume matches | Conflicts |
|---|---:|---:|---:|---:|---:|---:|---:|
| NESDO | 8041 | 934 | 320 | 29 | 25 | 25 | 0 |
| ULBSL | 8063 | 932 | 318 | 29 | 25 | 25 | 0 |
| YMHL | 9342 | 97 | 2 | 29 | 25 | 25 | 0 |
| **Total** | | **1,963** | **640** | **87** | **75** | **75** | **0** |

The 25 overlapping official business dates per symbol run from 2026-10-05 through 2026-11-20. All 75 overlap rows exactly match the pinned OHLCV source's High, Low, Close and Volume fields after numeric normalization.

## Important limits

- The captured NEPSE per-security response has High, Low, Close, quantity, turnover and trade count, but no Open. This is not full OHLCV parity.
- The NEPSE response contains four later rows per symbol (2026-11-23, 24, 25, 26), after the pinned OHLCV files' last date of 2026-11-20. Those 12 rows have no same-date source row to compare.
- There are no adjacent repeated-tuple pairs for any of these three symbols inside the official capture window. Therefore this pass adjudicates **zero** of their 640 repeated pairs and zero of the 23,377 global uncovered pairs.
- The current security IDs do not prove that the same IDs applied throughout the historical source files.
- A positive trade count is strong per-security activity evidence for those official dates; it does not prove the adjacent repeated tuples on other dates are valid or misdated.

## Pinned source provenance

The source OHLCV rows were read from commit `56362fb4f65b91fdcca8f50b50e53ad80e703649`. The official raw response files and SHA-256 values are recorded in the companion CSV/JSON. The scanner repository's SHA256SUMS manifest blob is `40c2d4d6b482c0aacf0f6cb0c0baf8083e0b3d37`.

## Disposition

Partial official H/L/C/volume parity confirmed for 75 date rows. Full OHLCV/date-lineage adjudication remains unresolved. No raw or canonical OHLCV changes, date shifts, deletions, deduplication or promotions.
