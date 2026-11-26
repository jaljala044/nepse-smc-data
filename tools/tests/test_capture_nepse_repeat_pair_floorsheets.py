import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from capture_nepse_repeat_pair_floorsheets import page_parts, repeat_pairs


class RepeatPairFloorsheetCaptureTests(unittest.TestCase):
    def test_extracts_both_dates_for_each_open_repeat(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "repeats.csv"
            with path.open("w", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=[
                    "symbol", "previous_date", "date", "classification"
                ])
                writer.writeheader()
                writer.writerows([
                    {"symbol":"BNL","previous_date":"2026-11-13","date":"2026-11-17","classification":"OPEN_SESSION_REPEAT_REVIEW"},
                    {"symbol":"BNT","previous_date":"2026-06-29","date":"2026-07-01","classification":"OPEN_SESSION_REPEAT_REVIEW"},
                    {"symbol":"ENL","previous_date":"2026-08-25","date":"2026-08-26","classification":"OPEN_SESSION_REPEAT_REVIEW"},
                    {"symbol":"UNL","previous_date":"2026-08-24","date":"2026-08-27","classification":"OPEN_SESSION_REPEAT_REVIEW"},
                    {"symbol":"UNL","previous_date":"2026-09-28","date":"2026-09-29","classification":"OPEN_SESSION_REPEAT_REVIEW"},
                    {"symbol":"TEST","previous_date":"2026-01-01","date":"2026-01-02","classification":"CLOSED_SESSION_REPEAT_CANDIDATE"},
                ])
            pairs = repeat_pairs(path)
            self.assertEqual(len(pairs), 10)
            self.assertIn(("UNL", "2026-08-27"), pairs)
            self.assertNotIn(("TEST", "2026-01-02"), pairs)

    def test_parses_complete_and_empty_floorsheet_payloads(self):
        rows, pages, elements, status = page_parts({
            "floorsheets": {"content":[{"contractId":1}], "totalPages":1, "totalElements":1}
        })
        self.assertEqual((len(rows), pages, elements, status), (1, 1, 1, "OK"))
        rows, pages, elements, status = page_parts({"floorsheets":{"content":[],"totalPages":0,"totalElements":0}})
        self.assertEqual((rows, pages, elements, status), ([], 0, 0, "OK"))
        rows, pages, elements, status = page_parts([])
        self.assertEqual((rows, pages, elements, status), ([], 0, 0, "EMPTY_RESPONSE"))


if __name__ == "__main__":
    unittest.main()
