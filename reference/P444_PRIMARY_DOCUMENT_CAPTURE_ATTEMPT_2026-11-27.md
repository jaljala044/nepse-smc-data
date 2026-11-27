# P4.44 — primary-document capture attempt (2026-11-27)

## Scope and result

This pass revisited the official NEPSE-hosted PDF references already present in the 26-symbol lifecycle ledger. The NEPSE document endpoints are reachable through the web document renderer, and two documents yielded readable text. The original PDF bytes could not be downloaded into the working environment during this pass. Therefore this is a source-inspection log, **not** a provenance-complete evidence capture.

No ledger rows were promoted or rewritten. All 26 symbols remain HOLD_UNKNOWN. No stable historical security ID, first/last executed trade date, or effective validity interval is established by this pass.

## Readable primary-source observations

1. **JALPA / KLBSL — NEPSE-hosted issuer merger notice**
   - URL: https://www.nepalstock.com/api/nots/security/fetchFiles?fileLocation=klbsl_user%2F2024-06-24%2FJoint+Transaction+Notice-merged_1719213283816.pdf
   - The rendered 2-page PDF identifies Kisan Laghubitta and Jalpa Samudayik Laghubitta and describes their merger into Matribhumi Laghubitta.
   - The readable notice text states integrated business operations from BS 2081-03-27 (2024-07-11), and that both institutions' banking transactions were closed on BS 2081-03-26 for data migration.
   - This supports the merger/successor relationship and the stated joint-operation date. It does **not** establish the predecessor's last executed trade, historical stable ID, or an exchange-certified validity interval.

2. **MKLB / MMFDB / SABSL / SDLBSL — NEPSE-hosted ticker/company list**
   - URL: https://www.nepalstock.com/api/nots/news/notice/fetchFiles/df221a2bedf0c416585b019c459f17fb.pdf
   - The rendered 4-page NEPSE PDF contains a company-name/ticker table. Readable entries associate MKLB with Manakamana Smart Laghubitta, MMFDB with Mirmire Laghubitta, SABSL with Sabaiko Laghubitta, and SDLBSL with Sadhana Laghubitta.
   - This is ticker/name corroboration at the document's date, not a historical stable-ID register or lifecycle boundary.

3. **NICAD8283, NICGF and SBLD2082 — signed cancellation-document endpoints**
   - NICAD8283: https://www.nepalstock.com/api/nots/security/fetchFiles?fileLocation=rita_listing%2F2025-09-18%2FNICAD8283_1758189461940.pdf
   - NICGF: https://www.nepalstock.com/api/nots/security/fetchFiles?fileLocation=rita_listing%2F2025-03-09%2FNICGF_1741513160809.pdf
   - SBLD2082: https://www.nepalstock.com/api/nots/security/fetchFiles?fileLocation=rita_listing%2F2026-01-08%2FSBLD2082_1767865294859.pdf
   - These official endpoints resolve as one-page PDFs in the renderer, but no extractable text was returned in this pass. Existing visual-review statements in the prior reconciliation remain leads; this pass did not independently recover the original bytes or hashes.

4. **SABSL / SDLBSL merger notice**
   - URL: https://nepalstock.com/api/nots/application/fetchFiles?encryptedId=9ca7219ecb5528b642fc495f3e0c0da70f1020bdfa9281b5f72ad4be333c6939dc685ea7a65f901247228853ff475dd77a074bb6c1c743913c2feb997fb2b239
   - The endpoint resolves to a 2-page PDF but yielded no readable text in this pass. The pre-existing 2024-07-14 versus 2025-07-14 conflict remains unresolved.

## Capture/provenance limitation

- Direct binary download attempts for the NEPSE PDF endpoints failed in this execution environment.
- The document renderer exposes parsed text for the first two sources but does not provide the original byte stream, exact byte length, HTTP response headers, retrieval timestamp, or SHA-256.
- A rendered-text observation must not be substituted for a raw PDF payload or its cryptographic digest.
- No raw document was added to the repository, and no fabricated hash, retrieval timestamp, or Git blob SHA was entered.

## Five-workstream checkpoint

| Workstream | Current result | Disposition |
|---|---|---|
| 1. Primary lifecycle documents | Two NEPSE-hosted PDFs yielded readable text; three cancellation PDFs and the SABSL/SDLBSL PDF did not yield readable text; raw byte capture failed | **Partial; provenance incomplete** |
| 2. Resolve 26 historical identities | Existing ledger has 26 HOLD_UNKNOWN rows; historical stable IDs remain 0/26 | **Blocked on archived effective-dated security master / raw primary records** |
| 3. Expand execution evidence | Existing 23,377-pair matrix remains 21,082 current-snapshot-only, 2,295 unresolved, 0 historical IDs; market-wide session totals are not per-security execution proof | **No pair adjudication** |
| 4. Resolve March 1/2 lineage | Existing session crosswalk retains 13 current-side March 1 baseline conflicts; no authoritative date/completeness proof added here | **Unresolved** |
| 5. Canonical-ingestion quarantine | Existing publication code checks the historical quarantine overlay and equity exception registers, but does not consume the P4.44 lifecycle ledger or repeated-pair matrix as a symbol/date hold source | **Coverage gap identified; do not claim P4.44 identity holds are enforced by this gate** |

## Next required action

Obtain the original NEPSE PDF bytes through a source-capable retrieval path, record UTC retrieval metadata and SHA-256, commit raw files without modification, and then update only the matching ledger rows with verified document references. Separately, design and test an explicit lifecycle-identity hold interface before claiming that unresolved P4.44 identities are blocked from canonical ingestion.

No OHLCV, floorsheet, canonical, or session data was modified. No date correction, deduplication, alias assignment, stable-ID assignment, or promotion was performed.
