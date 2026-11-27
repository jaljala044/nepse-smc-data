# P4.43 master-session candidate consolidation — artifact read-back (2026-11-27)

## Execution provenance

- Branch: `p443-global-integrity-audit`
- Commit: `4021b46f0cd695149354fd73ef4a11379f961a04`
- Workflow: [P443 session count recovery, run 3](https://github.com/jaljala044/nepse-smc-data/actions/runs/46002462651)
- Run conclusion: `success`
- Pinned ShareSansarScraper commit: `524442d518d2f2705ade0680c9d2e3f90738e3d6`
- Artifact ID: `15198727482`
- Artifact ZIP SHA-256: `9cc96738fad27f6eb0c869aaf18259d0cc7f20d84a2e8ccc63040ec5d22d15ea`
- Read-back master CSV SHA-256: `87243ae8371e85a8306922e10f4123ef055941ce7ea3e33bf590e03eb94b7d88`
- Read-back master summary SHA-256: `ef2083541ea038b63a7d46deb0e14b55a1aeb8b7eefa47eb257c00fa5a7abd73`

The run log confirms both recovery and consolidation commands completed, and the artifact was downloaded, unzipped, and independently read back.

## Consolidated candidate coverage

The artifact contains 195 unique session dates, 2026-01-01 through 2026-11-20:

| Candidate classification | Sessions |
|---|---:|
| Existing baseline candidate | 41 |
| Archive contract-parity candidate | 5 |
| Secondary archive aggregate totals-match candidate | 148 |
| Secondary date-shift candidate | 1 |
| **Total** | **195** |

The artifact summary reports `officially_approved=0` and `promoted=0`. All 195 rows have `official_review=PENDING` and `publication_allowed=false`.

## March 1 date-shift finding

The 2026-03-01 master row is classified as `SECONDARY_DATE_SHIFT_CANDIDATE`, not as an ordinary same-date match. Its totals are sourced from the pinned archive's 2026-03-02 file:

- Source date: `2026-03-02`
- Source Git blob: `53bc1975d9c4e3f20989b85791a815b6eb806b04`
- Candidate totals: 341 securities, 13,193,462 shares, NPR 5,648,319,041.36 turnover, 55,206 transactions.

This is a date-lineage candidate only. It does not establish that the 2026-03-02 file should be relabelled as 2026-03-01, nor does it authenticate the correct exchange session key. It remains pending official review and non-publishable. The original 2026-03-01 archive partition remains a 13-symbol partial/conflicting partition; its source data was not edited.

## Read-back checks and limitations

- Master CSV: 195 rows and 195 unique dates.
- Date range: 2026-01-01 to 2026-11-20.
- Classification counts reconcile exactly to the 195-row summary.
- All publication gates remain false; no promotion occurred.
- The five archive-parity candidates are based on the recorded two-archive contract-parity comparison and are not official approval.
- The 148 secondary totals matches establish aggregate agreement against the pinned market-summary baseline, not row-level floorsheet completeness or independent execution correctness.
- The 41 existing baseline candidates reuse counts already present in the baseline and are not new independent source recovery.
- The master CSV leaves `source_blob` empty for 46 rows (41 existing-baseline and five archive-parity routes); the artifact does not provide a per-row archive blob SHA for those routes.
- This narrow workflow does not run the full P4.43 global-integrity audit, does not complete P4.44 historical identity evidence, and does not validate canonical OHLCV changes.

## Disposition

Keep all 195 rows as review candidates only. Do not publish, promote, shift dates, infer missing source rows, or modify canonical OHLCV. Next work is independent row-level/source-completeness validation for the 148 same-date aggregate matches, primary verification of the five archive-parity sessions, and official date-key adjudication of the March 1/2 candidate.
