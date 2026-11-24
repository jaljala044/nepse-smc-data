"""Fail-closed daily floorsheet collector.

A partial pagination run is never written to the canonical floorsheet directory.
The source page is scraped until the Next control is explicitly disabled, or a
short final page is observed with no Next control. Ambiguous pagination fails.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

import pandas as pd
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

URL = "https://chukul.com/floorsheet"
MAX_PAGES = 200
PAGE_SIZE = 500
NAVIGATION_TIMEOUT_MS = 45_000
PAGE_CHANGE_TIMEOUT_MS = 12_000
CLICK_ATTEMPTS = 3


def normalize_date_str(year_str: str, month_str: str, day_str: str) -> str | None:
    try:
        dt = datetime.date(int(year_str), int(month_str), int(day_str))
        if 2000 <= dt.year <= 2100:
            return dt.strftime("%Y-%m-%d")
    except ValueError:
        return None
    return None


def extract_trading_date(page_text: str, rows: list[list[str]], fallback_date: str) -> str:
    combined = page_text + "\n" + " ".join(str(cell) for row in rows for cell in row)
    match = re.search(r"\b(20\d{2})[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])\b", combined)
    if match:
        y, m, d = match.groups()
        value = normalize_date_str(y, m, d)
        if value:
            return value
    match = re.search(r"\b(0[1-9]|[12]\d|3[01])[-/](0[1-9]|1[0-2])[-/](20\d{2})\b", combined)
    if match:
        d, m, y = match.groups()
        value = normalize_date_str(y, m, d)
        if value:
            return value
    for row in rows:
        if row:
            contract = str(row[0]).strip()
            match = re.match(r"^(20\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d*$", contract)
            if match:
                value = normalize_date_str(*match.groups())
                if value:
                    return value
    return fallback_date


def row_signature(row: list[str]) -> tuple[str, ...]:
    return tuple(re.sub(r"\s+", " ", str(value)).strip() for value in row)


def scrape_complete_pages() -> tuple[list[list[str]], str, int]:
    all_rows: list[list[str]] = []
    seen_contracts: set[str] = set()
    page_count = 0
    page_text = ""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(URL, wait_until="domcontentloaded", timeout=NAVIGATION_TIMEOUT_MS)
            page.wait_for_selector("table tbody tr", timeout=NAVIGATION_TIMEOUT_MS)
            page_text = page.locator("body").inner_text(timeout=10_000)

            while page_count < MAX_PAGES:
                rows = page.eval_on_selector_all(
                    "table tbody tr",
                    """els => els.map(tr =>
                        Array.from(tr.querySelectorAll('td')).map(td =>
                            td.innerText.replace(/\s+/g, ' ').trim()
                        )
                    ).filter(r => r.length > 0)""",
                )
                if not rows:
                    raise RuntimeError(f"empty table on page {page_count + 1}")

                page_count += 1
                added = 0
                for row in rows:
                    if len(row) < 7:
                        raise RuntimeError(f"row has {len(row)} columns; expected at least 7")
                    contract = str(row[0]).strip()
                    if not contract:
                        raise RuntimeError("row has empty contract number")
                    if contract in seen_contracts:
                        raise RuntimeError(f"duplicate contract number across pages: {contract}")
                    seen_contracts.add(contract)
                    all_rows.append(row)
                    added += 1

                print(f"Collected page {page_count}: {added} unique contracts")

                next_btn = page.locator('button[aria-label="Next page"]')
                if next_btn.count() == 0:
                    if len(rows) < PAGE_SIZE:
                        break
                    raise RuntimeError("Next-page control missing after a full page; completeness unproven")

                btn_class = str(next_btn.get_attribute("class") or "").lower()
                aria_disabled = str(next_btn.get_attribute("aria-disabled") or "").lower()
                if next_btn.is_disabled() or aria_disabled == "true" or "disabled" in btn_class:
                    break

                if page_count >= MAX_PAGES:
                    raise RuntimeError(f"MAX_PAGES={MAX_PAGES} reached while Next remains enabled")

                old_first = str(rows[0][0]).strip()
                advanced = False
                last_error: Exception | None = None
                for attempt in range(1, CLICK_ATTEMPTS + 1):
                    try:
                        next_btn.scroll_into_view_if_needed(timeout=5_000)
                        next_btn.click(timeout=8_000)
                        page.wait_for_function(
                            """old => {
                                const cell = document.querySelector('table tbody tr td');
                                return !!cell && cell.innerText.replace(/\s+/g, ' ').trim() !== old;
                            }""",
                            arg=old_first,
                            timeout=PAGE_CHANGE_TIMEOUT_MS,
                        )
                        advanced = True
                        break
                    except Exception as exc:
                        last_error = exc
                        # A click may have succeeded even if the wait timed out.
                        # Check the live page before retrying, otherwise a second
                        # click could skip a page and silently lose contracts.
                        try:
                            current_first = page.eval_on_selector(
                                "table tbody tr td",
                                "el => el ? el.innerText.replace(/\\s+/g, ' ').trim() : ''",
                            )
                        except Exception:
                            current_first = ""
                        if current_first and current_first != old_first:
                            advanced = True
                            break
                        print(f"Page advance attempt {attempt}/{CLICK_ATTEMPTS} failed: {exc}")
                if not advanced:
                    raise RuntimeError(
                        f"pagination did not advance after {CLICK_ATTEMPTS} attempts; "
                        "refusing to publish partial snapshot"
                    ) from last_error
        finally:
            browser.close()

    if not all_rows:
        raise RuntimeError("no floorsheet rows collected")
    return all_rows, page_text, page_count


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def main() -> None:
    rows, page_text, page_count = scrape_complete_pages()
    base_headers = ["Contract_No", "Symbol", "Buyer", "Seller", "Quantity", "Rate", "Amount"]
    col_count = max(len(row) for row in rows)
    headers = base_headers + [f"Extra_{i}" for i in range(1, col_count - len(base_headers) + 1)]
    normalized = [row[:col_count] + [""] * (col_count - len(row)) for row in rows]
    frame = pd.DataFrame(normalized, columns=headers)

    from nepse_session_date import effective_nepse_session_str
    session_date = extract_trading_date(page_text, normalized, effective_nepse_session_str())
    output = Path("floorsheet") / f"floorsheet_{session_date}.csv"

    # Do not silently replace an existing daily archive. Re-run comparisons must
    # be explicit and versioned by a separate reconciliation process.
    if output.exists():
        raise FileExistsError(f"{output} already exists; refusing to overwrite")

    csv_text = frame.to_csv(index=False)
    digest = hashlib.sha256(csv_text.encode("utf-8")).hexdigest()
    atomic_write(output, csv_text)
    manifest = {
        "source_url": URL,
        "session_date": session_date,
        "collected_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "page_count": page_count,
        "contract_count": len(frame),
        "unique_contract_count": int(frame["Contract_No"].nunique()),
        "sha256_csv_utf8": digest,
        "completeness": "pagination_terminal_state_observed",
        "limitations": [
            "Completeness is based on the source site's pagination controls, not an exchange-signed record count.",
            "Source publication and retrieval timestamps are not interchangeable.",
        ],
    }
    atomic_write(output.with_suffix(".manifest.json"), json.dumps(manifest, indent=2) + "\n")
    print(f"Published complete snapshot: {output} ({len(frame)} contracts, {page_count} pages)")
    print(f"SHA-256: {digest}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FATAL: floorsheet snapshot not published: {exc}", file=sys.stderr)
        sys.exit(1)
