import argparse
from pathlib import Path
from scanner_inputs.canonical_publication import publish_daily_floorsheet
from scanner_inputs.historical_quarantine import load_holds
import datetime
import os
import re
import sys
import time
import pandas as pd
from playwright.sync_api import sync_playwright


def normalize_date_str(year_str: str, month_str: str, day_str: str) -> str | None:
    try:
        dt = datetime.date(int(year_str), int(month_str), int(day_str))
        if 2000 <= dt.year <= 2100:
            return dt.strftime("%Y-%m-%d")
    except ValueError:
        return None
    return None


def extract_trading_date(page_text: str, cleaned_rows: list[list[str]], fallback_date: str) -> str:
    combined = page_text + "\n" + " ".join(str(cell) for row in cleaned_rows for cell in row)

    match_ymd = re.search(r"\b(20\d{2})[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])\b", combined)
    if match_ymd:
        y, m, d = match_ymd.groups()
        valid = normalize_date_str(y, m, d)
        if valid:
            return valid

    match_dmy = re.search(r"\b(0[1-9]|[12]\d|3[01])[-/](0[1-9]|1[0-2])[-/](20\d{2})\b", combined)
    if match_dmy:
        d, m, y = match_dmy.groups()
        valid = normalize_date_str(y, m, d)
        if valid:
            return valid

    for row in cleaned_rows:
        if not row:
            continue
        contract_no = str(row[0]).strip()
        match_contract = re.match(r"^(20\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d*$", contract_no)
        if match_contract:
            y, m, d = match_contract.groups()
            valid = normalize_date_str(y, m, d)
            if valid:
                return valid

    return fallback_date


def fetch_floorsheet(overlay, controls):
    load_holds(overlay)  # Fail before network collection if evidence is unavailable.
    reached_end = False
    all_rows = []
    max_pages = 200
    page_text = ""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Navigating to Chukul floorsheet...")
        page.goto("https://chukul.com/floorsheet", wait_until="domcontentloaded")

        try:
            page.wait_for_selector("table tbody tr", timeout=35000)
            time.sleep(2)
            page_text = page.evaluate("() => document.body ? document.body.innerText : ''")
        except Exception as e:
            print(f"Timed out waiting for table: {e}")
            browser.close()
            sys.exit(1)

        last_seen_first_row = ""
        page_count = 0

        while page_count < max_pages:
            rows = page.eval_on_selector_all(
                "table tbody tr",
                """els => els.map(tr =>
                    Array.from(tr.querySelectorAll('td')).map(td => td.innerText.replace(/\\s+/g, ' ').trim())
                ).filter(r => r.length > 0)""",
            )

            if not rows:
                break

            cur_first_row = rows[0][0]
            if page_count > 0 and cur_first_row == last_seen_first_row:
                break

            all_rows.extend(rows)
            page_count += 1
            last_seen_first_row = cur_first_row
            print(f"Scraped Page {page_count} ({len(rows)} rows)")

            next_btn = page.locator('button[aria-label="Next page"]')
            if next_btn.count() == 0:
                break

            btn_class = str(next_btn.get_attribute("class") or "").lower()
            aria_disabled = str(next_btn.get_attribute("aria-disabled") or "").lower()
            if next_btn.is_disabled() or aria_disabled == "true" or "disabled" in btn_class:
                reached_end = True
                print("Reached last page (Next button disabled).")
                break

            next_btn.scroll_into_view_if_needed()
            next_btn.click()

            changed = False
            for _ in range(16):
                time.sleep(0.5)
                new_first_row = page.eval_on_selector(
                    "table tbody tr td",
                    "el => el ? el.innerText.replace(/\\s+/g, ' ').trim() : ''",
                )
                if new_first_row and new_first_row != last_seen_first_row:
                    changed = True
                    break

            if not changed:
                print("Page did not update before timeout; stopping pagination.")
                break

        browser.close()

    if not reached_end:
        raise ValueError("Pagination completeness not established; archive withheld")
    if not all_rows:
        print("No floorsheet rows collected.")
        sys.exit(1)

    col_count = max(len(r) for r in all_rows)
    base_headers = ["Contract_No", "Symbol", "Buyer", "Seller", "Quantity", "Rate", "Amount"]
    if col_count <= len(base_headers):
        headers = base_headers[:col_count]
    else:
        headers = base_headers + [f"Extra_{i}" for i in range(1, col_count - len(base_headers) + 1)]

    cleaned_rows = [r[:col_count] + [""] * (col_count - len(r)) for r in all_rows]
    df = pd.DataFrame(cleaned_rows, columns=headers)

    from nepse_session_date import effective_nepse_session_str
    fallback_date = effective_nepse_session_str()
    file_date = extract_trading_date(page_text, cleaned_rows, fallback_date)

    os.makedirs("floorsheet", exist_ok=True)
    filepath = f"floorsheet/floorsheet_{file_date}.csv"
    raw = df.to_csv(index=False).encode("utf-8")
    controls = Path(controls)
    result = publish_daily_floorsheet(raw, file_date, Path(filepath), overlay,
                                     control_path=controls / f'{file_date}.json',
                                     evidence_path=controls / f'{file_date}.evidence.json')
    print(f"{result}: {len(cleaned_rows)} rows at {filepath}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--quarantine-overlay', type=Path, required=True)
    parser.add_argument('--session-controls', type=Path, required=True)
    args = parser.parse_args()
    fetch_floorsheet(args.quarantine_overlay, args.session_controls)
