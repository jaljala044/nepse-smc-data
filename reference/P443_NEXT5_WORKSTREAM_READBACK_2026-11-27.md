# P4.43 next-five workstream read-back — session candidates and corporate actions (2026-11-27)

## Repository state

- Branch: `p443-global-integrity-audit`
- Branch / PR head at report creation: `f3478fc7ced2c52daac481502c3600d3014e42e9`
- PR #80 remains open, draft and unmerged.
- P4.44 issue #82 remains open.
- No canonical OHLCV values were changed.

## 1. Rechecked the 195-session recovery artifact

The previous session-recovery workflow [run 46002462651](https://github.com/jaljala044/nepse-smc-data/actions/runs/46002462651) completed successfully on commit `4021b46f0cd695149354fd73ef4a11379f961a04`. Its artifact ZIP SHA-256 was independently rechecked locally as:

`9cc96738fad27f6eb0c869aaf18259d0cc7f20d84a2e8ccc63040ec5d22d15ea`

The consolidated artifact contains 195 unique session dates:
- 148 secondary aggregate totals-match candidates;
- one March 1 date-shift candidate;
- five two-archive contract-parity candidates;
- 41 existing-baseline candidates.

The artifact still reports zero official approvals and zero promotions. All publication gates remain false.

## 2. Independent sample inspection of daily source CSVs

Eight representative daily files were fetched from the pinned ShareSansarScraper commit `524442d518d2f2705ade0680c9d2e3f90738e3d6` and independently parsed:

`2026-01-01, 2026-02-24, 2026-03-03, 2026-04-29, 2026-05-25, 2026-06-18, 2026-08-20, 2026-09-09`

All eight passed these sample checks:
- returned content length matched the inventory byte count (ASCII CSV);
- parsed per-security row count matched the market-summary traded-security count;
- no duplicate symbols;
- serial numbers were contiguous from 1;
- summed volume and turnover matched the market-summary values.

This is a purposive eight-file sample, not a full 148-file completeness conclusion. These are per-security daily EOD aggregate files, not underlying transaction-level floorsheets.

## 3. Added an independent full-scope source-structure audit

Added `tools/p443_audit_session_source_structure.py` and wired it into `.github/workflows/p443-session-count-recovery.yml`.

The new audit independently reopens all 149 inventory files from the pinned Git commit and checks:
- source byte count and recomputed Git blob SHA;
- CSV headers and row shape;
- symbol presence and uniqueness;
- contiguous `S.No` sequence;
- numeric volume, turnover and transaction fields;
- aggregate symbols/volume/turnover against the baseline;
- independently recomputed transaction sum against the recovery output;
- publication gate remains false.

Expected held-candidate profile is 148 structurally valid aggregate matches and one source-integrity-valid March 1 baseline conflict.

**Execution status: passed.** [Session recovery run 46003236951](https://github.com/jaljala044/nepse-smc-data/actions/runs/46003236951) completed successfully on code commit `f3478fc7ced2c52daac481502c3600d3014e42e9`. The independent audit read-back reports 149/149 files audited, zero errors, 148 `PASS_AGGREGATE_AND_STRUCTURE`, and one `SOURCE_INTEGRITY_OK_BASELINE_CONFLICT`. All 149 source blob hashes and byte counts matched; all 149 had unique symbols, contiguous serials, and independent totals equal to the recovery output. All publication flags remained false.

- Artifact ID: `15199675445`
- Artifact ZIP SHA-256: `fbba570a93e8b6f6d8992f907b83db7bf6b1aa0d6e34b55e99df8279f23e06ba`
- Independent audit CSV SHA-256: `7acb6ac711ed6a9138a7f8dcc0181ffd4e15a62ea79dfed39701f22cdd01c87c`
- Independent audit JSON SHA-256: `e3512194595f2fb2dc9ed99ff06dc8ee5293163d484e468c182ae5bc90265333`

The March 1 source file itself passed source-integrity and structure checks (13 unique symbols, serial sequence valid, 2,619 bytes, exact pinned blob SHA), but its aggregate totals conflict with the baseline. This confirms the archive partition is a valid pinned file but an incomplete session representation—not a corrupted download. The independent audit establishes per-security daily EOD file consistency, not independent exchange completeness or transaction-level correctness. The baseline still has no independent transaction-count benchmark for these 149 recovery dates.

## 4. Rechecked the corporate-action source recovery artifact

[P443 corporate-action recovery run 46003119493](https://github.com/jaljala044/nepse-smc-data/actions/runs/46003119493) completed successfully on checkout commit `52ec3f71ef71d3820f2f77d21fef8bf9b8126002`. Its artifact (ID `15198044455`) was downloaded and inspected.

- Artifact ZIP SHA-256: `766dd83c0c71256be1610ebd162339f254474f825f1b0e739a7f3b4ff0b34047`
- Candidate CSV SHA-256: `60711327d51c279d0543dcaeded432f2f5ff568c9e1ceaaafd404f4b67a4e825`
- Coverage CSV SHA-256: `b0c13d09fbadff36b79c51191ee4d4ce50aebf360266292682684dd8cb60400b`
- File audit CSV SHA-256: `bcdae8a831792bd873ea85e97cc763ddc1708f82f7f77f42fda538ebdb56ae0d`

Artifact read-back:
- 323 source files, 1,533 extracted candidate rows;
- 281 target equities, with 200 symbols having source candidates and 81 without candidates;
- 1,414 candidate rows associated with target equities;
- 1,294 rows classified `UNVERIFIED_SECONDARY`;
- 239 rows classified `SOURCE_FIELD_REVIEW`;
- zero exact duplicate rows;
- zero approved adjustments.

All 281 official-coverage values are `UNKNOWN`. The extracted artifact leaves every effective date and adjustment factor blank, and every row has `adjustment_allowed=false`. The source is the pinned third-party repository `SamirWagle/Nepse-All-Scraper`, not an exchange-approved corporate-action register. The 3-event canonical action register remains the only registered adjustment input; the bounded comparison does not prove that other events are absent.

## 5. Preserved the acceptance boundary

- March 1 remains a 13-symbol partial archive partition.
- The March 2 archive file remains only a secondary date-shift candidate; no relabeling is authorized.
- The 148 same-date aggregate matches do not prove floorsheet completeness or execution-level correctness.
- Corporate-action candidates remain secondary evidence only; no factor calculation, canonical adjustment, or promotion is authorized.
- P4.44 historical stable-ID and lifecycle evidence remains unresolved; issue #82 stays open.
- No full P4.43 global-integrity workflow was run on this report's branch head.

## Next acceptance gates

1. Run and inspect the full P4.43 global-integrity audit on the latest documentation head; the new 149-file session-source audit already passed on code commit `f3478fc7`.
2. Obtain an independent session-level source or official market-summary transaction-count benchmark.
3. Adjudicate March 1/2 date lineage from an authoritative exchange session record.
4. Obtain primary exchange/issuer corporate-action notices before deriving effective dates or adjustment factors.
5. Continue P4.44 stable-ID and lifecycle evidence acquisition; retain HOLD/UNKNOWN where provenance is incomplete.

**Status: workstreams advanced; P4.43 and P4.44 remain incomplete. No data promotion or canonical OHLCV modification occurred.**


## Follow-on refresh — current branch and audit trigger (2026-11-27)

A later repository refresh found that the branch had advanced beyond the head recorded above:
- Current branch / PR head before this follow-on: `e4fd90894541ec0830eb7f112799c66c38de88e3`.
- PR #80 remains open, draft and unmerged; P4.44 issue #82 remains open.
- The latest successful full P4.43 global-integrity run visible at that refresh was run 298 on `5b00a706c3e81513d41e71e67763f81554ba34dd`, not on the current head.
- The separate 149-file session-source audit passed on `f3478fc7ced2c52daac481502c3600d3014e42e9`; it does not substitute for the full global audit.

To close the documentation-trigger gap, the global-integrity workflow now watches this workstream read-back file under both `push` and `pull_request` path filters. The workflow-trigger change was committed as `9b28b4c9ff23260af97fbe8f06b9612b3fb8c156`. This report update should itself trigger the full workflow on the resulting branch head; the run must be inspected before claiming validation.

### Active next-five gates
1. Verify the full P4.43 global audit on the latest branch head and inspect every job/artifact.
2. Seek an independent official session-level transaction-count/completeness benchmark for the 149 recovery dates.
3. Resolve March 1/2 archive date lineage from primary exchange session evidence; do not relabel based on secondary candidates.
4. Obtain primary exchange/issuer corporate-action notices before deriving dates or factors.
5. Continue P4.44 effective-dated stable-ID and lifecycle evidence acquisition; preserve HOLD/UNKNOWN for unsupported symbols.

No canonical OHLCV data was changed, promoted, deduplicated, or date-shifted by this follow-on.


## Next-five continuation — corporate-action queue safeguards (2026-11-27)

Current branch head at this update: `f34a7783c4b32a206f611cb9786089a572fce46b`.

The corporate-action date recovery queue was read back from blob `ed6d1d73a4356d368f9182ae2629c391da869349`:
- 35 unique source rows: 30 `EXTERNAL_EVIDENCE_REQUIRED`, 5 `ZERO_RESIDUAL_CANDIDATE`.
- Two UNL rows have comma-formatted cash/total values; the normalized strings preserve the exact numeric values while retaining raw fields.
- All 35 queue rows remain `independent_verification=false` and `adjustment_allowed=false`; artifact `approved=0`.
- The five zero-residual cases pass exact Decimal arithmetic, but arithmetic does not independently establish the missing dividend component as zero. Missing book-closure dates remain unresolved.

Added `test_p443_corporate_action_date_recovery_queue.py` and integrated it into the full P4.43 workflow and both path filters. The test checks row provenance uniqueness, queue counts, exact residual arithmetic, UNL raw/normalized equivalence, and no-approval flags.

Full P4.43 audit run #303 (`46004414129`) was triggered on this exact branch head:
https://github.com/jaljala044/nepse-smc-data/actions/runs/46004414129

At the last check, pinned inventory verification passed and the read-only global scan was in progress. The newly added date-queue test has not yet executed. Older runs #299–#302 target earlier commits and do not replace #303.

No source CSVs or canonical OHLCV were changed. No corporate-action dates, dividend components, adjustment factors, or stable IDs were promoted. Remaining gates: complete the latest full audit; acquire an independent official session completeness benchmark; resolve March 1/2 date lineage from primary evidence; verify corporate actions against original notices; and continue P4.44 effective-dated identity/lifecycle evidence acquisition.


## Next-five continuation — current-head evidence and artifact boundary (2026-11-27)

Current branch / PR #80 head before this report refresh: `1d78beb64111c9eec93b3c7111e28cad0062c7d2` (446 commits; PR remains open, draft and unmerged). The head is three commits ahead of the last successful full P4.43 audit run #304, which tested `bb55b6ba88f79f4de7ead09ed0ff6751e327a213`. Run #304 completed successfully, including the new corporate-action date-recovery queue regression step. A commit-specific Actions lookup for the current head returned no PR-triggered workflow runs. The three intervening commits therefore remain outside that verified run; this report refresh is intended to trigger the configured push path for a current-head audit.

### New corporate-action corroboration records

- Added `reference/P443_CORPORATE_ACTION_EXTERNAL_CORROBORATION_BATCH01.json` (blob `f016da6aeb725550818a578f90739de000850dfe`) and batch 02 (blob `40e309aab50c6d1202458218c68e5e467db0f3f8`).
- CBBL: secondary disclosures reproduce a 2026-12-08 AGM book-closure date, 2026-12-21 AGM date, 11.9631% proposed bonus and 13.0369% proposed cash dividend. The record links to a NEPSE-hosted notice PDF, but the PDF endpoint was not independently retrievable in this review. Treat the reproduced notice as corroboration, not as an independently hashed primary-source capture.
- MKJC: secondary disclosures reproduce 2026-12-08 book closure and 2026-12-18 AGM. The separate 1:0.70 rights issue remains proposal-only; no subscription dates or adjustment-effective date are established.
- NICA: secondary records support the 2026-11-27 book-closure / 2026-11-26 last-eligible-trade date semantics, but the adjustment-effective date remains null and the record is not approved.
- CYCL has a date conflict; KMCDB has no recovered date. Both remain unresolved.
- Every record retains `adjustment_allowed=false`; no adjustment date or factor is promoted.

### Overlay retrieval preflight — blocked, not repaired by assumption

Added `reference/P443_OVERLAY_ARTIFACT_PREFLIGHT_2026-11-27.json` (blob `5a82fdcdda95377650a0af80b595f45049bbba64`). Artifact 15155667000 was downloaded and its archive SHA-256 verified (`20b74549f8e73aa3f94067ef834e6023b888dd0ec6df69ba174a3ecce7cbeb86`); all 25 members were inspected. None matched the expected overlay payload (30,352,499 bytes; SHA-256 `6d76c2a161dc3a65067806b5114a418be6aee0a90ebdc5519e2a718a531f7a2d`). Result: `BLOCKED_EXPECTED_OVERLAY_NOT_PRESENT`. The expected digest was not changed, partial files were not promoted, and approved replacements remain zero. Rebuild/export with the original overlay CSV is required before this queue can be adjudicated.

### Current disposition and next gates

1. Obtain a successful full P4.43 audit run on the current branch head after this report-triggered run appears; run #304 is successful but predates the three evidence commits and is not a current-head pass.
2. Recover the original complete overlay payload and verify exact expected bytes and SHA-256 before any overlay adjudication.
3. Independently retrieve and hash original NEPSE/issuer notices for CBBL, MKJC and NICA; preserve book-closure dates separately from ex-date / adjustment-effective date.
4. Resolve CYCL's conflicting date and KMCDB's missing date from primary records; otherwise retain HOLD/UNKNOWN.
5. Continue P4.44 stable-ID and lifecycle evidence acquisition for the 209-symbol / 23,377-pair matrix; no inference from current display names or ticker similarity.

No canonical OHLCV, raw source, or pinned baseline was modified. No date shift, corporate-action factor, adjustment, deduplication, or promotion was authorized. P4.43/P4.44 remain incomplete.


## Next-five continuation — full current-head P4.43 run 305 read-back (2026-11-27)

The branch head at the start of this validation was `e4c0364e58e4b0c9469751560292122304c2302e`. Full P4.43 workflow run #305 completed successfully on that exact SHA:

- Run: https://github.com/jaljala044/nepse-smc-data/actions/runs/46005266027
- Run ID: `46005266027`; conclusion: `success`; all 52 job steps completed with no failed steps.
- Global artifact ID `15200727323`; archive size 1,403,274 bytes; GitHub-reported ZIP SHA-256 `963ba29f4205b3621356ed399eb5fb3650e670e5b0b6c93fdbcbc4be157eebc7`.
- Strict-content artifact ID `15200372454`; archive size 58,287,637 bytes; GitHub-reported ZIP SHA-256 `f57d23ac588e7a47471480452ca7242cf84ea9e3b27fcd29426006b755a348c8`. Both archives were downloaded and their local SHA-256 values matched the GitHub artifact digests.

### Global audit artifact read-back

The global artifact reports 928 inventory files, 1,650,883 CSV rows / JSON documents parsed, 691 parsed CSV files, 93 parsed JSON documents, six non-JSON provider responses, 146 unsupported file/check combinations, zero parse errors, and 189,899 findings. Finding classes include 95,356 repeated tuples across rows, 94,543 consecutive identical OHLCV tuples, zero OHLCV duplicate symbol/date keys, zero exact OHLCV duplicate rows, zero duplicate floorsheet contract keys, zero exact repeated floorsheet rows, and zero duplicate dates within an individual calendar file. The report explicitly treats repeated tuples as review leads, not errors, and unsupported checks are not certified clean. This is a deterministic read-only scan of pinned base `56362fb4f65b91fdcca8f50b50e53ad80e703649`.

### Strict audit artifact read-back

- The strict summary independently records the 928-file pinned scope, 1,668,641 parsed records, 94,543 repeated adjacent tuple pairs, 1,331 invalid-OHLCV flags, and ten exact repeated JSON summary objects. Its record counter is a different parser/output measure from the global scan's CSV-row-plus-JSON-document counter; the two totals are not interchangeable.
- HF-only fourth batch: eight selected dates / 1,058 requests; 916 H/L/volume matches with open/close still unverified and 142 H/L/volume conflicts. The eight fetched partitions contained valid arithmetic rows, unique contract IDs within each partition, no duplicate contract IDs, and matched pinned LFS size/SHA metadata. Across the four batch outputs, all 74 HF-only partitions / 15,439 requests were selected and fetched. Batch 04 itself covers the final eight selected dates / 1,058 requests; the other three batches account for the remaining 66 dates / 14,381 requests. The per-batch status counters retain the overall discovery queue's pre-batch `HF_AVAILABLE_NOT_FETCHED` baseline and must not be summed as residual work after all four batches.
- 2024-08-01 rate diagnostic: all 72,500 rows remain strict amount-arithmetic failures; all stored rates are whole rupees; implied rates lie within 0.5 rupees; 72,496 round half-up to the stored rate; 9,045 are exact half-rupee ties and four do not follow half-up. This remains a hypothesis about source precision loss, not proof of execution rates. No reconstruction or promotion is authorized.
- Secondary inventory mapping covers 603 indexed dates: 74 secondary-only candidate dates (15,439 requests), 22 dates also present in the primary archive (5,235 requests), and 220 dates with no indexed source (48,099 requests). Coverage inventory is not content validation or proof of no trade.
- Observed opening/closing evidence covers 3,177 targets across 22 dates: 2,357 observed OHLCV matches, 790 ambiguous boundary ties, and 30 observed open/close conflicts. No candidate was promoted.
- P4.44 read-back in the same artifact remains valid: 23,377 rows / 209 symbols / 23,377 unique pair IDs; 21,082 current-snapshot-only identity rows, 2,295 unresolved identity rows, zero verified historical effective-dated IDs, and all unresolved evidence remains held.

Run #305 closes the current-head CI evidence gap for the audited code and documentation state. It does not close P4.43 acceptance: unsupported inventory checks, independent source provenance/session completeness, full date-lineage adjudication, overlay payload recovery, and unresolved evidence queues remain open. P4.44 remains incomplete. PR #80 stays open, draft and unmerged.

No canonical OHLCV or raw source values were changed, shifted, deduplicated, corrected, or promoted. No corporate-action factor, inferred rate, stable ID, or lifecycle date was approved.


## Next-five continuation — authenticated overlay retrieval and CI gate (2026-11-27)

### Drive retrieval helper review

Commit `64ee704bd5949076de6b959e3ac24bef6e6c8035` added `scanner_inputs/retrieve_drive_quarantine.py`. Review of its call chain confirms that it does not rely on file size alone: after streaming the bounded expected byte count to a temporary file, it calls `scanner_inputs.historical_quarantine.load_holds()` before creating the final output link. That parser validates the pinned manifest, exact expected byte count, SHA-256 `6d76c2a161dc3a65067806b5114a418be6aee0a90ebdc5519e2a718a531f7a2d`, schema, unique symbol/date keys, row counts, dispositions, and non-promotion flags. The output link is created only after this validation succeeds. No overlay payload was retrieved in this review.

### Actual private Drive gate result

Publication-gate run #8:
https://github.com/jaljala044/nepse-smc-data/actions/runs/46006958259

- The 53 existing publication, quarantine and scanner regression tests passed.
- Python compilation passed.
- The actual Drive retrieval step failed closed because the Actions secret `GDRIVE_SERVICE_ACCOUNT_JSON` was empty / unavailable to the run. The log explicitly reports: `Missing GDRIVE_SERVICE_ACCOUNT_JSON secret; fail closed`.
- This is an external credential/configuration blocker, not a failed overlay digest check. No Drive request was made, no payload was downloaded, and no overlay was promoted.

### Added regression coverage and CI path wiring

- Added `test_p443_drive_quarantine_retrieval.py` with mocked authenticated Drive responses. It checks that output creation follows quarantine validation, and that size or parser-validation failures leave no final output.
- Added the retrieval script and its regression test to both push and pull-request path filters in `.github/workflows/p443-global-integrity-audit.yml`, and added the test command to the workflow.
- Commits: test `ba4d37ea3879b69fee88e0eab45890192178bb4f`; path-filter wiring `16d93b2ceed33192d478b9e5fa42ff7a87872350`; test-step wiring `03e50222793b7d093ce5127d039097166f00b810`.
- Full P4.43 run #308 passed on `c6ed9804b39bb75a962550b7b9b4b0ca7a971b42` (all 52 steps, no failed steps), but predates the Drive-retrieval test changes.
- Run #309 is running on intermediate commit `16d93b2c...`; run #310 is running on current branch head `03e50222...`. Neither had completed at report time.

### Current acceptance boundary

The next full-current-head validation is run #310:
https://github.com/jaljala044/nepse-smc-data/actions/runs/46007082433

The Drive credential must be configured by an authorized repository administrator before the actual retrieval gate can pass. Do not add a credential to the repository, commit it, expose it in logs, or weaken the fail-closed check. After the secret is configured, rerun the publication gate and verify the downloaded file against the existing pinned SHA before any use.

No canonical OHLCV, raw source, or overlay payload was changed or promoted. P4.43 and P4.44 remain incomplete; PR #80 remains open, draft and unmerged; issue #82 remains open.



## Next-five continuation — current branch and Drive gate read-back (2026-11-27)

Branch / PR #80 head at this refresh: `9d95329d170a7327796ed35e976cea437000ef4a`. PR #80 remains open, draft and unmerged; P4.44 issue #82 remains open.

### Current-head publication gate

Publication-gate run #9:
https://github.com/jaljala044/nepse-smc-data/actions/runs/46007511539

- Run targets the exact current head `9d95329d170a7327796ed35e976cea437000ef4a`.
- All 60 regression tests passed, including seven Drive retrieval tests; Python compilation passed.
- The actual private Drive retrieval step failed closed because `GDRIVE_SERVICE_ACCOUNT_JSON` was empty/unavailable. The job log explicitly states: `Missing GDRIVE_SERVICE_ACCOUNT_JSON secret; fail closed`.
- No Drive request was made, no overlay payload was downloaded, and no digest verification or promotion occurred. This is a credential/configuration blocker, not a payload-integrity failure.

### Full global audit status

- Run #308 passed all 52 steps on `c6ed9804b39bb75a962550b7b9b4b0ca7a971b42`; it is an earlier successful validation, not current-head evidence.
- Run #313 is still in progress on `271c63022d9134e21a1e08718777cbc6f1263ffb`, which is also behind the current branch head.
- At read-back, the pinned inventory, read-only scan, strict regression tests, Drive retrieval regression tests, pinned-byte cross-check, P4.44 evidence checks, and opening/closing execution reconciliation had passed in #313. The second HF-only batch was active; the third/fourth batches, rate-precision diagnostic, secondary coverage, secondary contract checks and artifact preservation were pending.
- Run #313 has no final artifact read-back yet. It cannot validate current head `9d95329...`.

### Next acceptance gates

1. An authorized repository administrator must configure the private Drive service-account secret without exposing or committing credentials; then rerun publication gate #9 and verify the original overlay's pinned size and SHA-256.
2. Complete the full P4.43 workflow on the exact latest branch head and inspect its artifacts.
3. Continue independent official session completeness and March 1/2 date-lineage evidence acquisition.
4. Obtain original primary corporate-action notices and resolve conflicting dates; keep all unverified dates/factors held.
5. Continue P4.44 historical stable-ID/lifecycle evidence acquisition; no inferred IDs or dates.

No canonical OHLCV, raw source, or overlay payload was changed, shifted, deduplicated, corrected, or promoted. P4.43 and P4.44 remain incomplete.



## Next-five continuation — Run #313 completion and current-head Run #314 (2026-11-27)

### Run #313 completed successfully

Full P4.43 global-integrity workflow #313:
https://github.com/jaljala044/nepse-smc-data/actions/runs/46007287653

- Exact tested commit: `271c63022d9134e21a1e08718777cbc6f1263ffb` (behind the branch head at this refresh).
- Job conclusion: success; all 53 steps completed successfully.
- This includes the four HF-only bulk floorsheet batches, 2024-08-01 rate-precision diagnostic, secondary historical coverage mapping, secondary contract normalization/integrity regressions, strict outputs, and machine-readable outputs.
- Artifacts reported by GitHub:
  - `p443-strict-content-audit`, ID `15201004193`, 58,287,639 bytes, SHA-256 `47f081e960b9061b19d5023fbaca58490c9c28e2c83db897bee893eceea8f61d`.
  - `p443-global-integrity-audit`, ID `15200569698`, 1,403,274 bytes, SHA-256 `0bc9495e4e56e7d5dfd2ccee24ff69952238ab32aef4af883172feb22b762d15`.
- These are verified artifact metadata/digests from the Actions API; contents have not yet been independently downloaded and read back in this continuation.

### Current branch-head validation

- Branch and PR #80 head before this report update: `e5bdfd4a9cb0ec2b64480a3a84df9fd7a37c834a`.
- Full audit Run #314 is in progress on that exact commit:
  https://github.com/jaljala044/nepse-smc-data/actions/runs/46007835131
- At read-back, the first HF-only batch was active; later HF batches, rate diagnostic, secondary coverage, regression checks and output preservation were pending.
- Run #313 success does not validate the newer #314 head. No #314 success is claimed.

### Current acceptance boundary

- Publication gate #9 on commit `9d95329d170a7327796ed35e976cea437000ef4a` passed all 60 regression tests and Python compilation, but failed closed before Drive access because `GDRIVE_SERVICE_ACCOUNT_JSON` was unavailable. No overlay payload was retrieved.
- The private Drive secret must be configured by an authorized repository administrator; do not commit or expose credentials.
- P4.44 still has 26 residual symbols without verified historical effective-dated stable IDs; keep all unresolved identity/lifecycle rows HOLD/UNKNOWN.
- Independent official session completeness, March 1/2 date lineage, and primary corporate-action evidence remain unresolved.

No canonical OHLCV, raw source, or overlay payload was changed, shifted, deduplicated, corrected, or promoted. PR #80 remains open, draft and unmerged; issue #82 remains open.


## Next-30 continuation — Run #316 artifact read-back and lifecycle gate (2026-11-27)

### Repository and validation state

- Branch head immediately before this report append: `c0a10bb12c8f47b981f69c15e386d8d2b86362ec`.
- PR #80 remains open, draft and unmerged; P4.44 issue #82 remains open.
- Full P4.43 global audit Run #316 completed successfully with all 53 workflow steps:
  https://github.com/jaljala044/nepse-smc-data/actions/runs/46009773312
- Exact tested SHA: `4653263c575dee39243ccfb6e07d15b2d87ad0a3`. This is behind the branch head and is not current-head validation.

### Run #316 artifact byte read-back

Both artifacts were downloaded from Actions. Local SHA-256 matches the Actions API digest:

| Artifact | ID | Local SHA-256 | Result |
|---|---:|---|---|
| p443-strict-content-audit | 15204346019 | `77dc65bff7ac0099f89b3c63383faf10e0b54d74e08d9bd88fe7e40fcb6206d3` | MATCH |
| p443-global-integrity-audit | 15203766454 | `cb38c4e08bf0a36b0008a72f1e7b45e5c6e6b22cf998169361378020617c5f23` | MATCH |

Strict artifact read-back:
- P4.44 matrix: 23,377 rows, 209 symbols, 23,377 unique pair IDs, 2024-03-05 to 2026-11-20, zero audit issues.
- Identity scope: 21,082 current-snapshot-only, 2,295 unresolved; historical effective-dated stable IDs verified: zero.
- Current-side session evidence: 1,503 market-closed, 21,874 unknown.
- Previous-side session evidence: 979 market-closed, 22,398 unknown.
- Every matrix row remains `HOLD_UNKNOWN_NO_INFERENCE`; promotion false; canonical_data_modified=false.

Global artifact read-back:
- 928 pinned files; 784 parsed structured files; 138 inventory-only/unsupported; six non-JSON provider responses.
- Strict parser reports 1,668,641 parsed records, 94,543 repeated-adjacent tuple findings, 1,331 invalid-OHLCV flags, and ten exact repeated JSON summary objects.
- The separate global report's 1,650,883 is CSV rows plus JSON documents; it is not the same counting unit as strict JSON record elements.

### P4.44 canonical lifecycle gate

The 26-symbol P4.44 ledger is now loaded as symbol-wide wildcard holds by both canonical floorsheet publication and scanner staging. No effective-date boundaries are inferred because historical stable IDs and verified intervals remain absent.

Publication gate #13 passed the combined regression tests and Python compilation, but failed closed at the actual private Drive retrieval step because `GDRIVE_SERVICE_ACCOUNT_JSON` was unavailable. Publication gate #14 added destination- and parent-symlink regression tests; its combined regression step and Python compilation passed, while the overall workflow again failed only at the private Drive credential step:
https://github.com/jaljala044/nepse-smc-data/actions/runs/46010316571

The tests cover exclusive publication, identical rerun, refusal to overwrite differing bytes, destination/parent symlinks, evidence digest mismatch, duplicate contract IDs, and preservation of existing target bytes. Work package #23 is complete. Work packages #21 is implemented and #22 regression coverage passed; actual private Drive verification remains externally blocked.

### Remaining work and safeguards

- Original NEPSE PDF byte capture still fails in this environment; no raw SHA-256, byte count, or retrieval timestamp was fabricated.
- Lifecycle schema/provenance validation exists, but full interval-overlap and impossible-sequence auditing remains open.
- The 26 lifecycle rows remain `HOLD_UNKNOWN`; historical stable IDs remain 0/26.
- The 23,377 repeated-pair matrix remains held with zero promotions.
- Run #316 does not validate the current branch head. This report append is included in the global workflow's push path filter to trigger a new full audit on the resulting commit; that run must be inspected before claiming current-head validation.

No canonical OHLCV, floorsheet, calendar, lifecycle date, security ID, or scanner input data was changed, corrected, shifted, deduplicated, or promoted.


## Run #317 — exact-head full audit and independent artifact read-back (2026-11-27)

Full P4.43 global-integrity workflow Run #317 completed successfully, all 53 steps, on exact tested commit `ad4eca1c0892ec6c1e55e0a264fc87988dce86aa`:
https://github.com/jaljala044/nepse-smc-data/actions/runs/46010696573

Both artifacts were downloaded and local ZIP SHA-256 values independently matched the GitHub Actions artifact digests:

| Artifact | ID | GitHub/local SHA-256 | Result |
|---|---:|---|---|
| Global audit | 15203502332 | `eaea2fa735031755dc2c1fecda0a396987933bbdc597127f99a64cf2c2ebef71` | MATCH |
| Strict audit | 15202733267 | `1873b11145aaa55c18d0539bc108c35dd8942e21eeaa241460e136feaa0f2b61` | MATCH |

### Strict artifact read-back

- 928 pinned files; status totals: 784 parsed, 89 text-inspected, 36 code-syntax-checked, 11 workflow-syntax-checked, 2 manual document reviews and 6 non-JSON provider responses.
- Strict parser: 1,668,641 parsed records; 94,543 repeated-adjacent OHLCV tuple findings; 1,331 invalid-OHLCV flags; 10 exact repeated JSON records.
- Limitations: checks are within-file; unclassified records are parsed but not business-key validated; findings overlap; non-tabular checks are syntax/text extraction rather than semantic certification. No correction or canonical promotion.

### Global artifact read-back

- 928 files visited; 691 CSV files and 93 JSON documents; 146 unsupported file/check combinations; 6 non-JSON provider responses; zero parse errors; 189,899 findings.
- 95,356 repeated tuples across rows, including 94,543 consecutive identical tuples. No OHLCV duplicate symbol/date keys, exact duplicate OHLCV rows, floorsheet duplicate contract keys, exact repeated floorsheet rows, or within-file duplicate calendar dates were found by these checks.
- The global report's 1,650,883 count is CSV data rows plus JSON documents; it is not directly comparable to strict parsed-record count 1,668,641, which counts JSON record elements. Keep counting units explicitly distinct.

### P4.44 matrix artifact read-back

- 23,377 rows; 209 symbols; 23,377 unique pair IDs; date range 2024-03-05 to 2026-11-20; independent read-back auditor: valid=true, zero issues.
- Identity: 21,082 current-snapshot-only; 2,295 unresolved; historical effective-dated stable IDs verified: 0.
- Current-side session evidence: 1,503 market-closed, 21,874 unknown. Previous-side: 979 market-closed, 22,398 unknown.
- Every row remains `HOLD_UNKNOWN_NO_INFERENCE`; promotion_allowed=false; canonical_data_modified=false.

### Floorsheet and rate diagnostic boundaries

- Primary-indexed bulk recovery: 22 dates / 5,235 requests; 3,177 H/L/volume matches and 2,058 conflicts. Open/Close and archive completeness remain unverified.
- HF-only secondary inventory: 74 secondary-only dates / 15,439 requests; 48,099 requests without indexed source. The archive is third-party; byte hashes pin captured content to its source-tree metadata, not exchange origin or full-session completeness. No rows promoted.
- 2024-08-01: 72,500 amount-arithmetic failures have whole-rupee stored rates; implied rates are within half a rupee for all, but four exact half-rupee cases do not follow half-up. This remains a diagnostic hypothesis; no rate/amount reconstruction is authorized.

### Subsequent lifecycle sequence tests

After Run #317, the branch added `tools/p444_audit_lifecycle_sequences.py` and regression tests. Publication-gate Run #18 (ID 46031200729) on `7ff62a8eb922196f63f805335148fdc4fe311fda` passed the combined regression suite, including lifecycle-sequence tests, and Python compilation. It failed closed only at private Drive retrieval because `GDRIVE_SERVICE_ACCOUNT_JSON` was unavailable; no private overlay was retrieved or promoted:
https://github.com/jaljala044/nepse-smc-data/actions/runs/46031200729

The latest branch head at this report update is newer than Run #317 and Run #18. Therefore Run #317 is a successful exact-head audit for `ad4eca1...`, but **not** validation of the latest branch head. A fresh full P4.43 run is still required after the documentation/test commits. Work #9 is implemented with regression tests passed; the actual lifecycle ledger sequence scan has not yet been executed as a CI acceptance step.

PR #80 remains open/draft/unmerged; issue #82 remains open. No raw/canonical OHLCV, floorsheet, calendar, lifecycle date, security ID or scanner input row was changed, corrected, shifted, deduplicated or promoted.
