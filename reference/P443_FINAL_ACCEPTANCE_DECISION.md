# P4.43 final acceptance decision

Audit scope: pinned base 56362fb4f65b91fdcca8f50b50e53ad80e703649. Audit investigation and initial disposition reporting completed; production acceptance is BLOCKED, not waived.

## Verified execution
- Run 125 (45895296361) completed successfully.
- Runs 143 (45896041494) and 145 (45896124933) passed the scanner quarantine and pinned cross-repository contract stages. Backend pin e5790632d293a477cc930a25649f39f8829cbf05.
- The 26 scanner test methods are fixture/contract tests, not independent historical trade validation or full strategy replay.
- Integer-volume and blocked fingerprint corrections committed at 4b14fd4515fd2c03f597e8649983b0d6ebb5496d; fractional-volume regression at f9df78f1f0bd8631d19d3c7f669873b2d05170fd. Latest execution not yet verified.

## Audit evidence
Six P443_*_RECONCILIATION.json reports preserve initial classifications. Use the latest successful strict audit and pair-level/holiday review artifacts for authoritative current counts; older aggregate reports are snapshots, not replacement data. Preserve raw records. No invented contract IDs, dates or prices.

## Outstanding acceptance gates
1. Confirm CI on final code revision.
2. Independent historical OHLCV/session and execution adjudication; no promotion of unresolved rows.
3. Complete source provenance, session completeness and cross-file/nested floorsheet ingestion protections.
4. Verify complete-period and point-in-time historical replay, including monthly consumers, SMC/ICT and authentic IDPAT V3 specification.
5. Keep production scoring/recommendations disabled until independently validated. PR #80 remains unmerged; do not treat audit completion as production approval.

Decision: audit review and tested contract foundation delivered; historical correction and production acceptance remain open. No raw modifications or production data promotion authorized.
