import csv
import hashlib
import json
from decimal import Decimal
from pathlib import Path
import unittest

from nepse_reference_validation import validate_calendar_rows

ROOT = Path(__file__).resolve().parent
CALENDAR = ROOT / "reference" / "nepse_positive_open_sessions_2025-11-26_2026-11-25.csv"
CLOSURES = ROOT / "reference" / "nepse_session_calendar_2026.csv"
CAPTURE_REPORT = ROOT / "reference" / "p443_positive_open_sessions_evidence" / "capture_report.json"


class PositiveOpenSessionEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with CALENDAR.open(newline="", encoding="utf-8") as stream:
            cls.rows = list(csv.DictReader(stream))
        with CLOSURES.open(newline="", encoding="utf-8") as stream:
            cls.closures = list(csv.DictReader(stream))
        cls.report = json.loads(CAPTURE_REPORT.read_text(encoding="utf-8"))
        cls.captures = {r["symbol"]: r for r in cls.report["results"]}

    def test_228_unique_dates_and_expected_range(self):
        dates = [r["date"] for r in self.rows]
        self.assertEqual(len(dates), 228)
        self.assertEqual(len(set(dates)), 228)
        self.assertEqual(min(dates), "2025-11-26")
        self.assertEqual(max(dates), "2026-11-25")

    def test_all_rows_have_valid_verified_open_provenance(self):
        self.assertEqual(validate_calendar_rows(self.rows), [])
        for row in self.rows:
            with self.subTest(date=row["date"]):
                self.assertEqual(row["status"], "verified_open")
                self.assertEqual(row["source_id"], "NEPSE_OFFICIAL_EOD_SECURITY_HISTORY_P437")
                self.assertEqual(row["scope"], "equity_session_positive_trade")
                self.assertEqual(len(row["raw_evidence_sha256"]), 64)

    def test_each_calendar_row_matches_its_pinned_official_response(self):
        response_cache = {}
        for row in self.rows:
            with self.subTest(date=row["date"], symbol=row["source_symbol"]):
                capture = self.captures[row["source_symbol"]]
                page = capture["pages"][0]
                self.assertEqual(page["url"], row["evidence_uri"])
                self.assertEqual(page["response_sha256"], row["raw_evidence_sha256"])
                self.assertEqual(str(capture["security_id"]), row["security_id"])
                expected_file = ROOT / row["source_capture_file"]
                self.assertTrue(expected_file.is_file())
                if expected_file not in response_cache:
                    raw = expected_file.read_bytes()
                    response_cache[expected_file] = (
                        hashlib.sha256(raw).hexdigest(),
                        json.loads(raw.decode("utf-8")),
                    )
                digest, payload = response_cache[expected_file]
                self.assertEqual(digest, row["raw_evidence_sha256"])
                source_row = next(
                    x for x in payload["content"]
                    if str(x["businessDate"])[:10] == row["date"]
                )
                self.assertGreater(int(source_row["totalTrades"]), 0)
                self.assertGreater(int(source_row["totalTradedQuantity"]), 0)
                self.assertEqual(Decimal(str(source_row["totalTrades"])), Decimal(row["total_trades"]))
                self.assertEqual(
                    Decimal(str(source_row["totalTradedQuantity"])),
                    Decimal(row["total_traded_quantity"]),
                )
                self.assertEqual(
                    Decimal(str(source_row["totalTradedValue"])),
                    Decimal(row["total_traded_value"]),
                )

    def test_source_witness_distribution_and_zero_trade_fallback(self):
        counts = {}
        for row in self.rows:
            counts[row["source_symbol"]] = counts.get(row["source_symbol"], 0) + 1
        self.assertEqual(counts, {"ACLBSL": 227, "AHPC": 1})
        row = next(x for x in self.rows if x["date"] == "2026-03-09")
        self.assertEqual(row["source_symbol"], "AHPC")
        self.assertEqual(row["total_trades"], "103")
        aclbsl = self.captures["ACLBSL"]
        acl_payload = json.loads(
            (ROOT / "reference" / "p443_positive_open_sessions_evidence" / "ACLBSL_page_0.json").read_text(encoding="utf-8")
        )
        acl_row = next(x for x in acl_payload["content"] if str(x["businessDate"])[:10] == "2026-03-09")
        self.assertEqual(int(acl_row["totalTrades"]), 0)

    def test_no_overlap_with_explicit_official_2026_closures(self):
        closed = {r["date"] for r in self.closures if r["status"] in {
            "verified_closed", "verified_exceptional_closed"
        }}
        opened = {r["date"] for r in self.rows}
        self.assertEqual(opened & closed, set())


if __name__ == "__main__":
    unittest.main()
