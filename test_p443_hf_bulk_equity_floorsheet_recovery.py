"""Regression tests for the HF-only bulk floorsheet evidence queue."""
import unittest

from tools.p443_hf_bulk_equity_floorsheet_recovery import select_hf_dates


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

    def test_invalid_batch_bounds_are_rejected(self):
        with self.assertRaises(ValueError):
            select_hf_dates({}, set(), set(), 0)
        with self.assertRaises(ValueError):
            select_hf_dates({}, set(), set(), 1, -1)


if __name__ == "__main__":
    unittest.main()
