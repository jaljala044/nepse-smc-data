# P4.23 — Official NEPSE EOD evidence gate and RHGCL confirmation

Date: 2026-11-26

## Status

**RHGCL 2026-11-19 primary-source confirmation completed.** The official NEPSE EOD API returned exactly one RHGCL row in a 347-row, one-page response. The unmodified response body was preserved as a GitHub Actions artifact and passed the strict evidence validator with zero quality flags.

## Official NEPSE record

| Field | Official value |
|---|---:|
| Symbol | RHGCL |
| Security ID | 8108 |
| Business date | 2026-11-19 |
| Open | 252.10 |
| High | 259.50 |
| Low | 252.10 |
| Close | **258.00** |
| Traded quantity | **9,054** |
| Turnover | NPR 2,332,952.50 |
| Trades | 47 |
| Last updated | 2026-11-19T14:59:54.225031 |

## Capture provenance

- Endpoint: `https://www.nepalstock.com/api/nots/nepse-data/today-price?size=500&page=0&businessDate=2026-11-19`
- Retrieval: 2026-11-26T22:33:29.871784+05:45
- HTTP: 200; content type application/json
- Board: 347 total elements; 1 page; RHGCL found exactly once
- Response bytes: 175,513
- Raw payload SHA-256: `303d92756ffbcaa2e6ab5020c29e1eab1b63ed99797bf024914dbb863cbae183`
- Artifact: [immutable raw response + manifest + validated row](https://github.com/jaljala044/nepse-smc-data/actions/runs/45862108316/artifacts/15137973461)
- Artifact ID: 15137973461; ZIP SHA-256: `72266336645ba3191c441cfa66cd493462b44f7a92fcc68db4b968e0d693a6ee`
- Run: [45862108316](https://github.com/jaljala044/nepse-smc-data/actions/runs/45862108316)
- Committed row and evidence manifest: [RHGCL official EOD JSON](official_eod_captures/RHGCL_2026-11-19_nepse_eod.json)

Validator result: `OFFICIAL_CAPTURE_ACCEPTED`; no quality flags; `raw_archive_mutated=false`.

## Reconciliation and promotion

The official row exactly matches the alternative history row and differs from the SMC raw row only in close and volume:

| Field | SMC raw | Official NEPSE |
|---|---:|---:|
| Open | 252.10 | 252.10 |
| High | 259.50 | 259.50 |
| Low | 252.10 | 252.10 |
| Close | 256.00 | **258.00** |
| Volume | 4,216 | **9,054** |

Decision: the derived RHGCL OHLCV v1 row is confirmed at `2026-11-19,252.1,259.5,252.1,258.0,9054.0`. Its correction ledger now cites NEPSE Official EOD and the payload SHA-256. The derived file bytes remain unchanged because they already contained the correct value. The SMC raw file is preserved unchanged.

The Merolagani floorsheet archive remains incomplete as a secondary tick-level record, but its limitations no longer block the OHLCV close/volume decision because the official EOD board provides the authoritative daily values.

## Implemented capture and validation

- `tools/capture_nepse_official_eod.py`: requests all official EOD pages, stores exact response bytes before parsing, records response URL, timestamp, byte count and SHA-256.
- `tools/validate_nepse_eod_capture.py`: validates exact symbol/date, official HTTPS host, timezone-aware retrieval timestamp, required OHLCV fields, range integrity and provenance.
- `.github/workflows/p423-capture-official-nepse-eod.yml`: manual capture workflow; task-branch push run also executed the RHGCL historical capture.
- `tools/tests/test_validate_nepse_eod_capture.py`: regression tests passed; capture script compiled successfully.

## Remaining boundary

This closes the RHGCL 2026-11-19 P4.23 target. It does **not** resolve the 86 external archive conflicts dated 2025-07-28; those dates are outside the official endpoint's rolling 365-day history window and remain quarantined UNKNOWN absent another permitted primary record. No other symbol/date is promoted by analogy.
