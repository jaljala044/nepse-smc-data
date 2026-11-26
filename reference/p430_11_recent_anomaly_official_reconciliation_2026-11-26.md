# P4.30 — official reconciliation of 11 recent OHLCV anomalies

Date: 2026-11-26  
Status: complete official board captures; all 11 rows accepted; 11 Open corrections proven.

## Executive result

The v2 integrity audit found 11 recent `OPEN_OUTSIDE_RANGE` anomalies on four business dates. P4.30 captured the complete official NEPSE EOD board for each date and reconciled every flagged symbol.

| Measure | Result |
|---|---:|
| Recent anomaly candidates | 11 |
| Complete official boards | 4/4 |
| Official rows found exactly once | 11/11 |
| Official row validation | 11/11 accepted, zero quality flags |
| Security-ID match | 11/11 |
| OHLCV tuple exact matches | 0/11 |
| Official Open corrections | 11 |
| High / Low / Close / Volume unchanged | 11/11 |
| Raw OHLCV files modified | 0 |

Every row differs only in Open. The official Open is within the official High–Low range. High, Low, Close and Volume exactly match the candidate v2 row. The official source therefore resolves all 11 recent invariant flags as external Open-field errors.

## Official correction values

| Symbol | Business date | Candidate Open | Official Open | Security ID |
|---|---|---:|---:|---:|
| MERO | 2026-04-24 | 731.1 | 730.0 | 1741 |
| UAIL | 2026-04-24 | 449.9 | 445.0 | 180 |
| API | 2026-04-27 | 339.9 | 345.0 | 697 |
| RAWA | 2026-04-27 | 648.7 | 640.0 | 9181 |
| SPDL | 2026-04-28 | 408.0 | 404.0 | 2759 |
| BGWT | 2026-04-29 | 740.0 | 720.0 | 9214 |
| HRL | 2026-04-29 | 685.5 | 685.0 | 9234 |
| RADHI | 2026-04-29 | 780.0 | 775.0 | 2776 |
| RAWA | 2026-04-29 | 615.0 | 610.0 | 9181 |
| UAIL | 2026-04-29 | 446.0 | 442.6 | 180 |
| UNHPL | 2026-04-29 | 487.9 | 480.2 | 2831 |

The row-level [official reconciliation matrix](p430_11_recent_anomaly_official_reconciliation_2026-11-26.csv) records the official OHLCV tuple, security ID, payload SHA-256, exact official endpoint and retrieval timestamp. The [11-row Open correction ledger](p430_11_official_open_corrections_2026-11-26.csv) records only the supported Open-field changes.

## Official capture details

The official NEPSE EOD API returned a complete one-page board for each date:

| Business date | Official board rows | Raw payload SHA-256 |
|---|---:|---|
| 2026-04-24 | 351 | `fd154d21f4f188d0a9f729231a94730b2112d4c8a15f09f0df04852e44228e7b` |
| 2026-04-27 | 351 | `11f84c9ddd72c0947565406203145dfe63c3ef197a08ea1dade3e59d417fe17e` |
| 2026-04-28 | 349 | `7d896a22e53916e70cd0de260313113fb4269e6b880a8bb9d0ab448dda2fcf31` |
| 2026-04-29 | 351 | `d359f2eda7f42562e3512743ee1215cfa7865212059fb59580b50893e262f79e` |

The immutable raw board responses and the generated queue are retained in workflow artifact [P4.30 official EOD recent anomalies](https://github.com/jaljala044/nepse-smc-data/actions/runs/45869372376/artifacts). The run used the official NEPSE API over HTTPS and retained TLS verification.

## Field and provenance limitations

- Turnover is present in the official EOD rows but absent from the v2 per-symbol OHLCV CSV schema. It is retained in the reconciliation matrix but is not compared or used to infer a correction.
- The 11 corrections are evidence-backed but have not yet been applied to the v2 files. P4.31 will apply them to a new derived release and prove raw/v2 preservation.
- No official price row is used to infer other dates or other securities.

## Remaining historical quality flags

The full v2 audit recorded 1,379 OHLCV invariant flags:

| Flag | Rows |
|---|---:|
| OPEN_OUTSIDE_RANGE | 1,325 |
| CLOSE_OUTSIDE_RANGE | 28 |
| HIGH_BELOW_LOW | 22 |
| NONPOSITIVE_PRICE | 4 |

The 11 P4.30 rows account for all 2026 invariant flags in this audit. The remaining 1,368 flags are historical rows from 2009–2020 and remain unresolved. They are concentrated in AHPC (607), SKBBL (381), API (123), MERO (105), SPDL (73), CHL (48) and HIDCL (32), with smaller counts in other symbols.

Do not bulk-fix these older rows. Their official daily records may be outside the rolling official EOD retrieval window. Keep them flagged/UNKNOWN until date-specific primary evidence or an independently validated historical archive supports a correction.

## Reproducibility

- Queue builder: `tools/build_p430_recent_anomaly_queue.py`
- Official EOD reconciler: `tools/audit_p430_recent_official_eod.py`
- Correction ledger builder: `tools/build_p430_official_open_corrections.py`
- Tests: `tools/tests/test_build_p430_recent_anomaly_queue.py`, `tools/tests/test_build_p430_official_open_corrections.py`
- Successful push CI: [45869372376](https://github.com/jaljala044/nepse-smc-data/actions/runs/45869372376)
- Successful PR CI: [45869379501](https://github.com/jaljala044/nepse-smc-data/actions/runs/45869379501)

## Next priority — P4.31

Build a new derived OHLCV release from v2 with exactly these 11 official Open corrections. Verify the 11 resulting rows against the official matrix, preserve v2 and raw Git blob hashes, test idempotency and duplicate rejection, then rerun the full 281-symbol integrity audit. Keep the 1,368 historical anomalies unresolved and excluded from any signal requiring valid OHLCV.
