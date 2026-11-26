# P4.23 — RHGCL official EOD capture workflow

The capture path now uses NEPSE's official EOD API endpoint through the public NEPSE client only for its short-lived authentication token and POST payload ID. The capture script sends the request to the official `www.nepalstock.com` host with TLS verification enabled and saves each response body byte-for-byte before parsing it.

## Run

Use GitHub Actions → **P4.23 capture official NEPSE EOD** → Run workflow.

Inputs:
- `business_date=2026-11-19`
- `symbol=RHGCL`

The workflow:
1. Installs the NEPSE API client.
2. Runs the evidence-validator regression tests.
3. Requests all pages of the official EOD board for the requested business date.
4. Saves every exact response body, response URL, retrieval timestamp, byte count and SHA-256 in `capture_manifest.json`.
5. Finds exactly one symbol/date row and runs `validate_nepse_eod_capture.py` on the original page bytes.
6. Uploads the raw pages, manifest and validated row as a 90-day GitHub Actions artifact.

No market data file is committed or overwritten. A failed request, missing symbol, duplicate symbol/date or invalid OHLCV must fail the workflow and preserve any partial capture artifact.

## Evidence promotion rule

The artifact is the primary-source evidence package. Only if the captured official NEPSE row passes validation and its complete fields are reconciled should the versioned derived record be promoted. The existing SMC raw row remains unchanged. If official NEPSE does not match the secondary value, leave the record UNKNOWN pending investigation.

## Validator contract

NEPSE's EOD schema permits some supplemental fields (including turnover and trade count) to be absent. The validator therefore requires identity, OHLC and traded quantity; it validates turnover and trade count when supplied. It does not fabricate missing optional fields.
