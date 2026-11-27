# P4.43 — exact overlap: invalid OHLCV exceptions and repeated-candle findings

Pinned source commit: `56362fb4f65b91fdcca8f50b50e53ad80e703649`.

## Reconciled counts

| Measure | Count |
|---|---:|
| Invalid-OHLCV flags | 1,331 |
| Exact equity exception-register matches | 1,329 |
| Non-equity instrument exceptions | 2 |
| Consecutive identical-OHLCV pair findings | 94,543 |
| Exception rows that are endpoints of a consecutive repeat pair | 4 |
| Distinct repeat pairs with both endpoints in the exception register | **2** |
| Repeat-finding current rows also present in exception register | 2 |

## Exact overlaps

| Symbol | Prior date / row | Current date / row | Repeated OHLCV tuple | Invalid reason |
|---|---|---|---|---|
| AHPC | 2011-06-19 / 303 | 2011-06-20 / 304 | 319, 325, 325, 325, 16 | Open outside range |
| API | 2016-09-03 / 190 | 2016-09-04 / 191 | 605, 647, 617, 630, 4,512 | Open outside range |

Both endpoint rows in each pair are exact matches to the existing symbol-specific exception register. The global findings output records the repeated-pair finding on the current endpoint row and links the prior endpoint through `related_line`.

## Interpretation

These are overlapping audit findings, not four additional unique defects. Two consecutive pairs (four source rows) are already represented in the 1,329 equity exception-register matches and also appear in the 94,543 repeated-pair findings. The repeated tuple remains invalid because the Open is outside the High/Low range. The equality across adjacent dates does not establish duplicated executions, a valid candle, or a correct source price.

All four rows remain `HOLD_UNRESOLVED`. This reconciliation does not authorize correction, deletion, deduplication, date shifting, or promotion. Raw and canonical data remain unchanged.

## Reproducibility

The companion CSV `P443_INVALID_EXCEPTION_REPEAT_OVERLAP_2026-11-27.csv` records all four endpoints, pinned blob SHA, source row, exact OHLCV tuple, pair key, and global-finding location. Machine summary: `P443_INVALID_EXCEPTION_REPEAT_OVERLAP_2026-11-27.json`.
