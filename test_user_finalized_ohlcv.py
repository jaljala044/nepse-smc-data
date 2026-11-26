"""Regression guard for user-finalized NEPSE OHLCV project inputs.

These seven rows were explicitly finalized by the user. This test protects the
project's accepted values from accidental overwrite; it does not claim that
those values have been independently verified against NEPSE exchange records.
"""
from __future__ import annotations

import csv
import unittest
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OHLCV_DIR = ROOT / "03_stock_charts_ohlcv"

# Controlling evidence: SEVEN_STOCK_SHAREHUB_EVIDENCE_AUDIT_2026-11-19_AND_2025-07-28.md
# Issue #4 comments 7183852195 and 7183897894 supersede earlier BGWT/HRL values.
# (symbol, session_date): (open, high, low, close, volume)
USER_FINALIZED = {
    ("BGWT", "2025-07-28"): ("940.00", "992.00", "933.40", "957.17", "14028"),
    ("MEHL", "2025-07-28"): ("471.10", "480.50", "460.00", "475.63", "29753"),
    ("RAWA", "2025-07-28"): ("796.00", "811.00", "780.30", "796.90", "3165"),
    ("RHGCL", "2025-07-28"): ("346.70", "362.00", "341.40", "357.05", "296715"),
    ("ULHC", "2025-07-28"): ("509.00", "515.00", "495.00", "510.75", "32288"),
    ("API", "2026-11-19"): ("331.00", "334.20", "330.00", "331.80", "105340"),
    ("HRL", "2026-11-19"): ("483.00", "488.00", "480.00", "483.90", "49184"),
}


class UserFinalizedOhlcvRegressionTests(unittest.TestCase):
    def test_user_finalized_rows_are_present_once_and_unchanged(self):
        for (symbol, session_date), expected in USER_FINALIZED.items():
            with self.subTest(symbol=symbol, session_date=session_date):
                path = OHLCV_DIR / f"{symbol}_OHLCV.csv"
                self.assertTrue(path.is_file(), f"missing OHLCV file: {path.name}")

                with path.open(newline="", encoding="utf-8-sig") as handle:
                    reader = csv.DictReader(handle)
                    self.assertEqual(
                        reader.fieldnames,
                        ["Date", "Open", "High", "Low", "Close", "Volume"],
                    )
                    matches = [
                        row for row in reader
                        if row.get("Date", "").strip() == session_date
                    ]

                self.assertEqual(
                    len(matches), 1,
                    f"{symbol} {session_date} must occur exactly once",
                )
                row = matches[0]
                actual = tuple(
                    Decimal(row[field])
                    for field in ("Open", "High", "Low", "Close", "Volume")
                )
                expected_decimal = tuple(Decimal(value) for value in expected)
                self.assertEqual(actual, expected_decimal)

    def test_expected_scope_contains_seven_user_finalized_records(self):
        self.assertEqual(len(USER_FINALIZED), 7)
        self.assertEqual(
            {symbol for symbol, _ in USER_FINALIZED},
            {"API", "BGWT", "HRL", "MEHL", "RAWA", "RHGCL", "ULHC"},
        )


if __name__ == "__main__":
    unittest.main()
