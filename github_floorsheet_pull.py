import datetime
import os
import sys
import time
import pandas as pd
from playwright.sync_api import sync_playwright


def fetch_floorsheet():
    all_rows = []
    max_pages = 200

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Navigating to Chukul floorsheet...")
        page.goto("https://chukul.com/floorsheet", wait_until="domcontentloaded")

        try:
            page.wait_for_selector("table tbody tr", timeout=35000)
            time.sleep(2)
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

    os.makedirs("floorsheet", exist_ok=True)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    filepath = f"floorsheet/floorsheet_{today}.csv"
    df.to_csv(filepath, index=False)
    print(f"Successfully saved {len(cleaned_rows)} rows to {filepath}")


if __name__ == "__main__":
    fetch_floorsheet()
