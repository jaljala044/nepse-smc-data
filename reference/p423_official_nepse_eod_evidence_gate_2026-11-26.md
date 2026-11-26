# P4.23 — Official NEPSE EOD evidence gate (first implementation slice)

Date: 2026-11-26

## Objective

Accept an official NEPSE end-of-day row only when the original response bytes, exact symbol/date identity, official endpoint URL, timezone-aware retrieval time and OHLCV fields are all available. Keep the source payload immutable and never modify the raw OHLCV archive as a side effect.

## Implemented

- `tools/validate_nepse_eod_capture.py` reads a preserved JSON payload offline.
- Requires an HTTPS NEPSE official host, timezone-aware retrieval timestamp, expected symbol and exchange-local business date.
- Requires exactly one matching row and all key EOD fields.
- Validates positive OHLC, non-negative volume/turnover/trade count, and OHLC range integrity.
- Emits `OFFICIAL_CAPTURE_ACCEPTED` only when the row has no quality flags. A close/open outside the daily range becomes `OFFICIAL_CAPTURE_REVIEW_REQUIRED`, not a silent pass.
- Records the original payload SHA-256, source URL, retrieval time, row, parsed values and `raw_archive_mutated=false`.
- Adds regression tests and a focused GitHub Actions workflow.

## Local usage

```bash
python tools/validate_nepse_eod_capture.py \
  --payload evidence/nepse_eod_2026-11-19.json \
  --symbol RHGCL \
  --date 2026-11-19 \
  --source-url 'https://www.nepalstock.com/<exact-eod-endpoint>' \
  --retrieved-at '2026-11-26T10:00:00+05:45' \
  --output evidence/validated/RHGCL_2026-11-19.json
```

The URL above is a placeholder path: operators must record the exact endpoint used for the actual capture. Do not invent an endpoint or claim that a capture exists because the validator passes synthetic tests.

## Current RHGCL state

No authenticated official NEPSE EOD payload for 2026-11-19 has been captured in this task. The public NEPSE page was not machine-readable in the browser retrieval. The validator is therefore ready for a real capture but has not promoted the secondary-source-corroborated 258.00 / 9,054 value to official status.

## Remaining P4.23 work

1. Capture the actual NEPSE EOD response for RHGCL 2026-11-19 while it remains within the official rolling history window.
2. Preserve the unmodified response and run the validator against it.
3. Compare official OHLCV, ShareSansar-derived history, history-starter and SMC raw values; require the official payload hash and row to be present in the evidence ledger.
4. If the official record confirms 258.00 / 9,054, update only the versioned derived record and retain the SMC raw source unchanged. If it differs, retain UNKNOWN pending reconciliation.
5. Extend the adapter to a batch of all eligible disputed symbols/dates and publish a deterministic row-level evidence CSV.

## Safety

This implementation does not make network requests, scrape the official site, or overwrite historical data. It validates evidence already captured by an authorized operator. It cannot recover 2025-07-28 from NEPSE's documented rolling 365-day history endpoint; the 86 old conflicts remain quarantined UNKNOWN unless permitted primary evidence is found.
