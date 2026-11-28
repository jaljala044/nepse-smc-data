import tempfile
import unittest
from pathlib import Path

from tools.shared_validation_registry import ValidationRegistry


class SharedValidationRegistryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.db = self.root / "validation.sqlite3"
        self.registry = ValidationRegistry(self.db)
        self.a = self.root / "repo-a.csv"
        self.b = self.root / "repo-b.csv"
        self.a.write_bytes(b"symbol,date,close\nNABIL,2026-11-20,500\n")
        self.b.write_bytes(self.a.read_bytes())

    def tearDown(self):
        self.temp.cleanup()

    def key(self, path, schema="ohlcv-v1", validator="ohlcv-checks-v1"):
        return self.registry.make_key(path, "daily_ohlcv", schema, validator)

    def test_identical_files_share_validation_result(self):
        key_a = self.key(self.a)
        self.registry.record(key_a, "passed", {"rows": 1})
        cached = self.registry.lookup(self.key(self.b))
        self.assertIsNotNone(cached)
        self.assertEqual(cached["status"], "passed")
        self.assertEqual(cached["report"]["rows"], 1)

    def test_changed_bytes_require_new_validation(self):
        self.registry.record(self.key(self.a), "passed", {"rows": 1})
        self.b.write_bytes(self.b.read_bytes() + b"NABIL,2026-11-21,505\n")
        self.assertIsNone(self.registry.lookup(self.key(self.b)))

    def test_schema_or_validator_version_change_requires_new_validation(self):
        self.registry.record(self.key(self.a), "passed", {"rows": 1})
        self.assertIsNone(self.registry.lookup(self.key(self.a, schema="ohlcv-v2")))
        self.assertIsNone(self.registry.lookup(self.key(self.a, validator="ohlcv-checks-v2")))

    def test_failed_result_is_reused_for_unchanged_input(self):
        self.registry.record(self.key(self.a), "failed", {"errors": ["bad close"]})
        cached = self.registry.lookup(self.key(self.b))
        self.assertEqual(cached["status"], "failed")

    def test_invalid_status_is_rejected(self):
        with self.assertRaises(ValueError):
            self.registry.record(self.key(self.a), "approved")

if __name__ == "__main__":
    unittest.main()
