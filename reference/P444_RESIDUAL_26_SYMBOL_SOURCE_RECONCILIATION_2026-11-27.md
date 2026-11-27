# P4.44 — residual 26-symbol source reconciliation (next work item)

Date: 2026-11-27  
Base symbol set: P4.43 209-symbol identity triage, pinned source commit `56362fb4f65b91fdcca8f50b50e53ad80e703649`.

## Result

A second targeted source pass found additional date-specific lifecycle evidence and organized all 26 symbols absent from the 2026-11-25 current snapshot into a source-tier matrix.

- **10/26** symbols now have at least one NEPSE-hosted official notice/listing-cancellation reference in the existing evidence set: JALPA, KLBSL, MKLB, MMFDB, SABSL, SDLBSL, SAMAJ, NICAD8283, NICGF and SBLD2082.
- The first nine have references in the existing six-document NEPSE-hosted corroboration ledger. SBLD2082 is a newly located NEPSE signed listing-cancellation notice indexed by search for 2082-09-24 (2026-01-08), after trading hours.
- **16/26** still lack a directly captured NEPSE primary identity/lifecycle record in this matrix.
- Secondary sources provide additional date/name leads for maturity and delisting events (including HBLD83, NICAD8182, NICD83/84, NMB50, SRD80, SBLD83 and mutual funds) and merger dates (including SFCL). These do not substitute for an exchange-signed record.
- **Historical stable security IDs verified: 0/26.** The official ticker list and notices establish names/successor relationships but do not expose the old stable IDs or complete validity intervals.
- All 26 remain HOLD/UNKNOWN for historical identity boundary purposes.

## Newly located primary record

NEPSE signed cancellation notice for SBLD2082:
https://www.nepalstock.com/api/nots/security/fetchFiles?fileLocation=rita_listing%2F2026-01-08%2FSBLD2082_1767865294859.pdf

The indexed notice identifies 10.50% SBL Debenture 2082 and says listing cancellation is effective after trading on 2082-09-24 (2026-01-08). The raw PDF bytes and SHA-256 were not captured into the repository during this pass, so it is a primary-source lead, not yet a fully provenance-complete evidence record.

## Important date conflict retained

The NEPSE-hosted SABSL/SDLBSL issuer notice prints 2082-03-30 (2025-07-14), while the existing Priority97 record and secondary merger chronology indicate 2024-07-14. This is not resolved by the present source pass. Keep both claims and do not choose a trading boundary.

## Source limitations

- A maturity date, merger joint-operation date, listing cancellation date, and last executed trade date are different facts. They must not be substituted for one another.
- A signed cancellation letter may say "after trading" on a date; that does not prove the last execution occurred on that date for every security row.
- Secondary company pages, media reports and market-data pages are discovery/corroboration only.
- Search-indexed official PDFs without raw bytes and a pinned hash do not meet the P4.44 provenance acceptance criterion.
- No historical stable ID, full lifecycle interval, or row-level OHLCV boundary is promoted.

## Disposition

The 26-symbol discovery and source-tier reconciliation is advanced, but **not resolved**. All 26 remain HOLD/UNKNOWN. No OHLCV dates or values changed. No canonical promotion, deletion, deduplication or date shifting.

Next: capture the original SBLD2082 NEPSE PDF bytes and SHA-256; acquire direct NEPSE notices for the remaining 16; obtain effective-dated historical security IDs from archived official security lists; then build the date-keyed join for the 23,377 repeat pairs.
