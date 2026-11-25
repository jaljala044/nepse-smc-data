# Five-stock source reconciliation — 2025-07-28

**Scope:** BGWT, MEHL, RAWA, RHGCL, ULHC  
**Purpose:** Record visible-page historical evidence gathered for the five disputed daily records.  
**Important:** This report keeps user-finalized chart OHLC values separate from independent source observations. It does not silently replace one series with another.

## 1. Floorsheet evidence — Merolagani visible UI

Source page: https://merolagani.com/Floorsheet.aspx  
Method: Entered each exact symbol and date 07/28/2025 in the visible Symbol and Date filters and searched. Values below are the filtered per-symbol summaries shown by the page, not the unfiltered market totals.

| Symbol | Matching rows / pages | Quantity shown | Turnover shown (Rs.) | Average rate shown |
|---|---:|---:|---:|---:|
| BGWT | 194 rows / 1 page | 14,028 | 13,256,345.00 | 944.99 |
| MEHL | 333 rows / 1 page | 29,753 | 14,008,898.10 | 470.84 |
| RAWA | 74 rows / 1 page | 3,165 | 2,515,662.50 | 794.84 |
| RHGCL | 3 pages; 500 rows on page 1 | 296,715 | 103,872,614.40 | 350.08 |
| ULHC | 300 rows / 1 page | 32,288 | 16,273,342.10 | 504.01 |

For RHGCL, the page displayed the aggregate quantity, turnover, and average rate for all three pages. Only page 1 transaction rows were extracted during this run; the page-level aggregate summary was read as the all-pages total. Do not interpret 500 as the total RHGCL transaction count.

### Comparison with user-finalized floorsheet aggregates

| Symbol | User quantity | UI quantity | Qty match | User turnover (Rs., whole rupee) | UI turnover (Rs.) | Difference |
|---|---:|---:|---|---:|---:|---:|
| BGWT | 14,028 | 14,028 | Yes | 13,256,345 | 13,256,345.00 | 0.00 |
| MEHL | 29,753 | 29,753 | Yes | 14,008,898 | 14,008,898.10 | +0.10 |
| RAWA | 3,165 | 3,165 | Yes | 2,515,663 | 2,515,662.50 | -0.50 |
| RHGCL | 296,715 | 296,715 | Yes | 103,872,614 | 103,872,614.40 | +0.40 |
| ULHC | 32,288 | 32,288 | Yes | 16,273,342 | 16,273,342.10 | +0.10 |

**Finding:** All five user-supplied quantities match the filtered Merolagani UI summaries exactly. Turnover matches the user-supplied whole-rupee values after ordinary display rounding; maximum absolute difference is Rs. 0.50. The average rates shown by the site agree with the user's calculated VWAP values to two decimals.

**Source limitation:** Merolagani is a third-party market-data portal, not the Nepal Stock Exchange itself. This is independently observed floorsheet evidence from its visible UI, not a byte-for-byte official NEPSE raw capture. Chukul's visible floorsheet page was inspected but did not show a filtered aggregate total in the visible UI; individual rows were paginated. The Chukul historical chart OHLC task was not completed in that run.

## 2. Historical OHLC evidence — Nepse Alpha visible UI

Source page: https://nepsealpha.com/nepse-data/  
Method: Daily mode, Specific Date = 2025-07-28, Price Type = Unadjusted. The UI returned 338 rows for the date; the five requested symbols were found in the result table.

| Symbol | Date | Open | High | Low | Close | Site % change | Site volume |
|---|---|---:|---:|---:|---:|---:|---:|
| BGWT | 2025-07-28 | 940.00 | 992.00 | 933.40 | 957.17 | +0.84% | 14,028 |
| MEHL | 2025-07-28 | 471.10 | 480.50 | 460.00 | 475.63 | -1.05% | 29,753 |
| RAWA | 2025-07-28 | 796.00 | 811.00 | 780.30 | 796.90 | -1.64% | 3,165 |
| RHGCL | 2025-07-28 | 346.70 | 362.00 | 341.40 | 357.05 | +5.03% | 296,715 |
| ULHC | 2025-07-28 | 345.00 | 345.00 | 335.00 | 345.00 | +2.37% | 45,475 |

This is a third-party historical-price UI result, not official NEPSE evidence. The page was explicitly set to Unadjusted. It conflicts with the user-finalized chart values for BGWT and ULHC; it also reports a different volume for ULHC. Do not overwrite the user-finalized values based on this one third-party source.

## 3. User-finalized chart OHLC retained separately

The following values were explicitly supplied and finalized by the user for the project:

| Symbol | Open | High | Low | Close |
|---|---:|---:|---:|---:|
| BGWT | 824.56 | 870.18 | 818.77 | 839.62 |
| MEHL | 471.10 | 480.50 | 460.00 | 475.63 |
| RAWA | 796.00 | 811.00 | 780.30 | 796.90 |
| RHGCL | 346.70 | 362.00 | 341.40 | 357.05 |
| ULHC | 509.00 | 515.00 | 495.00 | 510.75 |

### Interpretation and unresolved source conflicts

- **MEHL, RAWA, RHGCL:** Nepse Alpha OHLC matches the user-finalized OHLC exactly. MEHL's displayed percentage change differs slightly (-1.05% vs the user's -1.08%); this does not change the matching OHLC.
- **BGWT:** Nepse Alpha's unadjusted OHLC is materially higher than the user-finalized chart OHLC. The Merolagani floorsheet average rate is Rs. 944.99 and visible sample trades are in the Rs. 925–992 range, which is consistent with the unadjusted Nepse Alpha price range, not the user-finalized chart range. This suggests a possible adjusted-vs-unadjusted chart basis difference, but the adjustment factor and chart mode have not been independently established. Preserve both series with their source/basis labels.
- **ULHC:** Nepse Alpha reports OHLC 345/345/335/345 and volume 45,475, while the Merolagani floorsheet reports quantity 32,288, average rate Rs. 504.01, and transaction rates around Rs. 495–514. The floorsheet evidence supports the user's 509/515/495/510.75 price region and conflicts with the Nepse Alpha row. Treat Nepse Alpha's ULHC row as a source conflict, not as a replacement.
- The user-finalized OHLC values remain authoritative project inputs. This report adds independent source observations; it does not revoke the user's finalization.

## 4. Validation status

| Component | Result |
|---|---|
| Floorsheet quantity, five symbols | Independently matched in Merolagani visible UI |
| Floorsheet turnover, five symbols | Matched to whole-rupee user totals within Rs. 0.50 |
| OHLC, MEHL / RAWA / RHGCL | Matches Nepse Alpha unadjusted UI |
| OHLC, BGWT | Conflicting price basis; preserve user-finalized series and unadjusted third-party series separately |
| OHLC, ULHC | Nepse Alpha row conflicts with floorsheet prices and user-finalized series; do not replace |
| Chukul chart screenshots / historical OHLC | Not yet captured |
| ShareSansar / Punji cross-check | Not yet completed |
| Official NEPSE historical OHLC confirmation | Not yet obtained |

## 5. Decision

The five floorsheet quantity/turnover records can be marked reconciled against the Merolagani visible UI totals, subject to the third-party-source limitation and sub-rupee display rounding. The five user-finalized OHLC inputs should remain unchanged in the canonical project dataset. BGWT and ULHC must retain explicit source-conflict annotations until the chart adjustment basis (BGWT) and the ULHC discrepancy are resolved with a stronger source such as the original chart evidence or official NEPSE records.

**Do not close the broader NEPSE reference-validation Issue #4 on the basis of this five-stock audit.** That issue also requires the historical session calendar and effective-dated instrument-master evidence described in its acceptance criteria.
