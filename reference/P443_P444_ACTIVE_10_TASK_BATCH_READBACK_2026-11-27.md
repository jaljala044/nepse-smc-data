# P4.43/P4.44 active work packages #10 and #13–#22 — evidence read-back

Date: 2026-11-27  
Branch: `p443-global-integrity-audit`

## Artifact and run provenance

The latest successful P4.43 global-integrity workflow reviewed in this pass is run **46033103956** (run #324), global-integrity job conclusion `success`. Its strict-content artifact is ID `15214839272`, size 58,301,106 bytes, GitHub digest and independently recomputed ZIP SHA-256:

`afed913e7c2c45f98f90633f5c6c4a07ed2a54dfb6fb08a23c668fedab5aab98`.

The job completed inventory verification, read-only scan, strict-content tests, scanner quarantine tests, Drive quarantine retrieval regression tests, pinned-byte cross-check, exception reconciliation, repeated-candle classification, P4.44 matrix/lifecycle tests and the full 281-payload audit. All listed global-integrity job steps passed.

## #10 — all 281 security-history payloads

The artifact's `P444_281_SECURITY_HISTORY_CAPTURE_AUDIT_2026-11-27.json` reports:
- 281 payload files and 281 manifest symbol entries;
- 281 symbols; 8,142 total rows, dated 2026-10-05 through 2026-11-26;
- manifest SHA-256 match for every payload;
- zero row-level issues;
- zero symbols with Open price; 281 symbols without an Open field;
- audit `valid=true`; canonical data unchanged; promotion disallowed.

**Disposition: audit complete for this pinned capture.** It verifies payload integrity and row-level structure, not historical security-ID continuity. No Open value is synthesized.

## #13 — 928-file inventory

The artifact `coverage.json` contains exactly 928 entries. Every entry's pinned content hash and byte count was checked by the strict-content audit; the run's inventory and pinned-byte verification steps passed. Status distribution:
- 784 structured files parsed;
- 89 text files inspected;
- 36 Python files syntax-checked;
- 11 workflow YAML files syntax-checked;
- 2 PDFs identified for manual review;
- 6 non-JSON provider error responses isolated;
- zero failed files.

**Disposition: inventory and pinned-byte verification complete.**

## #14 — inventory-only / unsupported formats

All 138 inventory-only files received format-appropriate inspection: 89 text inspections, 36 Python syntax checks, 11 YAML syntax checks and two one-page PDFs identified for manual review. The PDFs yielded no extractable text and are not semantically certified. The six provider error bodies are separate from the 138 inventory-only files and were not counted as market data.

**Disposition: format-appropriate automated inspection complete; two PDFs remain manual-review exceptions.** No unsupported file was silently counted as parsed market rows.

## #15 — counting-unit reconciliation

Already reconciled: 1,650,790 CSV/CSV.GZ data rows plus 17,851 JSON record elements = 1,668,641 parsed records. The alternative global count uses 93 JSON documents, not JSON elements. Keep those units separate.

## #16 — exact duplicates and business keys

The strict scan emitted:
- 10 exact repeated JSON objects, all summary-object repeats in two P4.37 capture reports (not trade rows);
- zero `duplicate_business_key` or `conflicting_business_key` findings;
- zero duplicate full transaction rows in the reviewed P4.33 archive capture metadata;
- 1,331 invalid-OHLCV findings, a different class from duplicates.

Important exception: the P4.33 third-party floorsheet archives for 2024-08-14 and 2024-08-18 reuse `contract_no` values extensively. For 2024-08-14: 244,019 rows, 119,389 repeated contract-number occurrences, 47,427 repeated groups, 22,329 cross-symbol collisions, but 244,019 unique record IDs and zero duplicate full rows. For 2024-08-18: 300,918 rows, 142,724 repeated contract-number occurrences, 58,864 repeated groups, 27,893 cross-symbol collisions, but 300,918 unique record IDs and zero duplicate full rows. The 2024-08-18 SMPDA subset has 192 rows and 192 unique record IDs, although 15 contract numbers repeat within that symbol.

Therefore `contract_no` is not a safe global row primary key in these archives. The source-scoped, session-scoped record `id` is the stronger row identity candidate. This does not prove exchange authority or completeness.

**Disposition: PARTIAL.** Exact duplicates and current scan findings are counted; the contract-number reuse pattern requires explicit row-identity semantics and full source/session crosswalk.

## #17 — repeated adjacent OHLCV tuples

All 94,543 adjacent repeated tuple pairs were classified:
- 26,544 pairs touch a historically listed-holiday candidate;
- 9,027 pairs contain a recorded market-wide closure;
- 73 pairs have both dates open but tuple remains unverified;
- 58,899 pairs have insufficient session evidence.

The queue split is 35,571 pairs for quarantine review and 58,972 for independent security-date evidence. The 23,377-pair P4.44 matrix is the uncovered subset across 209 symbols. All remain review/hold only; zero rows corrected or promoted.

**Disposition: PARTIAL.** Classification is complete for the 94,543 pair set; source-level adjudication is not.

## #18 — full date-lineage scan

The known-audit crosswalk reconciles 2,067 distinct symbol/source-date keys across P4.27/P4.28, P4.5, P4.37 and P4.42. Existing lineage rows cover 68,783 rows across 253 symbols. However, 209 of the 462 symbols with repeated-tuple findings are not represented in that source-lineage table; full 928-file date-shift adjudication, full-period official calendar and historical instrument identity remain incomplete.

**Disposition: BLOCKED/PARTIAL evidence base.** The prior-audit crosswalk is reproducible but does not satisfy full-scope row-level lineage.

## #19 — 2026-03-01 / 2026-03-02 archive conflict

The 2026-03-01 partition has 13 symbols, 30 transactions, 364,868 quantity and NPR 65,246,109.50 turnover. The alternative 2026-03-02 partition has 341 symbols, 55,206 transactions, 13,193,462 quantity and NPR 5,648,319,041.36 turnover. An independent published 2026-03-01 market summary reports 341 companies and 55,206 transactions, making a one-day label-shift hypothesis plausible. It does not authenticate the raw archive date or establish all transaction totals from an exchange-origin source.

**Disposition: UNRESOLVED.** Keep both original partitions intact; publication remains disallowed.

## #20 — floorsheet identity uniqueness with session/source scoping

The 22-session two-archive comparison has 21 exact full-session parity dates and one 2026-04-10 row conflict (10,081 secondary-only rows). The report states zero duplicate contract-number occurrences within each of those 22 individual session files; however, this result is limited to that selected batch and does not resolve P4.33's 2024-08-14 / 2024-08-18 repeated contract numbers. The P4.33 records have unique `id` values even where `contract_no` repeats.

Recommended identity key for the audit contract: `source repository + source revision/blob + session date + record id`. Retain `contract_no` as a business/reference field, not as a global unique key. Cross-source parity should compare normalized row tuples without collapsing repeated contract numbers.

**Disposition: PARTIAL.** The identity distinction is established in reviewed samples; full date/source coverage and authoritative source lineage are not.

## #21–#22 — scanner/publication holds and tests

Latest publication-gate run 46033103764:
- combined unittest command for canonical publication, historical/scanner quarantine, Drive quarantine, P4.44 lifecycle holds, lifecycle sequence audit and lifecycle validator: passed;
- Python compilation: passed;
- actual private Drive quarantine overlay verification: failed because the required private Drive credential/verification path was unavailable.

**#21:** lifecycle-symbol hold integration remains implemented and tested; do not release holds on this workflow result.  
**#22:** regression coverage passed, but end-to-end workflow remains partial because private Drive verification failed.

## Merger successor handling — correction to apply

For confirmed mergers, represent the predecessor-to-successor relationship as a directed identity edge and use the successor's current ticker/security identity for post-merger/current-security lookups. Preserve predecessor OHLCV and source rows under their original historical ticker and dates; do not rewrite history or combine predecessor and successor price series without a documented corporate-action adjustment. In the reviewed evidence set, JALPA and KLBSL point to MATRI, while SABSL and SDLBSL point to SMPDA. These successor codes are the operational lookup targets; the old predecessor symbols are lifecycle aliases, not separate currently active securities. Any successor security ID must still be fetched from the applicable dated/current security master rather than copied from a predecessor ID.

## Data safety

No raw captures, OHLCV, canonical data, lifecycle dispositions or scanner inputs were modified or promoted by this read-back. This document records existing artifact evidence and corrects audit semantics only.


## Merger successor mapping correction (2026-11-27)

Current successor lookups are now explicit in `P444_MERGER_SUCCESSOR_CURRENT_ID_CROSSWALK_2026-11-27.csv`: JALPA/KLBSL → MATRI (security ID 694), SABSL/SDLBSL → SMPDA (security ID 2896), and SAMAJ → GBLBS (security ID 583), all using the 2026-11-25 snapshot. These five predecessor symbols are not to be treated as standalone current securities where the successor relationship is established. Preserve their historical OHLCV under the predecessor tickers; use successor code/ID for current lookups. Do not reuse a successor ID as the predecessor's historical stable ID, and do not infer unresolved merger dates or last-trade boundaries.


## P4.23 status correction — RHGCL primary EOD capture (2026-11-27)

A fresh read-back of the committed official evidence supersedes the earlier statement that RHGCL Open was absent and the key remained only partially confirmed. The committed `reference/official_eod_captures/RHGCL_2026-11-19_nepse_eod.json` contains a validated official NEPSE row for security ID 8108 / RHGCL / 2026-11-19 with Open 252.10, High 259.50, Low 252.10, Close 258.00, quantity 9,054, turnover NPR 2,332,952.50 and 47 trades. The source response is one page (347 upstream rows), HTTP 200, captured 2026-11-26T22:33:29.871784+05:45; raw payload SHA-256 is `303d92756ffbcaa2e6ab5020c29e1eab1b63ed99797bf024914dbb863cbae183`. The validator status is `OFFICIAL_CAPTURE_ACCEPTED` with zero quality flags.

The versioned derived OHLCV decision is therefore supported for RHGCL 2026-11-19: use the official full OHLCV tuple; preserve the discrepant SMC raw tuple unchanged. This does not resolve the other 86 conflict keys dated 2025-07-28. The 86-row secondary counterpart index remains complete (86/86, no missing or duplicate keys), but all 86 remain `CONFLICT_UNRESOLVED_PRIMARY_EVIDENCE_PENDING`. Their timestamp/order blocker remains: the candidate YONEPSE archive has no trade timestamps, so Open/Close must not be inferred from contract-ID ordering.

**Corrected work-package #26 disposition:** 86 unresolved 2025-07-28 keys; RHGCL 2026-11-19 primary-confirmed separately. No raw source rows changed in this read-back.


## Run #336 — explicit floorsheet row identity and global audit read-back

- Run #336 completed successfully (59/59 workflow steps) on exact tested code SHA `c261b1c0e3c64cd1268a92eaaf0690cb028a738d`: https://github.com/jaljala044/nepse-smc-data/actions/runs/46043405148
- Global artifact ID `15221652252`; downloaded ZIP SHA-256 `5dd8dd7ce89e538510745c28683058d2140b7fc9e50d65387c450b7606898248`, matching GitHub artifact metadata. Strict artifact ID `15221597345`; downloaded ZIP SHA-256 `1242b5abcd38f7a37f7f819b44992b8d202d2075d7b9f1a57f949138a1b30d01`, also matching GitHub metadata.
- The global report covers the pinned 928-file inventory: 691 parsed CSV files, 93 parsed JSON documents, 1,650,883 CSV rows plus JSON documents, zero parse errors, and 150 unsupported file/check combinations. It reports zero OHLCV duplicate symbol/date keys, zero OHLCV exact duplicate rows, zero floorsheet explicit record-ID repeats within source file/session, zero exact repeated floorsheet rows and zero duplicate dates within a calendar file.
- The audit no longer manufactures a record ID from contract number + symbol + buyer + seller when an explicit source transaction/record ID is absent. Such a check is marked unsupported; exact full-row repeat detection remains separate. This is a pinned-scope result, not a global uniqueness guarantee.
- **#16 disposition:** complete for the pinned 928-file audit and implemented checks, with the 150 unsupported checks explicitly retained as limitations.
- **#17 disposition:** complete for classification only. The strict artifact has 94,543 unique adjacent repeat-pair findings: 26,544 historical-holiday candidates, 9,027 recorded-closure pairs, 73 both-open/unverified pairs and 58,899 insufficient-session-evidence pairs. The review split is 35,571 quarantine-review and 58,972 independent-evidence. Zero rows corrected or promoted.

## Work package #18 — exact lineage coverage gap recheck

Using the Run #336 strict artifact files `repeat_calendar_triage.csv` and `equity_security_date_source_lineage.csv`, independently compared exact `(symbol, date)` keys without alias or ticker-similarity matching:

- Repeat-pair set: 94,543 unique symbol/date keys across 462 symbols.
- Existing lineage set: 68,783 unique symbol/date keys across 253 symbols.
- Exact intersection: 47,665 keys.
- Repeat-pair keys without lineage: 46,878.
- Symbol coverage: 209 symbols have no lineage keys, 245 have partial coverage, and only 8 have every repeat-pair key covered.
- Existing lineage keys outside the repeat-pair set: 21,118.

This refines the earlier symbol-only gap statement: 209 symbols are entirely uncovered, but partial gaps also remain across 245 other symbols. The crosswalk is therefore not full-scope even for symbols already represented. The count measures evidence-index coverage only; it does not prove missing sessions, non-trading days, date shifts or source errors. Work #18 remains PARTIAL pending the full 525-file lineage scan and authoritative identity/calendar evidence.

No raw OHLCV, floorsheet, calendar, canonical or scanner-input rows were changed. No corrections, promotions or hold releases occurred.


## Work package #18 — Run #338 CI and exact artifact read-back

- The initial Run #337 export failed because its YAML folded command did not deliver the required CLI arguments; the three new regression tests passed. Corrected in commit `f0965688f085050e1a9499bfbca80d60dffe2c3f`.
- Run #338 (`46046751745`) passed the complete P4.43 workflow on branch head `f0965688f085050e1a9499bfbca80d60dffe2c3f`. New regression step and exact gap-export step both passed.
- Strict artifact `15222152680`: 58,728,598 bytes; SHA-256 `96cbdb5f7d4275c5ee93337b11525237910192897ef4482f92110a6b7f01109d` (matches GitHub metadata). Global artifact `15221704196`: 1,403,280 bytes; SHA-256 `3e6f452d17bf49f57d504706079e6fecddfd938e67b64c4503d60a38d651f0cc` (matches GitHub metadata).
- New gap CSV: 46,878 unique uncovered `(symbol,date)` rows across 454 symbols. Summary: 94,543 repeat-pair keys / 462 symbols; 68,783 lineage keys / 253 symbols; 47,665 exact intersections; 46,878 uncovered; 21,118 lineage keys outside the repeat-pair set; 209 symbols with no lineage, 245 partial, 8 full. All exported gap rows are explicitly `lineage_covered=false` and `promotion_allowed=false`.
- #18 remains PARTIAL: the exporter measures the current lineage register; it does not construct complete lineage for all 525 OHLCV files or supply authoritative identity, session-calendar and execution evidence. No source/canonical data changed and no hold was released.


## Work package #19 — March 1/2 archive conflict: independent publication cross-check

Two dated secondary reports independently publish the same session totals for 2026-03-01: Nepal News reports 341 companies, 13,193,462 shares and 55,206 transactions, with turnover rounded to NPR 5.64 billion (https://english.nepalnews.com/s/business/nepse-rises-by-19-27-points-to-close-at-2674-20/); Ratopati reports the same counts and exact turnover NPR 5,648,319,041.36 (https://english.ratopati.com/story/51155/nepse-rises-by-072-percent). NEPSE's public Market Summary History page currently returns no data rows (https://nepalstock.com.np/market-summary-history).

This independently corroborates the alternative 341-symbol partition's *reported session totals* for March 1. It does not authenticate the underlying 2026-03-02-labelled raw archive, its retrieval date or source, nor explain the separate 13-symbol/30-transaction March 1 partition. Both original partitions remain unchanged; no date relabeling or publication is allowed. Work #19 is now PARTIAL rather than wholly unresolved, pending exchange-origin raw evidence and source-provenance recovery.
