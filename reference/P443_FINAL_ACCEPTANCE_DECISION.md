# P4.43 final acceptance decision

Audit scope: pinned base 56362fb4f65b91fdcca8f50b50e53ad80e703649. Audit investigation and initial disposition reporting completed; production acceptance is BLOCKED, not waived.

## Verified execution
- Run 125 (45895296361) completed successfully.
- Runs 143 (45896041494) and 145 (45896124933) passed the scanner quarantine and pinned cross-repository contract stages. Backend pin e5790632d293a477cc930a25649f39f8829cbf05.
- Run 149 (45896232001) exposed a test-fixture typo in the expected Git blob SHA; the production quarantine fingerprint was correct. The fixture was corrected.
- **Run 151 (45896380619) passed all stages** on head `d0d12c5a87a436a86afb5d24e657a40c7c7f5f5b`.
- **Run 156 (45896661332) passed all stages** on head `281ce71756cd86f1609be7f817bce9999537d1c5`: inventory, standard scan, strict tests, scanner quarantine tests, pinned backend contract tests, strict pinned-byte audit, exception join, pair-calendar triage, disjoint queues, row-hold tests, authenticated holiday reconciliation, official security-history check of all 73 open-session pairs, and artifact preservation.
- **Run 166 (45897149333) passed all stages** on head `2a840c24b1dbb7bffe9586441d87b91be2610a7d`, including the new equity-first review regression tests and export. The 58,972 unresolved pairs were partitioned using the pinned current instrument crosscheck: 44,283 current-equity-first-pass, 6,351 current mutual-fund, and 8,265 unclassified within the insufficient-session group; among 73 both-open pairs, 5 current-equity, 5 mutual-fund, and 63 unclassified. This is prioritization only, not point-in-time identity or execution verification.
- Run 182 (45897847093) failed at the new unresolved-pair test import; no evidence check ran. The sibling-module imports were corrected for both package and direct-script execution.
- **Run 190 (45898089926) passed all stages** on head `bee8e164e8e9866baddbde557890b90fb953e7b0`, including both new regression suites, all-58,972-pair official EOD comparison, unique security-date recovery queue export, and artifact preservation.
- The 73-pair check found no matching security/date EOD captures for either side of any pair. All remain unverified; missing capture is not proof of no trade.
- The 23 scanner quarantine test methods and cross-repository contract tests are fixture/contract tests, not independent historical trade validation or full strategy replay.
- `reference/P443_CANONICAL_EQUITY_EXCEPTION_PRIORITY.json` records verified per-symbol exception counts and a conservative hold policy; it is review policy only, not runtime enforcement.

## Audit evidence
- Run 156 (`open_pair_security_summary.json`) checked 73 pairs with both dates marked open in calendar evidence. All 73 returned `NO_SECURITY_DATE_EVIDENCE` for both dates. No price or row was promoted; absent EOD capture does not establish absence of execution.
- Run 166's `equity_first_repeat_summary.json` confirms the above current-instrument partition; all 58,972 rows remain `promotion_allowed=false`. The 5 equity-priority open-session pairs are BNL, BNT, ENL and UNL; the remaining open pairs are either current mutual funds or unclassified. No historical instrument identity is inferred from current status.
- Run 190 (`unresolved_pair_security_summary.json`) checked all 58,972 evidence-review pairs. 58,535 had no official security/date capture for either date; 437 had a previous-date HLCV plus positive-execution match but no current-date capture. Zero pairs had both dates matched, and zero mismatches/conflicts were found. All remain unverified; a previous-date match is not full OHLCV validation.
- Run 190's equity recovery queue contains 68,783 unique security/date requests across 253 current-equity-first-pass symbols from 44,288 pairs (10 P1 open-pair dates; 68,773 P2 session/execution dates). It is an acquisition queue only; no evidence was fetched or data corrected.
- The two unmatched equity-register rows (KDBY 2026-04-29 and KEF 2026-04-28) are classified by the pinned official security master as investment-fund instruments (Kumari Dhanabriddhi Yojana and Kumari Equity Fund), not ordinary equity securities. They remain quarantined from the equity candle universe; this is an instrument-class disposition, not price validation.
Six P443_*_RECONCILIATION.json reports preserve initial classifications. Use the latest successful strict audit and pair-level/holiday review artifacts for authoritative current counts; older aggregate reports are snapshots, not replacement data. Preserve raw records. No invented contract IDs, dates or prices.

## Outstanding acceptance gates
1. Confirm CI on final code revision.
2. Independent historical OHLCV/session and execution adjudication; no promotion of unresolved rows.
3. Complete source provenance, session completeness and cross-file/nested floorsheet ingestion protections.
4. Verify complete-period and point-in-time historical replay, including monthly consumers, SMC/ICT and authentic IDPAT V3 specification.
5. Keep production scoring/recommendations disabled until independently validated. PR #80 remains unmerged; do not treat audit completion as production approval.

Decision: audit review and tested contract foundation delivered; historical correction and production acceptance remain open. No raw modifications or production data promotion authorized.
