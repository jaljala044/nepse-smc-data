# NEPSE official holiday API capture audit — 2015–2025

Date: 2026-11-27  
Source repository: `jaljala044/nepse-elite-ai-scanner-pro`  
Capture root: `data/evidence/raw/nepse/holiday-api-authenticated/`  
Source: `NEPSE_OFFICIAL_HOLIDAY_API`  
Endpoint pattern: `https://nepalstock.com.np/api/nots/holiday/list?year={year}`

## Scope and result

Read-only inspection of the pinned GitHub tree found one authenticated raw-response capture for each requested year 2015 through 2025. Each capture includes `response-body.bin`, `parsed-response.json`, `response-headers.json`, `source-url.txt`, `capture-report.json`, and `SHA256SUMS`.

- Requested years present: **11/11 (2015–2025)**.
- HTTP status in each capture report: **200**.
- Raw response preservation flag: **true** for every year.
- Request errors: **none** in the capture reports.
- Total parsed records: **458**.
- Distinct holidayDate values: **457**.
- Duplicate-date group: one, in 2020 (2020-04-13), with two separate descriptions.
- All 458 records have null `id`, `instrumentTypeId`, and `activeStatus`; those fields cannot be used as stable holiday-row identity, instrument scope, or active/inactive filter.

## Per-year inventory

| Requested year | Parsed records | Unique dates | Raw response SHA-256 |
|---:|---:|---:|---|
| 2015 | 54 | 54 | `a7a88f019ddff9d689d537648c5158fcee51adb159abf91ac52b6c76f480f100` |
| 2016 | 33 | 33 | `40679b6516ad2ad97e9fb55efd4dfb01e34b060e6355bddf6d99e68edc45b1d0` |
| 2017 | 38 | 38 | `40e4d12e0e821e5c36be6f14224b7e870cd15eb153127071c8df10494fc4c504` |
| 2018 | 29 | 29 | `8ec39101709349dfad051e884d0c4edfc14a3310fca52ae21abdc41c2af87cbd` |
| 2019 | 22 | 22 | `9e5094599dc5703456ed5022141b9f3453820a6c5da9b1620db25b153fe7101c` |
| 2020 | 101 | 100 | `4a98b87e9e7703c5661fdeac44fef23e1b050a6fa23d843c6509f5140a1e7e89` |
| 2021 | 25 | 25 | `e68f6cc14d932a66e4f6bf53866a7d6d7e1744001a0a5e679ca3200870558a7a` |
| 2022 | 36 | 36 | `831ec883905e1c8583638bc52e6f2c0c2bb16c934b0c802fed1c0d7e3a703f01` |
| 2023 | 37 | 37 | `5c8add8566704d1695d421a4e9a7fc0e638afd50085d6941130fc184461a15dd` |
| 2024 | 37 | 37 | `11fedf2985caa3a27d82b7eb282981df3e28de9eae29080012f1b2c6cb545926` |
| 2025 | 46 | 46 | `9a830365d29f4789a8a929f27fcf64e52d1beec9910a118a598074401c04c685` |
| **Total** | **458** | **457** | — |

The listed SHA-256 values are the values recorded consistently in each capture report and its `SHA256SUMS` entry. This inspection compared the metadata records; it did not independently recompute hashes from downloaded raw response bytes.

## Duplicate-date review

2020-04-13 appears twice:
- `As Per Order by SEBON Lockdown`
- `New Year Holiday`

Both records have null `id`, `instrumentTypeId`, and `activeStatus`. Preserve both descriptions as distinct source records. Do not deduplicate solely by date. For a date-level closure calendar, retain a one-date key with both source descriptions and both source-row references.

No other duplicate `holidayDate` value was found in the 2015–2025 captures.

## What this establishes

- Byte-preserved, exchange-hosted holiday API responses are available for every requested year 2015–2025 in the companion repository.
- The captured endpoint returned 458 holiday records with 457 unique date values.
- The source's own fields are insufficient to infer instrument class or status from the null metadata columns.

## What this does not establish

- These records are holiday-list entries, not a complete record of every market closure or emergency suspension.
- A date absent from the holiday list is **not** proof of an open trading session.
- The API response does not encode stable record IDs or instrument-type scope in these captures.
- The audit does not verify weekly schedule rules, exceptional suspensions, or per-security execution.
- The audit does not establish positive-open dates or a complete expected-session denominator.
- No dates are promoted into the verified-open calendar by this report.

## Disposition

**COMPLETE — 2015–2025 raw holiday-capture inventory and duplicate-date audit.**  
**NOT COMPLETE — historical exchange-session calendar.** Closure-list evidence is now available for the 11 captured years, but positive-open evidence, schedule transitions, and exceptional closures require separate primary evidence.

No raw captures, parsed source files, canonical calendar rows, OHLCV files, lifecycle records, or scanner inputs were modified.
