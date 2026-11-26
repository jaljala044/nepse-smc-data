import json
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import validate_nepse_eod_capture as M


def payload(row=None):
    row = row or {
        "businessDate": "2026-11-19",
        "securityId": 1234,
        "symbol": "RHGCL",
        "securityName": "Rapti Hydro And General Construction Limited",
        "openPrice": 252.10,
        "highPrice": 259.50,
        "lowPrice": 252.10,
        "closePrice": 258.00,
        "totalTradedQuantity": 9054,
        "totalTradedValue": 2332952.50,
        "totalTrades": 103,
    }
    return json.dumps({"content": [row], "totalElements": 1, "totalPages": 1}).encode()


class OfficialEodCaptureTests(unittest.TestCase):
    URL = "https://www.nepalstock.com/api/nots/nepse-data/today-price?size=500&page=0&businessDate=2026-11-19"

    def validate(self, raw=None, **kwargs):
        args = {
            "expected_symbol": "RHGCL",
            "expected_date": "2026-11-19",
            "source_url": self.URL,
            "retrieved_at": "2026-11-26T10:00:00+05:45",
            "raw_payload_file": "capture.json",
        }
        args.update(kwargs)
        return M.validate_capture(raw or payload(), **args)

    def test_valid_exact_row_is_accepted_and_hashed(self):
        result = self.validate()
        self.assertEqual(result["status"], "OFFICIAL_CAPTURE_ACCEPTED")
        self.assertEqual(result["evidence_tier"], "OFFICIAL_NEPSE_EOD_CAPTURE")
        self.assertEqual(result["parsed_ohlcv"]["close"], "258.0")
        self.assertEqual(len(result["raw_payload_sha256"]), 64)
        self.assertFalse(result["raw_archive_mutated"])

    def test_duplicate_symbol_date_rows_are_rejected(self):
        row = json.loads(payload())["content"][0]
        raw = json.dumps({"content": [row, row], "totalElements": 2, "totalPages": 1}).encode()
        with self.assertRaisesRegex(M.EvidenceError, "found 2"):
            self.validate(raw)

    def test_wrong_date_is_rejected(self):
        row = json.loads(payload())["content"][0]
        row["businessDate"] = "2026-11-20"
        with self.assertRaisesRegex(M.EvidenceError, "found 0"):
            self.validate(payload(row))

    def test_non_official_host_is_rejected(self):
        with self.assertRaisesRegex(M.EvidenceError, "official NEPSE host"):
            self.validate(source_url="https://hamroshare.com.np/company/RHGCL")

    def test_timezone_is_required_for_retrieval_timestamp(self):
        with self.assertRaisesRegex(M.EvidenceError, "timezone offset"):
            self.validate(retrieved_at="2026-11-26T10:00:00")

    def test_wrong_official_path_is_rejected(self):
        with self.assertRaisesRegex(M.EvidenceError, "today-price EOD endpoint"):
            self.validate(source_url="https://www.nepalstock.com/api/nots/nepse-data/price-volume?businessDate=2026-11-19")

    def test_source_url_date_must_match_expected_date(self):
        with self.assertRaisesRegex(M.EvidenceError, "businessDate"):
            self.validate(source_url="https://www.nepalstock.com/api/nots/nepse-data/today-price?businessDate=2026-11-20")

    def test_pagination_metadata_is_required(self):
        raw = json.dumps({"content": [json.loads(payload())["content"][0]]}).encode()
        with self.assertRaisesRegex(M.EvidenceError, "totalElements and totalPages"):
            self.validate(raw)

    def test_invalid_security_id_is_rejected(self):
        row = json.loads(payload())["content"][0]
        row["securityId"] = 0
        with self.assertRaisesRegex(M.EvidenceError, "securityId"):
            self.validate(payload(row))

    def test_high_below_low_is_rejected(self):
        row = json.loads(payload())["content"][0]
        row["highPrice"] = 250
        with self.assertRaisesRegex(M.EvidenceError, "highPrice is below lowPrice"):
            self.validate(payload(row))

    def test_outside_range_close_is_review_not_silent_acceptance(self):
        row = json.loads(payload())["content"][0]
        row["closePrice"] = 260
        result = self.validate(payload(row))
        self.assertEqual(result["status"], "OFFICIAL_CAPTURE_REVIEW_REQUIRED")
        self.assertIn("close_outside_range", result["quality_flags"])

    def test_missing_required_field_is_rejected(self):
        row = json.loads(payload())["content"][0]
        del row["totalTradedQuantity"]
        with self.assertRaisesRegex(M.EvidenceError, "missing required fields"):
            self.validate(payload(row))


if __name__ == "__main__":
    unittest.main()
