import csv
import hashlib
from collections import Counter
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
INVENTORY = ROOT / "reference" / "NEPSE_GLOBAL_DUPLICATE_AUDIT_INVENTORY.csv"
PINNED_COMMIT = "56362fb4f65b91fdcca8f50b50e53ad80e703649"
EXPECTED_COUNTS = {
    "related_project_artifact": 36,
    "session_calendar": 32,
    "market_or_floorsheet_summary": 13,
    "floorsheet_or_reconciliation": 33,
    "ohlcv_symbol_archive": 525,
    "provider_or_audit_archive": 226,
    "scanner_input_archive": 63,
}


def git_blob_sha(data):
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


class GlobalDuplicateAuditInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with INVENTORY.open(newline="", encoding="utf-8") as stream:
            cls.rows = list(csv.DictReader(stream))

    def test_inventory_has_expected_scope_and_unique_paths(self):
        self.assertEqual(len(self.rows), 928)
        paths = [row["path"] for row in self.rows]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertEqual(dict(Counter(row["category"] for row in self.rows)), EXPECTED_COUNTS)

    def test_inventory_pins_commit_and_blob_metadata(self):
        for row in self.rows:
            with self.subTest(path=row["path"]):
                self.assertEqual(row["repository"], "jaljala044/nepse-smc-data")
                self.assertEqual(row["ref"], "main")
                self.assertEqual(row["commit_sha"], PINNED_COMMIT)
                self.assertRegex(row["git_blob_sha"], r"^[0-9a-f]{40}$")
                self.assertGreater(int(row["bytes"]), 0)
                self.assertIn(row["scan_status"], {
                    "metadata_indexed_content_scan_pending",
                    "inventory_only_format_not_row_scanned",
                })

    def test_all_inventory_entries_match_pinned_checkout_bytes(self):
        for row in self.rows:
            with self.subTest(path=row["path"]):
                path = ROOT / row["path"]
                self.assertTrue(path.is_file(), f"missing inventory path: {row['path']}")
                data = path.read_bytes()
                self.assertEqual(len(data), int(row["bytes"]))
                self.assertEqual(git_blob_sha(data), row["git_blob_sha"])


if __name__ == "__main__":
    unittest.main()
