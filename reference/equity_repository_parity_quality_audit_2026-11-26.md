# Equity OHLCV Repository Parity and Full Structural Quality Audit — 2026-11-26

## Scope and method

Audited the 281 provisional common-equity OHLCV file pairs in:

- `jaljala044/nepse-smc-data`
- `jaljala044/nepse-history-starter`

Repository tree blob SHA comparison found 258 byte-identical file pairs and 23 pairs with different file blobs. Every one of the 258 identical pairs was fetched from the starter repository and checked row by row. Because each corresponding SMC file has the same Git blob SHA, the same row-level results apply to both copies. Both files for all 23 non-identical pairs were also fetched and compared row by row using numeric OHLCV values (so formatting differences such as 179.7 vs 179.70 are treated as equal).

Checks performed:
- duplicate date values
- OHLC invariant: High >= max(Open, Low, Close) and Low <= min(Open, High, Close)
- zero and negative volume
- missing/non-numeric OHLCV fields
- date format validity
- ascending date order
- adjacent rows with identical OHLCV values

This is a structural audit, not proof that each price/volume value matches an external provider, nor proof of expected-session completeness.

## Repository parity

| Metric | Result |
|---|---:|
| Provisional equity symbols | 281 |
| OHLCV files present in each repository | 281 |
| Byte-identical file pairs | 258 |
| Divergent file pairs | 23 |
| Missing files in either repository | 0 |

## Row-level structural results

| Metric | SMC repository | History starter repository |
|---|---:|---:|
| Rows checked | 246,129 | 233,457 |
| Duplicate dates | 0 | 0 |
| Invalid OHLC rows | 1,329 | 0 |
| Zero-volume rows | 0 | 0 |
| Negative-volume rows | 0 in the 258 identical pairs; not separately aggregated for all 23 divergent pairs | 0 in the 258 identical pairs; not separately aggregated for all 23 divergent pairs |
| Missing/non-numeric OHLCV rows | 0 in the 258 identical pairs; 0 reported in the divergent-pair audit | 0 |
| Invalid date rows | 0 in the 258 identical pairs | 0 in the 258 identical pairs |
| Out-of-order date steps | 0 in the 258 identical pairs | 0 in the 258 identical pairs |
| Adjacent repeated OHLCV rows | 71,806 | 78,868 |

The 258 byte-identical pairs account for 212,690 rows in each repository and contain:
- 0 duplicate dates
- 0 invalid OHLC rows
- 0 zero-volume rows
- 0 negative-volume rows
- 0 missing/non-numeric rows
- 0 invalid date rows
- 0 out-of-order date steps
- 71,801 adjacent repeated OHLCV rows across 252 symbols

The 23 divergent pairs account for 33,439 SMC rows and 20,767 starter rows:
- SMC: 1,329 invalid OHLC rows and 5 adjacent repeated OHLCV rows
- Starter: 0 invalid OHLC rows and 7,067 adjacent repeated OHLCV rows
- Both sides: 0 duplicate dates and 0 zero-volume rows

## Interpretation and cautions

1. **Structural validation passed for the 258 byte-identical pairs** under the checks listed above. Byte identity means both repositories share the same values; it does not establish external correctness.
2. **The 23 different-blob pairs are not 23 broad price conflicts.** Numeric comparison found 13,517 matching OHLCV rows out of 13,518 common dates. The 23 pairs contain 19,797 dates only in SMC and 7,090 dates only in starter. The extra starter dates are largely calendar-day carry-forward rows; the SMC files preserve longer historical date coverage. Treat the repositories as different coverage constructions, not as competing full-history price series.
3. Adjacent repeated OHLCV values are a suspicious pattern consistent with calendar-day forward-fill, especially given the known weekly closure regime changes. They are not automatically proven to be synthetic or invalid without date-level comparison against the exchange calendar and source evidence. Do not count these rows as independent executed trades without corroboration.
4. Some symbols have shorter histories because their archives begin later. Short row counts alone are not proof of missing data. Lifecycle/listing and suspension evidence remains necessary.
5. The ShareSansar-derived archive exactly corroborates 13 sampled OHLC invariant-flagged rows across 13 symbols. These are source-reported anomalies, not automatically SMC repository corruption. See [13-row source corroboration](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/shareSansar_source_corroboration_ohlc_flags_2026-11-26.csv).
6. The only numeric mismatch is RHGCL on 2026-11-19. The ShareSansar-derived row matches the starter values (Close 258.00, Volume 9,054) rather than SMC (Close 256.00, Volume 4,216). See [RHGCL reconciliation](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/RHGCL_2026-11-19_source_reconciliation_2026-11-26.md).
7. The OHLC invariant check does not test adjusted-vs-unadjusted basis, provider accuracy, trade-volume reconciliation, corporate-action treatment, or ticker identity.

## Deliverables

- [258-pair detailed structural audit CSV](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/equity_identical_pair_row_quality_audit_2026-11-26.csv)
- [23-pair numeric overlap and divergence audit CSV](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/equity_repository_divergence_audit_2026-11-26.csv)
- [RHGCL source-supported discrepancy evidence](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/RHGCL_2026-11-19_source_reconciliation_2026-11-26.csv)
- [281-equity observed-date coverage CSV](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/equity_observed_date_coverage_2026-11-26.csv)
- [Canonical session calendar](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/nepse_canonical_session_calendar_2025-2026.csv)

## Task 5 outcome

**Completed for row-level structural checks across all 281 provisional common-equity pairs.** All 258 identical pairs have now been audited, and both sides of all 23 divergent pairs have been audited.

**Not completed:** full lifecycle/session completeness validation and date-by-date adjudication of repeated OHLCV rows. Numeric overlap comparison is complete for all 23 non-identical pairs; one RHGCL row has a source-supported candidate resolution, while the other 22 pairs match numerically on every common date. No raw OHLCV file was changed.

## Recommended next phase

1. Resolve the single RHGCL 2026-11-19 row using the source-supported starter value in a derived view. Retain both raw files; the other 22 different-blob pairs match numerically on all common dates.
2. Investigate the 1,329 invalid SMC OHLC rows without overwriting raw source rows.
3. Classify adjacent repeated OHLCV rows against the two weekly trading-calendar regimes and derive a separate non-forward-filled view with provenance.
4. Validate symbol listing/suspension dates before publishing expected-session completeness scores.

## Source corroboration of OHLC invariant flags

A separate sample check compared the first flagged date for 13 symbols against the ShareSansar-derived daily archive `shawinCreates/Nepse-Market-Data`. All 13 sampled rows matched exactly for Open, High, Low, Close and Volume. This indicates that at least these invariant violations are already present in the source-reported ShareSansar values and were not introduced by the SMC repository. The sample is not exhaustive and does not certify all 1,329 flagged rows.

Do not auto-correct these values. Retain the raw source values and classify them as provider-reported OHLC invariant violations until a stronger row-level source resolves them. In particular, a zero Open must not be replaced with previous close or a guessed price.

Evidence: [13-row comparison CSV](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/shareSansar_source_corroboration_ohlc_flags_2026-11-26.csv) · [Evidence report](https://github.com/jaljala044/nepse-smc-data/blob/main/reference/shareSansar_source_corroboration_ohlc_flags_2026-11-26.md). The mirror's README documents that its daily-price files are scraped from ShareSansar: [source README](https://github.com/shawinCreates/Nepse-Market-Data/blob/main/README.md).
