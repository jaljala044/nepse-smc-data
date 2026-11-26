# P4.43 final acceptance decision

Audit scope: pinned base 56362fb4f65b91fdcca8f50b50e53ad80e703649. Audit investigation and initial disposition reporting completed; production acceptance is BLOCKED, not waived.

## Verified execution
- Run 125 (45895296361) completed successfully.
- Runs 143 (45896041494) and 145 (45896124933) passed the scanner quarantine and pinned cross-repository contract stages. Backend pin e5790632d293a477cc930a25649f39f8829cbf05.
- Run 149 (45896232001) exposed a test-fixture typo in the expected Git blob SHA; the production quarantine fingerprint was correct. The fixture was corrected.
- **Run 151 (45896380619) passed all stages** on head `d0d12c5a87a436a86afb5d24e657a40c7c7f5f5b`.
- **Run 156 (45896661332) passed all stages** on head `281ce71756cd86f1609be7f817bce9999537d1c5`: inventory, standard scan, strict tests, scanner quarantine tests, pinned backend contract tests, strict pinned-byte audit, exception join, pair-calendar triage, disjoint queues, row-hold tests, authenticated holiday reconciliation, official security-history check of all 73 open-session pairs, and artifact preservation.
- The 73-pair check found no matching security/date EOD captures for either side of any pair. All remain unverified; missing capture is not proof of no trade.
- The 23 scanner quarantine test methods and cross-repository contract tests are fixture/contract tests, not independent historical trade validation or full strategy replay.
- `reference/P443_CANONICAL_EQUITY_EXCEPTION_PRIORITY.json` records verified per-symbol exception counts and a conservative hold policy; it is review policy only, not runtime enforcement.

## Audit evidence
- Run 156 (`open_pair_security_summary.json`) checked 73 pairs with both dates marked open in calendar evidence. All 73 returned `NO_SECURITY_DATE_EVIDENCE` for both dates. No price or row was promoted; absent EOD capture does not establish absence of execution.
- The two unmatched equity-register rows (KDBY 2026-04-29 and KEF 2026-04-28) are classified by the pinned official security master as investment-fund instruments (Kumari Dhanabriddhi Yojana and Kumari Equity Fund), not ordinary equity securities. They remain quarantined from the equity candle universe; this is an instrument-class disposition, not price validation.
Six P443_*_RECONCILIATION.json reports preserve initial classifications. Use the latest successful strict audit and pair-level/holiday review artifacts for authoritative current counts; older aggregate reports are snapshots, not replacement data. Preserve raw records. No invented contract IDs, dates or prices.

## Outstanding acceptance gates
1. Confirm CI on final code revision.
2. Independent historical OHLCV/session and execution adjudication; no promotion of unresolved rows.
3. Complete source provenance, session completeness and cross-file/nested floorsheet ingestion protections.
4. Verify complete-period and point-in-time historical replay, including monthly consumers, SMC/ICT and authentic IDPAT V3 specification.
5. Keep production scoring/recommendations disabled until independently validated. PR #80 remains unmerged; do not treat audit completion as production approval.

Decision: audit review and tested contract foundation delivered; historical correction and production acceptance remain open. No raw modifications or production data promotion authorized.
