# Derived Common-Equity OHLCV v2 — Official EOD release

Date: 2026-11-26  
**Release branch:** `derived/ohlcv-v2-official-eod`  
**Release commit:** `4255cc293a347857ac77c04a947beb784203062f`  
**Status:** `OFFICIAL_EOD_V2_DERIVED_NOT_FULL_SESSION_CLEAN`

## Dataset

- [Derived v2 directory](https://github.com/jaljala044/nepse-smc-data/tree/derived/ohlcv-v2-official-eod/derived/ohlcv_v2)
- [README and derivation policy](https://github.com/jaljala044/nepse-smc-data/blob/derived/ohlcv-v2-official-eod/derived/ohlcv_v2/README.md)
- [281-symbol manifest](https://github.com/jaljala044/nepse-smc-data/blob/derived/ohlcv-v2-official-eod/derived/ohlcv_v2/manifest.csv)
- [713-row correction ledger](https://github.com/jaljala044/nepse-smc-data/blob/derived/ohlcv-v2-official-eod/derived/ohlcv_v2/corrections.csv)
- [599-row official provenance ledger](https://github.com/jaljala044/nepse-smc-data/blob/derived/ohlcv-v2-official-eod/derived/ohlcv_v2/provenance_ledger.csv)

## Release totals

| Metric | Result |
|---|---:|
| Common-equity symbols | 281 |
| v1 source rows | 246,129 |
| v2 derived rows | 246,238 |
| Official EOD rows applied | 599 |
| Official date shifts | 490 |
| Official rows inserted | 109 |
| Official field corrections | 112 |
| Raw source files modified | 0 |
| Unverified rows promoted | 0 |

The 599 official rows cover 254 symbols across six business dates. All official rows were found exactly once, passed the strict NEPSE EOD validator with zero quality flags, and matched the current security-ID snapshot.

### Changes applied

- 490 raw rows dated on verified closed sessions were moved to their official NEPSE business dates in the derived view only.
- 109 official rows were inserted where the v1 raw-derived files had no row.
- 109 invalid secondary Open values were replaced by official Open.
- Three Close values were replaced by official NEPSE values: KBL 191.80, SAIL 1,329.00 and ULBSL 3,178.00 on 2026-03-01.
- The prior official RHGCL correction (Close and Volume) is preserved.
- The 713-row correction ledger comprises 490 date changes, 109 row insertions, 109 Open corrections, 3 new Close corrections and the 2 prior RHGCL field corrections.

## Preservation

- Every one of the 281 raw source Git blob hashes was revalidated against the v1 manifest.
- The v1 release branch remains unchanged.
- Unaffected v1 symbol files are byte-reused.
- All changes are in the new derived v2 directory; no raw OHLCV source file was edited.
- Adjacent repeated candles and remaining source OHLC invariant flags are retained. This release does not certify full expected-session completeness or full corporate-action adjustment coverage.

## Verification

- Builder: `tools/build_derived_ohlcv_v2.py`
- Regression tests: `tools/tests/test_build_derived_ohlcv_v2.py`
- Workflow: `.github/workflows/derived-ohlcv-v2-official-eod.yml`
- CI run: [45867152948](https://github.com/jaljala044/nepse-smc-data/actions/runs/45867152948)
- Release artifact: [15139594805](https://github.com/jaljala044/nepse-smc-data/actions/runs/45867152948/artifacts/15139594805)
- Artifact ZIP SHA-256: `a3397ddf5d03da97a16950f949ccd0a58d3a42ab7895b54b3adfd504ea2b5143`

## Next priority — P4.30

Run the full 281-symbol v2 integrity gate: validate all OHLCV invariants, duplicate dates, calendar alignment, the 1,329 retained source OHLC invariant flags, repeated-candle classifications and corporate-action adjustment basis. Only after this gate should the scanner consume v2 as its historical price input; any uncovered or conflicting row must remain UNKNOWN.


## P4.30 integrity audit

The full v2 integrity audit is documented in [derived OHLCV v2 integrity audit](derived_ohlcv_v2_integrity_audit_2026-11-26.md). CI run [45868691178](https://github.com/jaljala044/nepse-smc-data/actions/runs/45868691178) passed and retained the findings in artifact [15141173903](https://github.com/jaljala044/nepse-smc-data/actions/runs/45868691178/artifacts/15141173903).

- 281/281 raw source Git blob hashes and 599/599 official provenance rows verified; zero duplicate dates or ordering flags.
- 1,329 unique invalid OHLCV rows remain across 13 symbols (1,379 reason flags); no automatic repair.
- 71,806 adjacent repeated rows remain flagged; five open-session repeat pairs require per-security floorsheet verification.
- Corporate-action coverage remains partial: three recorded events, 278 symbols without records, and one NLIC split proposal without a verified effective date.
- T+2/swing use is conditional on valid bars and liquidity checks; positional/investment adjusted-return metrics remain unsafe until corporate actions are validated.

P4.31 is capturing the official company floorsheets for the five repeat pairs. UNL remains UNKNOWN until its exact symbol/date evidence is reconciled.
