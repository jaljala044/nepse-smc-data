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
