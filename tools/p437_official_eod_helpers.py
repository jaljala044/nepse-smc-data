"""Pure helpers for P4.37 official NEPSE today-price evidence summaries."""
def summarize_pages(page_payloads, symbol, business_date, upstream_total_elements=None):
    symbol = symbol.strip().upper()
    all_rows = []
    for payload in page_payloads:
        content = payload.get("content") if isinstance(payload, dict) else None
        if isinstance(content, list):
            all_rows.extend(row for row in content if isinstance(row, dict))
    returned_dates = sorted({
        str(row.get("businessDate", ""))[:10]
        for row in all_rows if row.get("businessDate") is not None
    })
    symbol_rows = [
        row for row in all_rows
        if str(row.get("symbol", "")).strip().upper() == symbol
    ]
    matching_rows = [
        row for row in symbol_rows
        if str(row.get("businessDate", ""))[:10] == business_date
    ]
    if len(matching_rows) == 1:
        status = "TARGET_ROW_FOUND"
    elif len(matching_rows) == 0:
        status = "TARGET_ROW_MISSING"
    else:
        status = "TARGET_ROW_NOT_UNIQUE"
    captured_rows = len(all_rows)
    pagination_matches = (
        isinstance(upstream_total_elements, int)
        and captured_rows == upstream_total_elements
    )
    return {
        "status": status,
        "symbol": symbol,
        "business_date": business_date,
        "returned_business_dates": returned_dates,
        "symbol_row_count": len(symbol_rows),
        "target_row_count": len(matching_rows),
        "target_row": matching_rows[0] if len(matching_rows) == 1 else None,
        "captured_rows": captured_rows,
        "upstream_total_elements": upstream_total_elements,
        "pagination_row_count_matches": pagination_matches,
        "raw_archive_mutated": False,
    }
