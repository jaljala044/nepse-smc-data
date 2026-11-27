import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.p444_audit_281_security_history import audit


class SecurityHistoryCaptureAuditTests(unittest.TestCase):
    def make_capture(self, rows, manifest_digest=None):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name) / "symbols"
        payload_dir = root / "TEST"
        payload_dir.mkdir(parents=True)
        payload = payload_dir / "response-01.bin"
        raw = json.dumps({"content": rows}, separators=(",", ":")).encode()
        payload.write_bytes(raw)
        digest = manifest_digest or hashlib.sha256(raw).hexdigest()
        manifest = Path(temp.name) / "SHA256SUMS"
        manifest.write_text(f"{digest}  symbols/TEST/response-01.bin\n", encoding="utf-8")
        return root, manifest

    @staticmethod
    def row(day, **changes):
        value = {
            "businessDate": day,
            "totalTrades": 10,
            "totalTradedQuantity": 100,
            "totalTradedValue": 12345.5,
            "highPrice": 125.0,
            "lowPrice": 120.0,
            "closePrice": 123.0,
        }
        value.update(changes)
        return value

    def test_valid_payload_matches_manifest_and_preserves_missing_open(self):
        root, manifest = self.make_capture([
            self.row("2026-11-26"), self.row("2026-11-25")
        ])
        result = audit(root, manifest, expected_symbols=1)
        self.assertTrue(result["valid"])
        self.assertEqual(result["symbols"], 1)
        self.assertEqual(result["total_rows"], 2)
        self.assertEqual(result["symbols_without_open_price"], 1)
        self.assertEqual(result["date_min"], "2026-11-25")
        self.assertEqual(result["date_max"], "2026-11-26")

    def test_manifest_digest_mismatch_fails_closed(self):
        root, manifest = self.make_capture([self.row("2026-11-26")], "0" * 64)
        result = audit(root, manifest, expected_symbols=1)
        self.assertFalse(result["valid"])
        self.assertIn("SHA256_MISMATCH", [x["code"] for x in result["issues"]])

    def test_duplicate_dates_and_non_descending_dates_are_reported(self):
        root, manifest = self.make_capture([
            self.row("2026-11-25"), self.row("2026-11-26"), self.row("2026-11-25")
        ])
        result = audit(root, manifest, expected_symbols=1)
        codes = [x["code"] for x in result["issues"]]
        self.assertIn("DUPLICATE_BUSINESS_DATE", codes)
        self.assertIn("DATES_NOT_DESCENDING", codes)

    def test_missing_field_and_invalid_price_range_are_reported(self):
        first = self.row("2026-11-26", closePrice=130.0)
        second = self.row("2026-11-25")
        del second["totalTrades"]
        root, manifest = self.make_capture([first, second])
        result = audit(root, manifest, expected_symbols=1)
        codes = [x["code"] for x in result["issues"]]
        self.assertIn("PRICE_RANGE_INCONSISTENT", codes)
        self.assertIn("REQUIRED_FIELDS_MISSING", codes)

    def test_expected_symbol_count_is_enforced(self):
        root, manifest = self.make_capture([self.row("2026-11-26")])
        result = audit(root, manifest, expected_symbols=281)
        self.assertFalse(result["valid"])
        self.assertIn("SYMBOL_COUNT_MISMATCH", [x["code"] for x in result["issues"]])


if __name__ == "__main__":
    unittest.main()
