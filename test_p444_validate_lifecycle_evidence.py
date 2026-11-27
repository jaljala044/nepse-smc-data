import csv
import tempfile
import unittest
from pathlib import Path

from tools.p444_validate_lifecycle_evidence import validate

FIELDS = [
    "symbol", "event_type", "effective_date", "calendar_basis", "security_id",
    "successor_symbol", "source_url", "retrieved_at_utc", "raw_payload_path",
    "raw_sha256", "git_blob_sha", "source_tier", "effective_date_confidence",
    "source_statement", "disposition",
]


class LifecycleValidatorTests(unittest.TestCase):
    def write(self, rows, fields=FIELDS):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name) / "ledger.csv"
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        return path

    def test_blank_hold_rows_are_valid_but_not_provenance_complete(self):
        path = self.write([{"symbol": "ABC", "source_tier": "unknown",
                            "effective_date_confidence": "none", "disposition": "HOLD_UNKNOWN"}])
        result = validate(path)
        self.assertTrue(result["valid"])
        self.assertEqual(result["provenance_complete_rows"], 0)

    def test_missing_schema_columns_fail_closed(self):
        path = self.write([{"symbol": "ABC"}], fields=["symbol", "event_type"])
        result = validate(path)
        self.assertFalse(result["valid"])
        self.assertIn("MISSING_REQUIRED_COLUMNS", [item["code"] for item in result["issues"]])

    def test_duplicate_schema_columns_fail_closed(self):
        path = self.write([], fields=FIELDS + ["symbol"])
        result = validate(path)
        self.assertIn("DUPLICATE_COLUMN_NAME", [item["code"] for item in result["issues"]])

    def test_incomplete_primary_claim_is_flagged(self):
        path = self.write([{"symbol": "ABC", "event_type": "delisting",
                            "effective_date": "2026-01-01", "source_url": "https://example.org",
                            "source_tier": "exchange_primary", "effective_date_confidence": "verified",
                            "disposition": "HOLD_UNKNOWN"}])
        codes = [item["code"] for item in validate(path)["issues"]]
        self.assertIn("INCOMPLETE_VERIFIED_PROVENANCE", codes)
        self.assertIn("VERIFIED_EVENT_MISSING_SECURITY_ID", codes)

    def test_invalid_date_event_tier_and_confidence_are_flagged(self):
        path = self.write([{"symbol": "ABC", "event_type": "trade_end",
                            "effective_date": "not-a-date", "source_tier": "blog",
                            "effective_date_confidence": "certain", "disposition": "HOLD_UNKNOWN"}])
        codes = [item["code"] for item in validate(path)["issues"]]
        self.assertIn("INVALID_EVENT_TYPE", codes)
        self.assertIn("INVALID_EFFECTIVE_DATE", codes)
        self.assertIn("INVALID_SOURCE_TIER", codes)
        self.assertIn("INVALID_CONFIDENCE", codes)

    def test_missing_event_date_and_merger_successor_are_flagged(self):
        path = self.write([{"symbol": "ABC", "event_type": "merger_successor",
                            "source_tier": "issuer_primary", "effective_date_confidence": "corroborated",
                            "disposition": "HOLD_UNKNOWN"}])
        codes = [item["code"] for item in validate(path)["issues"]]
        self.assertIn("EVENT_DATE_MISSING", codes)
        self.assertIn("MERGER_SUCCESSOR_MISSING", codes)

    def test_conflicting_same_date_events_are_flagged(self):
        base = {"symbol": "ABC", "event_type": "listing", "effective_date": "2020-01-01",
                "source_tier": "exchange_primary", "effective_date_confidence": "corroborated",
                "disposition": "HOLD_UNKNOWN"}
        first = dict(base, source_url="https://exchange.example/a")
        second = dict(base, source_url="https://exchange.example/b")
        codes = [item["code"] for item in validate(self.write([first, second]))["issues"]]
        self.assertIn("CONFLICTING_SAME_DATE_EVENT", codes)

    def test_duplicate_event_record_is_flagged(self):
        row = {"symbol": "ABC", "event_type": "listing", "effective_date": "2020-01-01",
               "source_url": "https://exchange.example/doc", "source_tier": "exchange_primary",
               "effective_date_confidence": "corroborated", "disposition": "HOLD_UNKNOWN"}
        codes = [item["code"] for item in validate(self.write([row, row]))["issues"]]
        self.assertIn("DUPLICATE_EVENT_RECORD", codes)


if __name__ == "__main__":
    unittest.main()
