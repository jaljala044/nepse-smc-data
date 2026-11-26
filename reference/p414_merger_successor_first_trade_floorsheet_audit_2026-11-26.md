# P4.14 merger-successor first-trade floorsheet audit — 2026-11-26

## Decision

**No first-trade boundary is promoted in this pass.** NMLBBL and SMPDA remain `UNKNOWN` in the lifecycle coverage input. The public-source investigation identified candidate archives and an advertised historical query interface, but did not retrieve date-specific contract rows or prove complete session coverage for either target date.

This is a useful negative result: the evidence path is now explicit, and no listing date, company-operation date, scheduled commencement, or first positive OHLCV row has been silently substituted for an executed-trade boundary.

## Scope and target dates

| Symbol | Target archive first positive-volume date | Prior NEPSE session to test | Current first-trade status | Why still blocked |
|---|---|---|---|---|
| NMLBBL | 2024-05-19 | 2024-05-16 | UNKNOWN | No date-specific floorsheet contracts, page totals, or complete-session proof retrieved |
| SMPDA | 2024-08-18 | 2024-08-14 | UNKNOWN | No date-specific floorsheet contracts, page totals, or complete-session proof retrieved |

The prior-session dates are candidate sessions for investigation based on the exchange's Sunday–Thursday trading week; they are not evidence that either security had zero contracts on those dates. The 2024-05-17 and 2024-08-15 events are post-merger share-listing/release events already recorded in the typed lifecycle ledger. They do not prove the first executed contract.

## Source investigation

### 1. Hugging Face: urekmazino69/Nepse-floorsheet-and-indices

Dataset card: https://huggingface.co/datasets/urekmazino69/Nepse-floorsheet-and-indices

The public dataset card describes one CSV per trading date under `floorsheet/YYYY-MM-DD.csv`, with fields including `contract_no`, `calculation_date`, `time`, `stock_symbol`, `buyer`, `seller`, `quantity`, `rate` and `amount`. It declares daily coverage beginning 2024-01-02.

Exact object retrieval attempts for:
- `floorsheet/2024-05-19.csv`
- `floorsheet/2024-08-18.csv`

did not return accessible file content in this audit environment. The dataset card's folder example and declared date range do not establish that either exact object exists, that its rows are complete, or that its contents are exchange-origin. No row count, contract ID, hash, or symbol-level result is asserted.

Classification: `PUBLIC_ARCHIVE_LEAD_NOT_RETRIEVED`.

### 2. Nepse Signal historical floorsheet interface

Floorsheet page: https://nepsesignal.com/nepse/floorsheet/

The page describes symbol and business-date filtering and claims historical coverage from 2018 with pagination through a day's contracts. Its methodology page states that daily floorsheets are ingested from the NEPSE API.

These are provider statements, not independently verified source provenance. The public page rendered no floorsheet records during this inspection, and no date-specific query result, response payload, page count, source hash, or export was obtained for either target date. The advertised 2018 coverage therefore remains an unverified lead, not evidence.

Classification: `PROVIDER_CLAIM_QUERY_NOT_VERIFIED`.

### 3. NEPSE API route lead

Public unofficial client code documents a per-company route pattern with a `businessDate` parameter, `totalPages` pagination, and company/security ID lookup. This is useful implementation intelligence only. It does not establish that the route is accessible for historical dates, that the endpoint honors the date parameter, or that returned pages are complete. A separate public pipeline engineering note reports that its tested NEPSE floorsheet API ignored `businessDate` and that the per-company route was blocked (403). The contradictory reports reinforce the need for a captured response, not assumptions.

References:
- https://github.com/basic-bgnr/NepseUnofficialApi/blob/master/nepse/NepseLib.py
- https://ankitsanjyal.github.io/projects/nepse-pipeline.html

Classification: `UNOFFICIAL_ROUTE_LEAD_CONFLICTING_BEHAVIOUR`.

## Evidence required to close each boundary

For each target date and the immediately preceding confirmed open session:

1. Exact raw floorsheet file or API page payloads, with retrieval timestamp, request URL/parameters, response headers, source revision and SHA-256.
2. Full pagination evidence: upstream `totalElements`, page size, page count, every page retrieved, no empty/missing pages, parsed rows equal upstream total.
3. Contract validation: unique contract IDs; exact business date; symbol and security identity; positive quantity/rate; amount = quantity × rate; valid buyer/seller member IDs.
4. Positive NMLBBL/SMPDA contract on the candidate first-trade date, if present.
5. Complete prior-session floorsheet with zero contracts for the symbol before claiming the candidate date is the first executed trade. If the prior session's completeness cannot be proved, the first-trade boundary remains UNKNOWN.
6. Reconcile contract quantity and turnover to an independent OHLCV/EOD record where available. A mismatch is retained as a conflict, not silently repaired.
7. Preserve source independence: two CSV mirrors of one upstream capture are not two independent sources.

## Current lifecycle and scanner effect

- Do not populate `valid_from` for NMLBBL or SMPDA from this audit.
- Do not change first-trade dates for any other symbol.
- Do not classify absence in a partial or unverified file as `NO_TRADE`.
- Do not promote these records into canonical floorsheet, training, backtest or broker-footprint datasets.
- Scanner Stage 1 remains fail-closed; the two symbols remain UNKNOWN/LOW CONFIDENCE for first-trade boundary evidence.
- No BUY eligibility, score, or recommendation changes.

## Next executable step

Acquire date-specific exports from the Nepse Signal interface or exact Hugging Face CSV objects through a binary-capable retrieval route. If either source supplies rows, retain the raw object and perform contract-level validation; then obtain complete prior-session evidence before changing the lifecycle boundary. If neither source yields reproducible raw records, record the source as inaccessible and continue with official exchange records and other public archives rather than inferring a no-trade day.

## Evidence references inspected

- Dataset card: https://huggingface.co/datasets/urekmazino69/Nepse-floorsheet-and-indices
- Nepse Signal floorsheet: https://nepsesignal.com/nepse/floorsheet/
- Nepse Signal methodology: https://nepsesignal.com/methodology/
- Unofficial NEPSE API client: https://github.com/basic-bgnr/NepseUnofficialApi/blob/master/nepse/NepseLib.py
- Pipeline source-behaviour note: https://ankitsanjyal.github.io/projects/nepse-pipeline.html
- Existing event ledger: `reference/nepse_security_lifecycle_events_2026-11-26.csv`
- Existing lifecycle coverage input: `data/reference/nepse_equity_lifecycle_coverage_input_2026-11-26.csv`
