# P4.32 — Official NEPSE merger-listing PDF capture and first-trade boundary audit

**Audit date:** 2026-11-26  
**Repository evidence branch:** `p432-official-listing-pdf-capture`  
**Capture commit:** `f7b928c0dd398dee05a1ae6e0bf697e3267cb31c`

## Result

Both official NEPSE listing PDFs were retrieved from the exchange `fetchFiles` endpoint, validated as PDF responses, saved byte-for-byte, and SHA-256 hashed.

| Symbol | NEPSE document date | Document role | HTTP | Bytes | SHA-256 |
|---|---|---|---:|---:|---|
| NMLBBL | 2024-05-17 | Post-merger share listing and trading release | 200 | 483,523 | `366c28bcb864ea51d9ce4defff49ae0263fe03cff209e352c2a6a222b2e24053` |
| SMPDA | 2024-08-15 | Post-merger share listing | 200 | 516,758 | `f30ea664f83281449c916394631dbac2ad858b293edf4985627a554ca0e15438` |

Raw evidence files:
- `reference/p432_official_listing_documents/NMLBBL_2024-05-17_NEPSE_official.pdf`
- `reference/p432_official_listing_documents/SMPDA_2024-08-15_NEPSE_official.pdf`
- `reference/p432_official_listing_documents/capture_report.json`

Capture timestamp: `2026-11-26T17:39:39.134156Z`. The capture report records the exact source URLs, HTTP status, MIME type, byte length and checksum.

## What these primary documents prove — and do not prove

- **NMLBBL:** the official 2024-05-17 notice concerns 13,377,643 post-merger shares being listed and trading released. It is not a certificate of the first executed trade. The rendered official PDF text states the listing/release action; it does not provide a contract ID or transaction timestamp.
- **SMPDA:** the official 2024-08-15 document is the post-merger share-listing notice. The event ledger records the listing event and opening-range context. It does not establish the first executed contract or prove there were no earlier executions.

The business/merger effective dates and post-merger share-listing dates must remain distinct from the first executed transaction.

## First-trade boundary status

| Symbol | Candidate first positive-volume archive date | Prior session requiring complete floorsheet check | Status |
|---|---|---|---|
| NMLBBL | 2024-05-19 | 2024-05-16 | `UNKNOWN` |
| SMPDA | 2024-08-18 | 2024-08-14 | `UNKNOWN` |

The dates above are candidates from the existing archive boundary audit, not primary-confirmed first trades. To promote either date, obtain:
1. A complete, date-specific NEPSE floorsheet for the candidate date, including all pages and upstream pagination totals, with at least one valid contract for the target security.
2. A complete floorsheet for the immediately preceding confirmed open session, demonstrating zero contracts for the target security.
3. Contract-ID uniqueness, exact business date/security identity, positive quantity and rate, amount arithmetic, and reconciliation to an independent daily EOD record where available.

No partial archive or missing file can establish `NO_TRADE`.

## Reproducibility and tests

- Capture script: `tools/capture_nepse_listing_pdfs.py`
- Regression tests: `tools/tests/test_capture_nepse_listing_pdfs.py`
- CI workflow: `.github/workflows/p432-official-listing-pdf-capture.yml`
- CI run: https://github.com/jaljala044/nepse-smc-data/actions/runs/45869584139

The capture tests passed. The workflow successfully retrieved both official PDFs and committed the exact binaries plus the capture report.

## Disposition

- Official listing-document evidence: **captured and checksum-verified**.
- First executed trade dates: **not verified**.
- NMLBBL and SMPDA lifecycle `valid_from`: **remain UNKNOWN**.
- No canonical OHLCV, lifecycle valid_from, floorsheet, scoring, or training data changed.
- No first-trade claim is promoted from listing dates, merger dates, or secondary-provider archive boundaries.
