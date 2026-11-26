"""Tests for shared-field full-session parity normalization and review gating."""
import unittest
from collections import Counter

from tools.p443_full_session_parity import has_collection_failures, parse, signature


class FullSessionParityTests(unittest.TestCase):
    def test_single_leading_excel_quote_is_counted_and_normalized(self):
        row = {
            "transaction": "'2025112701000001",
            "date": "2025-11-27",
            "symbol": "ACLBSL",
            "buyer": "58",
            "seller": "17",
            "quantity": "10",
            "rate": "100",
            "amount": "1000",
        }
        stats = Counter()
        result = signature(row, False, "2025-11-27", stats)
        self.assertEqual(result[1], "2025112701000001")
        self.assertEqual(stats["leading_apostrophe_contract_ids"], 1)

    def test_secondary_contract_fields_use_same_normalization(self):
        row = {
            "contract_no": "'2025112701000001",
            "calculation_date": "2025-11-27",
            "stock_symbol": "ACLBSL",
            "buyer": "58",
            "seller": "17",
            "quantity": "10",
            "rate": "100",
            "amount": "1000",
        }
        stats = Counter()
        result = signature(row, True, "2025-11-27", stats)
        self.assertEqual(result[1], "2025112701000001")
        self.assertEqual(stats["leading_apostrophe_contract_ids"], 1)

    def test_duplicate_ids_after_normalization_are_rejected(self):
        rows = [
            {
                "transaction": "'2025112701000001", "date": "2025-11-27",
                "symbol": "ACLBSL", "buyer": "58", "seller": "17",
                "quantity": "10", "rate": "100", "amount": "1000",
            },
            {
                "transaction": "2025112701000001", "date": "2025-11-27",
                "symbol": "ACLBSL", "buyer": "58", "seller": "17",
                "quantity": "10", "rate": "100", "amount": "1000",
            },
        ]
        with self.assertRaisesRegex(ValueError, "duplicate contract"):
            parse(iter(rows), False, "2025-11-27")

    def test_exact_whole_rupee_floor_amount_is_accepted_and_counted(self):
        row = {
            "transaction": "2025112701000001", "date": "2025-11-27",
            "symbol": "ACLBSL", "buyer": "58", "seller": "17",
            "quantity": "10", "rate": "100.05", "amount": "1000",
        }
        stats = Counter()
        signature(row, False, "2025-11-27", stats)
        self.assertEqual(stats["amount_floor_truncated"], 1)
        self.assertEqual(stats["amount_exact_match"], 0)

    def test_non_floor_amount_mismatch_is_rejected(self):
        row = {
            "transaction": "2025112701000001", "date": "2025-11-27",
            "symbol": "ACLBSL", "buyer": "58", "seller": "17",
            "quantity": "10", "rate": "100.05", "amount": "1000.2",
        }
        with self.assertRaisesRegex(ValueError, "invalid contract"):
            signature(row, False, "2025-11-27")

    def test_invalid_contract_prefix_is_not_silently_removed(self):
        row = {
            "transaction": "''2025112701000001", "date": "2025-11-27",
            "symbol": "ACLBSL", "buyer": "58", "seller": "17",
            "quantity": "10", "rate": "100", "amount": "1000",
        }
        with self.assertRaisesRegex(ValueError, "invalid contract"):
            signature(row, False, "2025-11-27")

    def test_row_conflict_is_review_not_collection_failure(self):
        self.assertFalse(has_collection_failures([
            {"status": "EXACT_PARITY"},
            {"status": "ROW_CONFLICT"},
        ]))
        self.assertTrue(has_collection_failures([
            {"status": "EXACT_PARITY"},
            {"status": "UNAVAILABLE_OR_INVALID"},
        ]))


if __name__ == "__main__":
    unittest.main()
