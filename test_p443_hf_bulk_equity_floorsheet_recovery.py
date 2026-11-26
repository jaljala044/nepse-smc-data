"""Regression tests for the HF-only bulk floorsheet evidence queue."""
import unittest

from tools.p443_hf_bulk_equity_floorsheet_recovery import parse_hf_session, select_hf_dates


class HFBulkRecoveryTests(unittest.TestCase):
    def test_selects_only_hf_dates_not_already_covered_by_primary(self):
        bydate = {
            "2025-01-01": {"AAA", "BBB"},
            "2025-01-02": {"AAA"},
            "2025-01-03": {"AAA", "BBB", "CCC"},
            "2025-01-04": {"AAA", "BBB"},
        }
        primary = {"2025-01-01"}
        hf = {"2025-01-01", "2025-01-02", "2025-01-03"}
        selected, ordered = select_hf_dates(bydate, primary, hf, 2)
        self.assertEqual(selected, ["2025-01-03", "2025-01-02"])
        self.assertEqual(ordered, ["2025-01-03", "2025-01-02"])

    def test_offset_advances_through_deterministic_batches(self):
        bydate = {
            "2025-01-01": {"A", "B", "C"},
            "2025-01-02": {"A", "B"},
            "2025-01-03": {"A"},
        }
        selected, ordered = select_hf_dates(bydate, set(), set(bydate), 1, 1)
        self.assertEqual(ordered, ["2025-01-01", "2025-01-02", "2025-01-03"])
        self.assertEqual(selected, ["2025-01-02"])

    def test_duplicate_contract_ids_are_preserved_as_collision_findings(self):
        rows = [
            {
                "contract_no": "20250101000001", "date": "2025-01-01",
                "symbol": "AAA", "buyer": "58", "seller": "17",
                "quantity": "10", "rate": "100", "amount": "1000",
            },
            {
                "contract_no": "20250101000001", "date": "2025-01-01",
                "symbol": "BBB", "buyer": "58", "seller": "18",
                "quantity": "20", "rate": "50", "amount": "1000",
            },
        ]
        contracts, collisions, collision_rows = parse_hf_session(
            iter(rows), "2025-01-01"
        )
        self.assertEqual(contracts.total(), 2)
        self.assertEqual(collisions, {"20250101000001": 2})
        self.assertEqual(len(collision_rows), 2)

    def test_empty_hf_session_is_not_treated_as_no_trade(self):
        with self.assertRaisesRegex(ValueError, "empty session"):
            parse_hf_session(iter([]), "2025-01-01")

    def test_invalid_batch_bounds_are_rejected(self):
        with self.assertRaises(ValueError):
            select_hf_dates({}, set(), set(), 0)
        with self.assertRaises(ValueError):
            select_hf_dates({}, set(), set(), 1, -1)


if __name__ == "__main__":
    unittest.main()
