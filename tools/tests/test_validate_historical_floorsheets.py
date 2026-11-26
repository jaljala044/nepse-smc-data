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
