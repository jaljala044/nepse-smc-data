# P4.37 — Cross-sector official EOD parity and ShareSansar date-contamination audit

**Audit date:** 2026-11-26  
**Capture:** 2026-11-26T19:59:11.080336Z  
**Sample:** 24 active securities, 12 sectors, two securities per sector  
**Window:** 2025-11-26 through 2026-11-26  
**CI run:** https://github.com/jaljala044/nepse-smc-data/actions/runs/45887648109

## Executive finding

The cross-sector sample confirms that the canonical OHLCV files contain stale carry-forward rows on dates that the canonical session calendar verifies as closed. The affected rows reproduce an exact High/Low/Close/Volume tuple from another official NEPSE EOD date.

- 24/24 security IDs matched the official security master and were active.
- 24/24 official EOD requests returned complete, single-page histories.
- Every security returned the same 228 official date keys; 5,472 rows were preserved.
- 1,455 canonical-only rows across 19 securities exactly match an official HLCV tuple on a different date.
- Those 1,455 rows fall on 81 unique dates, all `verified_closed`: 60 regular weekly closure dates and 21 listed-holiday dates.
- 36 official-only rows also match canonical tuples placed on other verified-closed dates.
- Three exact-date HLCV mismatches remain unresolved.
- No canonical OHLCV file was modified.

This is a confirmed closed-date carry-forward contamination pattern in the ShareSansar-derived import, not a set of additional NEPSE trading sessions.

## Official NEPSE sample coverage

| Sector | Symbols | Official rows | Canonical closed-date carry-forward rows | Exact-date HLCV mismatches |
|---|---|---:|---:|---:|
| Microfinance | ACLBSL, NUBL | 456 | 162 | 0 |
| Commercial Banks | NABIL, NMB | 456 | 162 | 0 |
| Hydropower | AHPC, API | 456 | 0 | 1 |
| Life Insurance | NLIC, LICN | 456 | 162 | 0 |
| Hotels and Tourism | SHL, CGH | 456 | 162 | 0 |
| Trading | STC, BBC | 456 | 162 | 0 |
| Finance | CFCL, ICFC | 456 | 160 | 1 |
| Manufacturing and Processing | HDL, NLO | 456 | 84 | 1 |
| Investment | HIDCL, NIFRA | 456 | 0 | 0 |
| Development Banks | GBBL, CORBL | 456 | 160 | 0 |
| Non-Life Insurance | NLG, NICL | 456 | 160 | 0 |
| Others | NTC, HRL | 456 | 81 | 0 |
| **Total** | **24 symbols** | **5,472** | **1,455** | **3** |

All 24 symbols share the same 228-date official history. There are 5,249 positive-trade rows and 223 zero-trade rows; 221 zero-trade rows belong to NLO, demonstrating why a daily EOD row must not automatically be interpreted as an executed trade.

All 24 evidence gates passed: complete pagination, one unique row per returned date, no missing business dates, no out-of-window dates, and complete HLCV/volume fields. The official response schema does not include Open.

## Canonical parity and quarantine results

Comparison is restricted to High, Low, Close and Volume because the official endpoint does not return Open.

| Quarantine disposition | Rows | Interpretation |
|---|---:|---|
| `CANONICAL_CLOSED_DATE_CARRY_FORWARD` | **1,455** | Canonical date is verified closed; HLCV tuple matches another official EOD date |
| `OFFICIAL_ONLY_NO_CANONICAL_TUPLE_MATCH` | 306 | Official date has no corresponding canonical row/tuple; not promoted or backfilled |
| `OFFICIAL_ONLY_MATCHES_CANONICAL_CLOSED_DATE` | 36 | Official EOD tuple appears under a different, verified-closed canonical date |
| `EXACT_DATE_HLCV_MISMATCH` | **3** | Same date but HLCV values differ |
| **Total quarantine rows** | **1,800** | Full row-level matrix committed |

### Closed-date carry-forward dates

The 1,455 canonical-only rows represent 81 distinct calendar dates repeated across the sampled securities:
- 60 dates classified by the canonical calendar as regular weekly closures.
- 21 dates classified as explicitly listed NEPSE holidays.
- 0 dates with UNKNOWN session status.

The 1,455 row-level calendar-day offsets from the matched official EOD date are:
| Offset | Rows |
|---:|---:|
| +1 day | 664 |
| +2 days | 556 |
| +3 days | 163 |
| +4 days | 54 |
| +5 days | 18 |
| **Total** | **1,455** |

The official calendar—not weekday inference alone—was used to classify closed dates. The 2026 weekly schedule transition is respected: Sunday–Thursday trading before 2026-04-06, then Monday–Friday trading from 2026-04-06. The 21 listed holidays are taken from the preserved NEPSE holiday captures.

### Three exact-date HLCV mismatches

| Symbol | Sector | Date | Canonical Close | Official Close | Official High | Official Low | Official Volume |
|---|---|---|---:|---:|---:|---:|---:|
| AHPC | Hydropower | 2026-07-17 | 271.9 | 272.0 | 274.9 | 265.3 | 77,148 |
| CFCL | Finance | 2026-11-18 | 636.00 | 589.9 | 640.0 | 589.9 | 307,576 |
| HDL | Manufacturing | 2026-07-17 | 1,163.90 | 1,163.0 | 1,163.9 | 1,148.0 | 20,089 |

These three are close-only differences; High, Low and Volume match on the same date. CFCL is material and must be separately checked against corporate actions and primary EOD evidence. No value is corrected by this audit.

## Root-cause trace: canonical source and ingestion path

### 1. Canonical files are ShareSansar-derived, not NEPSE-primary

The starter repository's import manifest records:
- Import repository: `jaljala044/nepse-history-starter`
- Import commit: `12002cdc679061192c1ea3cbd5300257286e66af`
- Manifest: `historical_imports/sharesansar_2026-11-20.json`
- Source workbook: `OmitNomis/ShareSansarScraper`, commit `d5949bd628d6b5ca9ebb2b4a15e001a434c6732c`
- Workbook path: `docs/Data/combined_excel.xlsx`
- Workbook Git blob SHA: `e200c06f47a0d529baae61680bb40a55d1114fa1`
- Workbook size: 41,946,267 bytes
- Workbook SHA-256: `dc9534bd1e38a467452196548f82a20b14a1fedc9a2e64983484d9137386c38c`
- Manifest counts: 937 archived snapshots, 525 source symbols, 303,438 source rows, 301,632 imported rows, 1,806 flagged rows.

Spot checks confirmed the current repository's ACLBSL, NMLBBL and CFCL OHLCV files are byte-for-byte identical to their `nepse-history-starter` counterparts.

### 2. Upstream scraper assigns the computer's date

In `ShareSansarDataScrape/spiders/market.py` at the pinned source commit:
- The output filename is assigned using `datetime.now().strftime('%Y_%m_%d')`.
- The scraper relies on `is_duplicate_of_latest`, which compares the entire scraped table excluding only the serial-number column.
- It does not obtain or validate an authoritative NEPSE `businessDate` before assigning the filename date.

The scraper README says it intends to skip closed days when the table is identical. The observed rows show that this guard did not prevent all stale snapshots from being archived.

### 3. Downstream builder treats every filename date as a session key

In `build_site_data.py`:
- `list_csv_dates()` extracts every valid `YYYY_MM_DD` filename from `docs/Data`.
- `read_session(date_key)` reads that file and publishes rows under the filename date.
- It does not reconcile those dates with an official NEPSE session calendar.

The source API metadata labels 937 archived snapshots as `tradingDays`; that count is not a verified count of NEPSE trading sessions.

### 4. Importer accepts calendar dates without exchange-session validation

In `nepse_history_import.py`:
- `session()` checks Gregorian `YYYY-MM-DD` syntax and supported date bounds.
- `input_date()` takes the row date or filename date and checks agreement between those two values.
- Neither function checks the date against an authoritative NEPSE open-session calendar.

This allows a scrape-date-labelled stale ShareSansar snapshot to enter the canonical OHLCV archive as if it were a trading session.

### 5. Direct source example

The upstream `docs/api/history/ACLBSL.json` contains repeated OHLCV tuples on consecutive calendar dates:
- 2024-03-07, 2024-03-08 and 2024-03-09 share the same OHLCV and volume.
- 2024-03-14, 2024-03-15 and 2024-03-16 share the same OHLCV and volume.
- Similar repeated values occur across other weekends/holidays.

This corroborates the one-year official EOD parity findings. The root cause is therefore a source-date/session-validation defect in the ShareSansar snapshot pipeline, not a NEPSE trading-session expansion.

## Committed evidence and reproducibility

- Capture script: `tools/capture_p437_closed_date_contamination_audit.py`
- Tests: `tools/tests/test_capture_p437_closed_date_contamination_audit.py`
- Workflow: `.github/workflows/p437-closed-date-contamination-audit.yml`
- Official security master: `reference/p437_cross_sector_date_contamination_audit/security_list.json`
- 24 raw official EOD response pages: `reference/p437_cross_sector_date_contamination_audit/*_page_0.json`
- Capture report: `reference/p437_cross_sector_date_contamination_audit/capture_report.json`
- Row-level quarantine matrix: `reference/p437_cross_sector_date_contamination_audit/quarantine_matrix.csv`
- CI run #45887648109 passed all regression tests, authenticated capture, parity checks and artifact commit.

## Disposition

1. Preserve all raw ShareSansar-derived OHLCV files unchanged.
2. Quarantine the 1,455 verified-closed carry-forward rows from indicator, volume, VSA, RS, backtest and training calculations in any derived dataset.
3. Keep the 36 official-to-closed-date mappings and 306 unmatched official rows visible; do not auto-correct or silently backfill.
4. Investigate AHPC, CFCL and HDL exact-date close mismatches separately.
5. Do not infer missing floorsheet contracts or first-trade dates from EOD history.

## Next priority — P4.38

Expand the same official EOD/date-calendar reconciliation to the full 281-equity universe. Produce a symbol-by-symbol impact matrix and a separate derived clean-session dataset. Keep raw OHLCV immutable, quarantine closed-date carry-forwards, and require primary evidence before resolving the three exact-date conflicts or any UNKNOWN session.
