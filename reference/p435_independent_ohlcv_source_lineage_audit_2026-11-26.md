# P4.35 — independent historical OHLCV source-lineage audit (2026-11-26)

## Disposition

**No candidate is currently qualified as an independent validation source for the 1,368 unresolved OHLCV flags.** Keep all 1,368 flags UNKNOWN. No external OHLCV or floorsheet data was imported, retained, compared row-by-row, repaired, promoted, or made scanner/training eligible.

SocrateAI's public NEPSE Open Data repository is a materially useful *unverified candidate*: it contains a 2025-07-28 floorsheet CSV and unadjusted stock OHLC CSV. Its upstream source, acquisition method, completeness guarantees, and authority to redistribute upstream data are not documented in the inspected repository. File existence is not evidence of independent lineage or correctness.

## Candidate inventory

| Candidate | Coverage/claim | Lineage finding | P4.35 disposition |
|---|---|---|---|
| Srijan Karki `srijankarki07/nepse-data` | Historical daily OHLC archive | README explicitly attributes historical backfill to ShareSansar | NOT_INDEPENDENT |
| Hugging Face `AnkitSanjyal/nepse-market-data` | `eod_price` described as NEPSE authoritative rolling 365 days; `eod_history_ext` described as ShareSansar historical; floorsheet/tick coverage begins 2026-08-19 | The older 1,368-key batch is outside the documented official rolling window and outside the stated floorsheet start | NOT_A_COVERAGE_MATCH |
| ShareHub | Historical price-history service | No authorised response, raw payload, retrieval metadata, or checksum obtained in this workflow | UNVERIFIED / NOT_ACQUIRED |
| SocrateAI `socrateai-official/nepse-open-data` | Daily floorsheet from 2024-01-01 through 2026-11-26 in current tree; stock OHLC files extend back to 2007 in the tree | Public repository does not identify upstream source or capture method; rights question remains unanswered | UNVERIFIED / DO_NOT_USE_FOR_VALIDATION |
| `binayabaral/nepal-market-data` | Daily historical prices | README explicitly attributes NEPSE data to ShareSansar and `Aabishkar2/nepse-data` | NOT_INDEPENDENT |

## SocrateAI candidate: immutable inspection record

Repository: https://github.com/socrateai-official/nepse-open-data  
Default branch: `main`  
Inspected tree commit: `70324524df83eaa7c2964441ad4026d6ab00cc7e`  
Tree SHA: `70324524df83eaa7c2964441ad4026d6ab00cc7e`  
Repository created: 2025-07-03  
Repository latest push observed: 2026-11-26

The README describes folders for floorsheets, adjusted/unadjusted OHLC and index data, but does not state the upstream data provider, API, collection code, timestamp policy, or completeness method. The inspected repository tree contains no source-code or workflow directories; `meta/` contains only `.gitkeep`, not the README-promised symbol/sector CSVs.

Relevant files at the pinned tree:

| File | Git blob SHA | Bytes |
|---|---|---:|
| `floorsheet/floorsheet_2025-07-28.csv` | `9c5533626b354d5fefca06d6762d51e0b9beaac6` | 10,026,040 |
| `ohlc_unadjusted_stock/unadj_2025-07-28.csv` | `c6642c2d179b34800b5758ad4225b0861dbf5313` | 14,164 |
| `ohlc_adjusted_stock/adj_2025-07-28.csv` | `c6642c2d179b34800b5758ad4225b0861dbf5313` | 14,164 |

**Anomaly:** the adjusted and unadjusted OHLC files for 2025-07-28 have the exact same Git blob SHA, so their bytes are identical. This does not establish that either file is correctly adjusted or unadjusted; it is a data-basis question that requires source-owner explanation and corporate-action-aware checks.

The floorsheet file and OHLC file are present for the exact 2025-07-28 conflict date, but the floorsheet is ~10 MB and the current inspection did not retrieve its bytes. No row counts, trade-ID uniqueness, completeness, pagination totals, arithmetic, or OHLC aggregation are claimed.

The 2025-07-28 bulk update commit is `7648ec7ce9988e032975d6cf8bcc876ba7da7ae5`, authored by `Surazz2022`, unsigned, with message stating it updated a “cleaned NEPSE dataset” for floorsheet and adjusted/unadjusted OHLC from 2007-01-02 to 2025-07-28. The message does not identify the upstream source or how the data was obtained.

The repository's MIT license text says it applies to “this dataset and associated documentation files”, but that text alone does not demonstrate that the repository owner has authority to relicense underlying exchange/provider data. Public issue #2 asks the maintainer to clarify upstream source, licensing scope, rights, and provenance; the issue had no maintainer response/comments at inspection time.

References:
- Repository: https://github.com/socrateai-official/nepse-open-data
- README: https://github.com/socrateai-official/nepse-open-data/blob/main/README.md
- Pinned 2025-07-28 data commit: https://github.com/socrateai-official/nepse-open-data/commit/7648ec7ce9988e032975d6cf8bcc876ba7da7ae5
- Unanswered provenance/rights issue: https://github.com/socrateai-official/nepse-open-data/issues/2
- License: https://github.com/socrateai-official/nepse-open-data/blob/main/LICENSE

## Independent-lineage and coverage conclusion

The SocrateAI dataset may be an additional archive, but a separate Git repository or a separate uploader is not proof of a separate upstream capture path. Until its maintainer identifies the upstream provider and capture method, demonstrates rights to redistribute the data, and supplies reproducible coverage/completeness metadata, it cannot be counted as an independent vote against ShareSansar-derived values.

No inspection of the 1,368 exact keys was performed against SocrateAI files because doing so would risk presenting an unverified and potentially same-source dataset as independent evidence. The 1,283 ShareSansar-mirror matches remain non-independent; the 85 missing keys remain unavailable from that lineage.

## Minimum acquisition needed to unblock P4.35

1. Written maintainer response identifying the source endpoint/provider for each of floorsheet, unadjusted OHLC, and adjusted OHLC; explain whether any data was copied from ShareSansar, Aabishkar2, YONEPSE, or another archive.
2. Evidence of permission/rights to redistribute upstream market data under the repository's stated license, or an authorised private-use data licence for this project.
3. Immutable source revision plus exact 1,368-key file inventory, raw/adjusted basis, field semantics, source dates, and capture/revision timestamps.
4. For any floorsheet used as evidence: complete date-specific pages/pagination totals, unique contract identifiers, valid symbol/date, positive quantity/rate, amount arithmetic, and reconciliation to independent EOD totals.
5. For any OHLC used as evidence: point-in-time raw/unadjusted basis, corporate-action handling, source lineage, and exact key coverage.

If these inputs are not available, use a permitted primary NEPSE historical EOD payload, authorised provider response, or complete date-matched floorsheets instead.

## Safeguards retained

- All 1,368 OHLCV invariant flags remain UNKNOWN.
- No OHLCV files or candidate third-party data were imported into this repository.
- No canonical rows, corporate-action adjustments, lifecycle dates, scoring, training eligibility, or BUY eligibility changed.
- No source was silently treated as independent based on a distinct repository or file hash.
