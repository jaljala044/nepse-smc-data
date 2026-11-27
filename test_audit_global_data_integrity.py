import csv
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from tools.audit_global_data_integrity import finding_totals, scan_csv

ROOT = Path(__file__).resolve().parent


class GlobalBusinessKeyAuditTests(unittest.TestCase):
    def scan_rows(self, header, rows, filename="floorsheet_2025-01-02.csv"):
        temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.addCleanup(temp.cleanup)
        path = Path(temp.name) / filename
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(header)
            writer.writerows(rows)
        findings = []
        stats = Counter()
        scan_csv(path, "floorsheet_or_reconciliation", findings, stats)
        return findings, stats

    def test_reused_contract_number_with_distinct_record_ids_is_not_duplicate(self):
        findings, _ = self.scan_rows(
            ["Date", "ID", "ContractNo", "Symbol", "Buyer", "Seller", "Quantity"],
            [
                ["2025-01-02", "1001", "77", "ABC", "1", "2", "10"],
                ["2025-01-02", "1002", "77", "XYZ", "1", "2", "20"],
            ],
        )
        self.assertEqual(findings, [])

    def test_record_id_is_scoped_to_session_date(self):
        findings, _ = self.scan_rows(
            ["Date", "ID", "ContractNo", "Symbol", "Buyer", "Seller", "Quantity"],
            [
                ["2025-01-02", "1001", "77", "ABC", "1", "2", "10"],
                ["2025-01-03", "1001", "78", "ABC", "1", "2", "10"],
            ],
        )
        self.assertEqual(findings, [])

    def test_repeated_record_id_on_same_session_is_flagged(self):
        findings, _ = self.scan_rows(
            ["Date", "ID", "ContractNo", "Symbol", "Buyer", "Seller", "Quantity"],
            [
                ["2025-01-02", "1001", "77", "ABC", "1", "2", "10"],
                ["2025-01-02", "1001", "78", "XYZ", "3", "4", "20"],
            ],
        )
        self.assertEqual([row["finding_type"] for row in findings],
                         ["duplicate_floorsheet_record_id"])

    def test_exact_repeated_trade_row_is_separate_finding(self):
        findings, _ = self.scan_rows(
            ["Date", "ID", "ContractNo", "Symbol", "Buyer", "Seller", "Quantity"],
            [
                ["2025-01-02", "1001", "77", "ABC", "1", "2", "10"],
                ["2025-01-02", "1001", "77", "ABC", "1", "2", "10"],
            ],
        )
        self.assertEqual({row["finding_type"] for row in findings},
                         {"exact_duplicate_floorsheet_row", "duplicate_floorsheet_record_id"})

    def test_finding_total_uses_emitted_record_id_class(self):
        rows = [{"finding_type": "duplicate_floorsheet_record_id"}]
        totals = finding_totals(rows)
        self.assertEqual(totals["floorsheet_record_id_repeats"], 1)
        self.assertNotIn("floorsheet_contract_duplicates", totals)


if __name__ == "__main__":
    unittest.main()
