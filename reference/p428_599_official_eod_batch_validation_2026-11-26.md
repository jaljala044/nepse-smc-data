# P4.28 — official NEPSE EOD validation for 599 historical candidates

Date: 2026-11-26  
Status: complete-board official capture and row-level validation passed; correction ledger generated.

## Executive result

The official NEPSE EOD board was captured for all six candidate business dates. Every page was preserved byte-for-byte, and every target symbol/date row was found exactly once.

| Validation | Result |
|---|---:|
| Candidate rows audited | 599 |
| Unique symbols | 254 |
| Complete official board captures | 6/6 |
| Official rows found exactly once | 599/599 |
| Official capture accepted with zero quality flags | 599/599 |
| Official security ID matches current instrument snapshot | 599/599 |
| Exact OHLCV matches to candidate source | 487 |
| Official-source corrections required | 112 |
| Missing or duplicate official rows | 0 |

The current security-ID snapshot dated 2026-11-25 maps all 254 candidate symbols exactly once with unique IDs. The official EOD rows independently return matching symbol/security-ID pairs for all 599 date-scoped records. This is historical identity evidence for these captured dates; it does not complete the wider 525-file effective-dated instrument master.

## Complete official board captures

Endpoint for every date:

`https://www.nepalstock.com/api/nots/nepse-data/today-price?size=500&page=0&businessDate=YYYY-MM-DD`

| Business date | Board rows | Retrieval time (NPT) | Raw response SHA-256 |
|---|---:|---|---|
| 2026-03-01 | 341 | 2026-11-26 23:00:15.162202 | `f95a54e751d3fe604c25e797e948831a35928166e2efea2319e244c9c359a5b5` |
| 2026-07-24 | 353 | 2026-11-26 23:00:19.003197 | `84c19dfc08fdb6dc75eb9c878a0bd4893aa91b95fac8f780fdba181529ddfe7a` |
| 2026-04-24 | 351 | 2026-11-26 23:00:22.977057 | `fd154d21f4f188d0a9f729231a94730b2112d4c8a15f09f0df04852e44228e7b` |
| 2026-04-27 | 351 | 2026-11-26 23:00:26.274142 | `11f84c9ddd72c0947565406203145dfe63c3ef197a08ea1dade3e59d417fe17e` |
| 2026-04-28 | 349 | 2026-11-26 23:00:30.708115 | `7d896a22e53916e70cd0de260313113fb4269e6b880a8bb9d0ab448dda2fcf31` |
| 2026-04-29 | 351 | 2026-11-26 23:00:34.669248 | `d359f2eda7f42562e3512743ee1215cfa7865212059fb59580b50893e262f79c` |

All six responses were one page each; page row counts equal the API's `totalElements`. The original JSON response bodies, manifests, and hashes are retained in the immutable workflow artifact.

## What the official data resolved

### 109 invalid external OHLCV candidates

All 109 official rows pass the NEPSE validator with zero quality flags. The discrepancy is isolated to **Open**:

- 88 external candidates had Open above High.
- 21 external candidates had Open below Low.
- Official NEPSE Open is within the official High–Low range for all 109.
- High, Low, Close, Volume and Turnover match the candidate rows in all 109 cases.
- The 109 external Open values are not used; the official Open values are the primary-source values.

These rows can leave the invalid-source quarantine once the P4.29 derived correction ledger is applied. Do not edit the raw source archives.

### 490 one-day date-shift candidates

- 487/490 candidate OHLCV tuples match official NEPSE exactly.
- Three 2026-03-01 closes differ from the later ShareSansar backfill:
  - KBL: candidate 192.00; official 191.80
  - SAIL: candidate 1,306.00; official 1,329.00
  - ULBSL: candidate 3,118.00; official 3,178.00
- For these three rows, Open, High, Low, Volume and Turnover match; only Close differs.
- Official EOD confirms the 2026-03-01 and 2026-07-24 business dates for all 490 target rows. The following raw SMC dates (2026-03-02 and 2026-07-25) are closed dates in the pinned session calendar.

Use the official values for derived history. Preserve the raw SMC rows and their original dates.

## Correction ledger

The [112-row official correction ledger](p428_112_official_eod_corrections_2026-11-26.csv) records each changed field, candidate and official tuples, official security ID, raw payload SHA-256, endpoint URL and retrieval timestamp.

- 109 rows: Open correction.
- 3 rows: Close correction.
- All 112 rows: official capture accepted, zero quality flags, security ID match.

The [599-row full reconciliation matrix](p428_599_official_eod_reconciliation_2026-11-26.csv) includes the 487 exact-match rows as well as all corrections.

## Reproducibility

- Capture tool: `tools/capture_nepse_official_eod_board.py`
- Batch validator: `tools/audit_p428_official_eod_batch.py`
- Correction-ledger builder: `tools/build_p428_official_eod_corrections.py`
- Tests: `tools/tests/test_audit_p428_official_eod_batch.py` and `tools/tests/test_build_p428_official_eod_corrections.py`
- CI run: [45866097177](https://github.com/jaljala044/nepse-smc-data/actions/runs/45866097177)
- Immutable payload + matrix artifact: [15139463647](https://github.com/jaljala044/nepse-smc-data/actions/runs/45866097177/artifacts/15139463647)
- Artifact ZIP SHA-256: `cbce448ecabe823dd5a23fcc92e8b6c53cc14f3a2a7f631c958e23532cd77984`

## Disposition and next priority

P4.28 establishes primary official EOD evidence for all 599 candidates. No raw source archive was changed.

**P4.29 — apply the 599 official EOD records to the provisional derived series.** Apply the 112 corrections, promote the 490 date-shift mappings using official business dates, preserve exact evidence references for the 487 unchanged rows, and add tests proving that raw files remain byte-identical and that no unverified rows are promoted.
