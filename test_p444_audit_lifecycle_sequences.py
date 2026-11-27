import csv
import tempfile
import unittest
from pathlib import Path

from tools.p444_audit_lifecycle_sequences import audit


FIELDS = ["symbol", "event_type", "effective_date", "successor_symbol",
          "effective_date_confidence", "disposition"]


class LifecycleSequenceAuditTests(unittest.TestCase):
    def write(self, rows):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name) / "ledger.csv"
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        return path

    def test_missing_dates_and_successors_are_review_only(self):
        path = self.write([
            {"symbol": "ABC", "event_type": "delisting", "effective_date": "",
             "effective_date_confidence": "corroborated", "disposition": "HOLD_UNKNOWN"},
            {"symbol": "XYZ", "event_type": "merger_successor", "effective_date": "2025-01-01",
             "effective_date_confidence": "corroborated", "disposition": "HOLD_UNKNOWN"},
        ])
        result = audit(path)
        codes = {item["code"] for item in result["findings_detail"]}
        self.assertIn("EVENT_DATE_MISSING", codes)
        self.assertIn("MERGER_SUCCESSOR_MISSING", codes)
        self.assertEqual(result["error_findings"], 0)
        self.assertEqual(result["mutations"], 0)
        self.assertEqual(result["promotions"], 0)

    def test_terminal_event_before_later_trading_is_flagged(self):
        path = self.write([
            {"symbol": "ABC", "event_type": "delisting", "effective_date": "2024-01-01",
             "effective_date_confidence": "verified", "disposition": "HOLD_UNKNOWN"},
            {"symbol": "ABC", "event_type": "trading_release", "effective_date": "2024-02-01",
             "effective_date_confidence": "verified", "disposition": "HOLD_UNKNOWN"},
        ])
        codes = [item["code"] for item in audit(path)["findings_detail"]]
        self.assertIn("TERMINAL_EVENT_PRECEDES_LATER_TRading", codes)

    def test_resumption_requires_prior_suspension_candidate(self):
        path = self.write([
            {"symbol": "ABC", "event_type": "resumption", "effective_date": "2024-02-01",
             "effective_date_confidence": "corroborated", "disposition": "HOLD_UNKNOWN"},
        ])
        codes = [item["code"] for item in audit(path)["findings_detail"]]
        self.assertIn("RESUMPTION_WITHOUT_PRIOR_SUSPENSION", codes)

    def test_bad_schema_fails_closed(self):
        path = self.write([{"symbol": "ABC"}])
        with self.assertRaisesRegex(ValueError, "schema"):
            audit(path)


if __name__ == "__main__":
    unittest.main()
