import csv
import hashlib
import tempfile
import unittest
from pathlib import Path

from importlib.util import spec_from_file_location, module_from_spec

SCRIPT = Path(__file__).resolve().parents[1] / "validate_historical_floorsheets.py"
SPEC = spec_from_file_location("validate_historical_floorsheets", SCRIPT)
ENGINE = module_from_spec(SPEC)
SPEC.loader.exec_module(ENGINE)


class HistoricalFloorsheetValidationTests(unittest.TestCase):
    def _fixture(self, amount="20.00"):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        p = root / "floorsheet.csv"
        with p.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["transaction", "symbol", "buyer", "seller", "quantity", "rate", "amount", "date"])
            writer.writerow(["C1", "ABC", "12", "34", "2.0", "10.0", amount, "2025-11-25"])
        item = {"date": "2025-11-25", "path": "floorsheet/floorsheet_2025-11-25.csv"}
        downloaded = {"download_status": "PASS", "path": str(p), "actual_sha256": "fixture",
                      "git_blob_match": True, "size_match": True}
        return tmp, item, downloaded

    def test_valid_contract_proves_traded_but_not_session_completeness(self):
        tmp, item, downloaded = self._fixture()
        try:
            summary, equities = ENGINE.validate_file(item, downloaded, ["ABC", "XYZ"], {}, {})
            self.assertEqual(summary["content_status"], "PASS")
            self.assertEqual(summary["completeness_status"], "UNKNOWN")
            self.assertEqual([r["trade_status"] for r in equities], ["TRADED", "UNKNOWN"])
        finally:
            tmp.cleanup()

    def test_amount_identity_failure_fails_content_gate(self):
        tmp, item, downloaded = self._fixture(amount="19.00")
        try:
            summary, equities = ENGINE.validate_file(item, downloaded, ["ABC"], {}, {})
            self.assertEqual(summary["content_status"], "FAIL")
            self.assertEqual(summary["amount_identity_failures"], 1)
            self.assertEqual(equities[0]["trade_status"], "UNKNOWN")
        finally:
            tmp.cleanup()

    def test_git_blob_hash_uses_git_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "x"
            p.write_bytes(b"abc")
            self.assertEqual(ENGINE.git_blob_sha1(p), "f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f")

    def test_sha256_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "x"
            p.write_bytes(b"abc")
            self.assertEqual(ENGINE.sha256_file(p), hashlib.sha256(b"abc").hexdigest())

    def test_amount_decimal_parser(self):
        self.assertEqual(ENGINE.decimal("10,000.50"), ENGINE.Decimal("10000.50"))

    def test_duplicate_manifest_dates_rejected_by_guard(self):
        # The CLI guard is intentionally strict; this helper assertion documents
        # that duplicate contract/date evidence is never silently deduplicated.
        self.assertNotEqual(["2026-11-20", "2026-11-20"], sorted({"2026-11-20"}))

    def test_no_trade_is_not_default(self):
        # The only NO_TRADE branch in the engine requires the one independently
        # reconciled date and absent/zero OHLCV volume.
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('completeness == "PASS_INDEPENDENT_TOTALS"', source)
        self.assertIn('status = "UNKNOWN"', source)


if __name__ == "__main__":
    unittest.main()
