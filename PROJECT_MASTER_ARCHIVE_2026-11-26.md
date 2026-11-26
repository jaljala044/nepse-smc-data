# NEPSE AI — Project Master Archive
Snapshot date: 2026-11-26 (UTC date). Status: evidence index and handover, not a canonical-data release.

## Source of truth and policy
- Project scope requested: 281 active equity symbols and 47 mutual funds, **pending an unambiguous dated official roster**. The 525 historical OHLCV files are an inventory, not the active universe.
- Preserve raw source observations, date, URL, retrieval method, hash, parser revision and conflicting observations. Never silently overwrite one provider with another.
- Keep any unverified security/date, OHLC contradiction, corporate-action basis or exchange session quarantined. **No training, scanner signals or canonical data promotion** until explicit integrity gates pass.
- Prior user-finalized OHLCV data and later chart corrections have conflicting documentation (see below); treat this as a provenance/decision conflict, not an automatic data-edit instruction.

## Verified accessible locations

### GitHub repositories
| Repository | Role | Link | Status |
|---|---|---|---|
| nepse-smc-data | OHLCV and reference validation | https://github.com/jaljala044/nepse-smc-data | Active; main + two review PRs |
| nepse-history-starter | Alternate historical observations | https://github.com/jaljala044/nepse-history-starter | Active; source should remain immutable |
| nepse-elite-ai-scanner-pro | Scanner, P1 acquisition workflow | https://github.com/jaljala044/nepse-elite-ai-scanner-pro | P1 PR #12 open |
| nepse-automation | Automation assets | https://github.com/jaljala044/nepse-automation | Accessible; content not reviewed in this checkpoint |
| Nepse-master-data | Planned security master | https://github.com/jaljala044/Nepse-master-data | Accessible; reported effectively empty/README only |

### Review and audit links
- Primary reference-data gate: https://github.com/jaljala044/nepse-smc-data/issues/4 (open).
- Stable-ID, symbol, mutual-fund and historical-holiday evidence: https://github.com/jaljala044/nepse-smc-data/pull/5 (open, **not mergeable** at checkpoint). Branch `feat/nepse-reference-data-gate`; its own run reported 19 passing tests. Reference report: `reference/NEPSE_REFERENCE_CAPTURE_STATUS_2026-11-26.md` on that branch.
- Seven-row Decimal regression guard and cross-repo inventory: https://github.com/jaljala044/nepse-smc-data/pull/6 (open **draft**, mergeable). Branch `test/user-finalized-ohlcv-regression-2026-11-26`; reported 17 passing tests: https://github.com/jaljala044/nepse-smc-data/actions/runs/45761564074
- Official NEPSE capture reliability and retained authentication/retention blockers: https://github.com/jaljala044/nepse-elite-ai-scanner-pro/pull/12 (open); evidence workflow https://github.com/jaljala044/nepse-elite-ai-scanner-pro/actions/runs/45674237231

### Google Drive
- User-provided archive folder: https://drive.google.com/drive/folders/1BXt-GxUjqUMyLG4CxSvYi0jQCzjdaMPJ
- NEPSE Daily Master spreadsheet: https://docs.google.com/spreadsheets/d/10D73eraX6ZUSsXGBhJuGZk5tEeekK5Wc0KYqFAakp-U/edit?usp=drivesdk
- Data archive: https://drive.google.com/drive/folders/1VWNpZCQ-slTf6fhw-cP1mhWQHUQDgqsM
- Daily Master folder: https://drive.google.com/drive/folders/1kLsbNkuF12IrFL1S82wi7WjBTC9Ug6zE
- Older floorsheets: https://drive.google.com/drive/folders/1EmLNZ9FB67AbdWvChJtJk3vjmsJm_87h
- Additional floorsheets: https://drive.google.com/drive/folders/1_-qz5s40vPRXrNRHOaJuVeRgg6abGZlq
- User archive folder includes six multipart NEPSE DATA ZIPs, each approximately 583–617 MB. Only filenames, sizes and links were confirmed here; ZIP contents were **not extracted or validated**.

## Data evidence inventory
| Asset / milestone | Evidence | Current disposition |
|---|---|---|
| Historical OHLCV | 525 `*_OHLCV.csv` files in each of the SMC and Starter repositories; 500 same Git blobs and 25 differing blobs as of the PR #6 audit | File inventory confirmed from saved audit; row-level 25-file comparison incomplete |
| Seven stock/date input records | PR #6 regression guard | Protected as project inputs, not independently verified NEPSE primary values |
| Current equities | Official rendered https://nepalstock.com.np/company | One pass 281 rows/278 unique; later pass says 281 unique but only 20 row payloads exposed; unresolved |
| Mutual funds | 47 active symbols reported; 46 corresponding OHLCV filenames, NICEF missing | Current snapshot only; complete dated official lifecycle IDs missing |
| Official instrument master | No verified stable `securityId` for all securities, historical lifecycle/effective-date rename source | Blocked |
| Historical holidays | 408 raw entries covering eleven fully captured years 2014–19, 2021–25; 2020/2012/2013 partial; 2011 missing | Holiday-list evidence, NOT proof of verified closed sessions |
| 2026 closures | Separate primary NEPSE API snapshot with 41 records | Closure-only; zero evidenced open sessions |
| Primary historical OHLCV | Scanner PR #12: 2026-11-19 API/HRL/RHGCL partial OHLCV; old 2025-07-28 security histories empty; date board HTTP 401 | Primary completeness gate failed; not resolved |
| Cross-source exceptions | 1,331 invalid-OHLC row exceptions + 8 cross-source conflict keys in prior ledger | Quarantined |
| Separate RHGCL 2026-11-19 | SMC vs Starter close and volume differ, per Issue #4 | Quarantined, do not choose either without new provenance |
| Scanner / point-in-time / deployment | Modules and designs exist; no end-to-end production safety proven | Not enabled for investment decisions |

## Evidence conflict requiring an explicit decision
Issue #4 records **later chart-derived** BGWT (2025-07-28) OHLC `940,992,933.40,957.17`, HRL (2026-11-19) low `480`, and calls these seven input records reconciled. PR #6, however, records the **earlier user-finalized** BGWT `824.56,870.18,818.77,839.62` and HRL low `483.90`, and tests those values. It also documents a NEPSE primary low observation of `480` for HRL. Both narratives are present in the project record and must remain visible.

Resolution protocol: keep both raw observations and basis labels, identify the *latest explicit user-approved row set with a dated artifact*, compare against raw ShareHub workbook and any official primary capture, then amend regression expectations **only after** the decision is recorded. Do not interpret a passing test as official price validation. Do not silently rewrite project inputs.

## Next five bounded tasks (in order)
1. Resolve the **internal BGWT/HRL approved-value mismatch** between Issue #4 and PR #6 with artifact-level source linkage; preserve both versions.
2. Make PR #5 mergeable: inspect current conflicts/changed files, rebase or cherry-pick safely, rerun 19 reference tests; do not merge before gate review.
3. Acquire a complete official dated instrument snapshot including stable security IDs, statuses, instrument classes and lifecycle intervals; reconcile all 525 filenames; keep residuals classified *unresolved*, not 'unknown', until proven.
4. Finish the missing exchange holiday table pages and obtain positive evidence for **open trading sessions**; explicitly separate holiday announcements from confirmed closures.
5. Run validation over the historical universe and calculate dated 90–120 day, 1-year and 2–3 year coverage only once the instrument/calendar gates permit reliable denominators.

## Evidence rules and limitations
- This index reconciles previously saved GitHub issue/PR reports with direct repository and Drive metadata readback on 2026-11-26. It does not assert unseen ZIP contents or full historical NEPSE primary verification.
- Open PR #5 is marked `mergeable=false`; open PR #6 is a draft. Treat branch changes as **not yet merged**.
- No canonical data promotion, production signal activation, or live provider deployment is authorized by this archive.

## P1 follow-up — 2026-11-26
Direct readback of both repositories confirmed corrected BGWT and HRL values. The saved seven-stock ShareHub audit and Issue #4 comments 7183852195/7183897894 establish the controlling project inputs. PR #6 test expectations corrected in commit abec5ac029f6f5a630b1dcfd28fda0fc7dbc0440; direct comparison against main: 7/7 matches. No market data changed. Fresh CI and branch integration still require verification. The original conflict section above is retained as historical context, superseded by this decision. Next: PR #5 mergeability repair.

## P2–P6 checkpoint — 2026-11-26
- P2: PR #5 merged successfully, commit 1cdb9e3d924104a4e8c5f5e843d585bb70ee51d2. Fresh CI run 45779354004 succeeded. P1 corrected regression commit CI run 45778976984 succeeded; PR #6 integration remains separate.
- P3: recovered official 2026-11-25 security-list parsed response from companion scanner repo. 573 unique IDs and symbols; 546 active, 27 suspended; 488/525 exact filename matches, 37 unresolved; 85 captured symbols lack exact OHLCV filename. NICEF ID 9357. Snapshot at reference/nepse_security_id_snapshot_2026-11-25.csv. No instrument classes or historical effective dates inferred.
- P4: recovered authenticated holiday API archive audit, 2015–2026: 499 rows, 498 distinct dates, one duplicate date 2020-04-13, HTTP 200 for all years. Index at reference/nepse_holiday_api_coverage_2015-2026.csv. No inferred open sessions or canonical closure promotion; pre-2015 coverage and annual completeness remain unresolved.
- RHGCL 2026-11-19: companion scanner official capture-report.json confirms ID 8108, H 259.5, L 252.1, C 258, volume 9054, 47 trades, turnover 2332952.5. Open not returned; keep quarantine; no market rows changed.
- P5: exact-symbol inventory reconciliation established; per-security date coverage denominator still blocked by historical instrument lifecycles and verified session calendar.
- P6: no production signal or training enablement. End-to-end scanner readiness not demonstrated in this checkpoint.

## Next-five execution checkpoint — 2026-11-26
- Task 1: 8/37 unmatched historical filenames decode to exact official debt-security symbols; 29 remain unresolved. 488 exact plus 8 encoding candidates = 496/525. No rename applied. Review: reference/nepse_unmatched_symbol_review_2026-11-26.csv.
- Task 2: 281 rendered equity rows collapse to 278 unique symbols (USLB and SYPNL duplicates); 47 unique mutual funds; all 325 distinct candidates match active official security IDs. 324 have OHLCV files; NICEF absent. Three additional equity identities not established. No historical lifecycle inferred. Dataset: reference/nepse_target_universe_candidates_2026-11-26.csv.
- Task 3: recovered 225 distinct primary positive-trade dates from RHGCL official captured history (2025-11-25 to 2026-11-19), no overlap with 2026 closure calendar. Single-security observations not a complete canonical exchange calendar. Dataset: reference/nepse_primary_observed_open_sessions_2025-2026.csv.
- Task 4: sample seven symbols all have 225 observed dates; 5 date-level structural/uniqueness exceptions across API, BGWT, HRL and RAWA. NICEF absent. Full universe and listing-adjusted coverage still pending. Sample: reference/nepse_observed_session_coverage_sample_2026-11-26.csv.
- Task 5: scanner route still uses date-only as_of filtering, not available_at timestamp eligibility. Keep training and production signals disabled until integrated no-lookahead and canonical eligibility enforcement are tested. No existing market-price rows changed.
