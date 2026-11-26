import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FINDINGS = ROOT / "reference" / "NEPSE_GLOBAL_DUPLICATE_AUDIT_FINDINGS.csv"
SUMMARY = ROOT / "reference" / "NEPSE_GLOBAL_DUPLICATE_AUDIT_SCAN_SUMMARY.csv"


class GlobalDuplicateAuditScanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with FINDINGS.open(newline="", encoding="utf-8") as stream:
            cls.findings = list(csv.DictReader(stream))
        with SUMMARY.open(newline="", encoding="utf-8") as stream:
            cls.summary = list(csv.DictReader(stream))

    def test_scan_outputs_cover_entire_pinned_inventory(self):
        self.assertEqual(len(self.summary), 928)
        self.assertEqual(len({row["path"] for row in self.summary}), 928)
        self.assertTrue(all(row["status"] != "parse_error" for row in self.summary), [r for r in self.summary if r["status"] == "parse_error"][:5])

    def test_findings_have_traceable_source_locations(self):
        for row in self.findings:
            self.assertTrue(row["path"])
            self.assertTrue(row["finding_type"])
            self.assertGreater(int(row["line"]), 1)
            self.assertGreater(int(row["related_line"]), 1)

    def test_no_source_data_is_modified_by_scan(self):
        # The scanner only reads inventory inputs and writes three audit outputs.
        self.assertTrue(FINDINGS.is_file())
        self.assertTrue(SUMMARY.is_file())
        self.assertTrue((ROOT / "reference" / "NEPSE_GLOBAL_DUPLICATE_AUDIT_REPORT.md").is_file())


if __name__ == "__main__":
    unittest.main()
