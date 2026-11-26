# P4.33 — NMLBBL and SMPDA first-trade floorsheet retrieval attempt

**Audit date:** 2026-11-26  
**Branch:** `p433-first-trade-floorsheet-capture`  
**Workflow run:** https://github.com/jaljala044/nepse-smc-data/actions/runs/45875343647

## Objective

Retrieve exact-date trade-level floorsheets for the candidate first-positive-volume dates and immediately preceding candidate sessions:

| Symbol | Candidate date | Prior session to inspect |
|---|---|---|
| NMLBBL | 2024-05-19 | 2024-05-16 |
| SMPDA | 2024-08-18 | 2024-08-14 |

A positive target-symbol contract on the candidate date plus a complete prior-session floorsheet with no target contracts would be needed to substantiate a first-trade boundary. A missing or partial archive can never prove `NO_TRADE`.

## Retrieval result

The Hugging Face dataset card for `urekmazino69/Nepse-floorsheet-and-indices` describes daily floorsheet files from 2024-01-02 and trade-level fields including contract number, calculation date, symbol, buyer, seller, quantity, rate and amount. The dataset card is a third-party provider statement, not NEPSE primary evidence.

The CI runner attempted the four exact documented object paths:

| Symbol | Date | Requested object | HTTP result | Disposition |
|---|---|---|---:|---|
| NMLBBL | 2024-05-19 | `floorsheet/2024-05-19.csv` | 404 | `UNAVAILABLE` |
| NMLBBL | 2024-05-16 | `floorsheet/2024-05-16.csv` | 404 | `UNAVAILABLE` |
| SMPDA | 2024-08-18 | `floorsheet/2024-08-18.csv` | 404 | `UNAVAILABLE` |
| SMPDA | 2024-08-14 | `floorsheet/2024-08-14.csv` | 404 | `UNAVAILABLE` |

The source URLs, retrieval timestamp and exact HTTP errors are preserved in `reference/p433_floorsheets/capture_report.json`. No raw CSV was received, so no file hash, contract count, daily total, target-symbol contract count, or arithmetic result is asserted.

The public dataset card currently also reports a dataset-generation parsing error for a malformed contract-number value. This is an additional reason not to infer completeness from the card's advertised layout.

## Validation implementation

Added:
- `tools/capture_p433_first_trade_floorsheets.py`
- `tools/tests/test_capture_p433_first_trade_floorsheets.py`
- `.github/workflows/p433-first-trade-floorsheet-capture.yml`
- `reference/p433_floorsheets/capture_report.json`

The four regression tests passed. They cover:
- valid target-symbol contract counting and SHA-256 preservation;
- duplicate contract IDs and wrong-date rejection;
- HTML/non-CSV response rejection;
- unavailable source handling without converting absence into `NO_TRADE`.

## Evidence classification and decision

- Dataset layout/coverage: third-party dataset-card claim.
- Four exact-date requests: observed HTTP 404 responses from the pinned URL pattern.
- Contract-level records: none retrieved.
- Full-session completeness: not demonstrated.
- First-trade boundary: **UNKNOWN for both symbols**.
- No lifecycle `valid_from`, canonical OHLCV, session-calendar status, training labels, or scanner scores were changed.

The 404s establish that these exact objects are not retrievable at the documented paths at retrieval time. They do **not** establish that the target securities did not trade, or that no alternative object path/archive exists.

## Next retrieval route

1. Inspect the Hugging Face repository tree and dataset-server export to identify the actual immutable data objects; do not assume the dataset-card example path exists.
2. If the repository exposes a consolidated Parquet/CSV object, retrieve the immutable file, hash it, and filter the four exact dates by contract-level rows.
3. Independently validate date, symbol, contract ID uniqueness, quantity/rate/amount and session totals.
4. Seek primary NEPSE floorsheet/API records or independently controlled complete-session capture before promoting first-trade boundaries.
5. If no date-specific complete evidence can be obtained, preserve `UNKNOWN`; do not create zero-trade assertions.

## Source references

- Dataset card: https://huggingface.co/datasets/urekmazino69/Nepse-floorsheet-and-indices
- Exact candidate/prior object URLs are recorded in `capture_report.json`.
- Earlier source investigation and evidence requirements: `reference/p414_merger_successor_first_trade_floorsheet_audit_2026-11-26.md`.
