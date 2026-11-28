import tempfile
import unittest
from pathlib import Path

from nepse_shared_validation import ValidationRegistry, run_cached_validation


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

    def test_run_cached_validation_skips_identical_file_callback(self):
        calls = []
        def validator(path):
            calls.append(path)
            return {"valid": True, "rows": 1}
        first = run_cached_validation(
            self.registry, self.a, dataset_kind="daily_ohlcv",
            schema_version="ohlcv-v1", validator_version="ohlcv-checks-v1",
            validator=validator,
        )
        second = run_cached_validation(
            self.registry, self.b, dataset_kind="daily_ohlcv",
            schema_version="ohlcv-v1", validator_version="ohlcv-checks-v1",
            validator=validator,
        )
        self.assertFalse(first["cache_hit"])
        self.assertTrue(second["cache_hit"])
        self.assertEqual(first["report"], second["report"])
        self.assertEqual(len(calls), 1)

    def test_changed_file_runs_validator_again(self):
        calls = []
        def validator(path):
            calls.append(path)
            return {"valid": True, "rows": len(calls)}
        run_cached_validation(self.registry, self.a, dataset_kind="daily_ohlcv",
            schema_version="ohlcv-v1", validator_version="v1", validator=validator)
        self.b.write_bytes(self.b.read_bytes() + b"changed")
        result = run_cached_validation(self.registry, self.b, dataset_kind="daily_ohlcv",
            schema_version="ohlcv-v1", validator_version="v1", validator=validator)
        self.assertFalse(result["cache_hit"])
        self.assertEqual(len(calls), 2)

    def test_validator_exception_is_not_cached(self):
        def broken(path):
            raise RuntimeError("temporary infrastructure error")
        with self.assertRaises(RuntimeError):
            run_cached_validation(self.registry, self.a, dataset_kind="daily_ohlcv",
                schema_version="ohlcv-v1", validator_version="v1", validator=broken)
        self.assertIsNone(self.registry.lookup(self.registry.make_key(self.a, "daily_ohlcv", "ohlcv-v1", "v1")))

    def test_validator_must_return_boolean_valid_field(self):
        with self.assertRaises(ValueError):
            run_cached_validation(self.registry, self.a, dataset_kind="daily_ohlcv",
                schema_version="ohlcv-v1", validator_version="v1",
                validator=lambda path: {"valid": "yes"})

if __name__ == "__main__":
    unittest.main()
