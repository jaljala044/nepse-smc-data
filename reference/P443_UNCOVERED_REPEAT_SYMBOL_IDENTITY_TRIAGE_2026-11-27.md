# P4.43 — uncovered repeat-symbol identity and instrument-scope triage

Date: 2026-11-27  
Pinned global-audit source commit: `56362fb4f65b91fdcca8f50b50e53ad80e703649`  
External reference commit: `5a8768828d58bdcebb82393262726d1d030b7ec4`

## Result

All 209 uncovered repeat-finding symbols were cross-checked against four dated reference files: the target-universe candidate register, security snapshot, equity crosswalk and unmatched-symbol review.

| Measure | Count |
|---|---:|
| Symbols assessed | 209 |
| Current snapshot matches | 175 |
| No current snapshot match | 34 |
| Target-candidate registry classifies as Mutual Fund | 39 |
| Current equity-crosswalk matches | 3 |
| Snapshot-name debenture/bond candidates | 61 |
| Snapshot-name promoter-share candidates | 62 |
| Other snapshot records requiring class review | 10 |
| Unmatched-review rows | 34 (26 unresolved historical identity; 8 filename-encoding candidates) |

Snapshot status among matches: 172 `A`, 3 `S`.

## Findings

- **Mutual funds:** 39 symbols are classified as `Mutual Fund` in the dated target-candidate registry. Thirty-four have names that also indicate a fund/yojana; five additional records have non-obvious names in the snapshot and are identified by the candidate register: `H8020`, `LUK`, `RBBF40`, `SIGS2`, `SIGS3`.
- **Equity:** NESDO/8041, ULBSL/8063 and YMHL/9342 match the current equity crosswalk. The separate Priority 94 report supports their equity classification using approved-provider evidence. These are dated current IDs, not historical identity intervals.
- **Other instruments:** 61 snapshot display names suggest debentures/bonds and 62 suggest promoter shares. These are name-based candidates, not authoritative type fields.
- **Unresolved snapshot records:** 10 snapshot rows are not classifiable from the target registry or conservative name rules and remain `SNAPSHOT_PRESENT_CLASS_REVIEW`.
- **No current snapshot:** 34 symbols are absent; the existing unmatched review lists 26 as unresolved historical identities and eight as filename-encoding candidates. Candidate IDs/decoded names are not promoted.

## Evidence sources

External files at `5a8768828d58bdcebb82393262726d1d030b7ec4`:
- target candidate register blob `45f71a3a81dbe883c8562cf6d7d9e8da9bf51bc4`
- dated security snapshot blob `ed548857eb550fbb237910eb903fc202751c63a1`
- unmatched-symbol review blob `be595b84d07a32ffc76a7cadfa9dff91aebec8bb`
- equity crosswalk blob `9711b068f353f8129283258d6d14e3b73dd978fa`

The row-level CSV preserves each source's symbol, candidate ID, snapshot ID/status/name, unmatched-review disposition and triage result.



## Historical identity evidence overlap for the 34 snapshot-unmatched symbols

A further comparison against the existing Priority 97 historical-identity evidence JSON (external blob `589f4ac19451f3faecee41727b44fc62cdeeb818`) found records for **26 of the 34** symbols absent from the current security snapshot. The 26 existing records cover 17 equity, 6 mutual-fund, 10 debenture, and 3 promoter-share records in the source evidence dataset overall; for the 26 matched symbols specifically, the CSV records preserve their instrument classes and event notes. The eight without a matching Priority 97 record are: `GBILD84~2F85`, `GBILD86~2F87`, `MND84~2F85`, `NICAD85~2F86`, `NIFRAUR85~2F86`, `NMBD87~2F88`, `NMBD89~2F90`, `NMBUR93~2F94`.

These records include secondary-source merger, maturity, redemption, delisting and ticker-identity evidence. They do not resolve historical stable IDs or exchange-certified effective trading intervals: all matched records retain `stable_id=null` and `effective_date_verified=false`. Corporate joint-transaction dates and reported last-trade dates must not be treated as the same boundary. No OHLCV rows were spliced or altered.

## Limits and disposition

Current-snapshot presence/absence does not establish historical identity, lifecycle dates, or whether a repeated OHLCV tuple is valid. Debenture/bond and promoter classes are display-name clues only; the ten other snapshot records remain unresolved. All 23,377 repeat-pair findings remain `HOLD/UNKNOWN` pending date-matched official evidence. No OHLCV values, canonical identities, histories, or scanner coverage were changed or promoted.
