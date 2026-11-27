"""Regression tests for the 2024-08-01 rate-precision diagnostic."""
import unittest

from tools.p443_hf_20240801_rate_precision import analyze_rows


def make_row(i, rate="541.00", quantity="10", amount="5406.00"):
    return {
        "error": "amount_arithmetic_mismatch",
        "contract": f"2024080101{i:07d}",
        "date": "2024-08-01",
        "symbol": "TEST",
        "buyer": "58",
        "seller": "17",
        "quantity": quantity,
        "rate": rate,
        "amount": amount,
    }


class RatePrecisionDiagnosticTests(unittest.TestCase):
    def test_whole_rupee_rounding_pattern_is_reported_without_repair(self):
        rows = [make_row(i) for i in range(72496)]
        rows.extend(make_row(72496 + i, rate="213.00", quantity="2", amount="427.00") for i in range(4))
        report = analyze_rows(rows)
        self.assertEqual(report["input_rows"], 72500)
        self.assertEqual(report["stored_rate_whole_rupee_rows"], 72500)
        self.assertEqual(report["implied_rate_rounds_half_up_to_stored_rate"], 72496)
        self.assertEqual(len(report["half_up_rounding_exception_rows"]), 4)
        self.assertFalse(report["amount_or_rate_reconstruction_authorized"])
        self.assertEqual(report["rows_changed"], 0)
        self.assertEqual(report["rows_promoted"], 0)

    def test_changed_invalid_row_count_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "unexpected 2024-08-01 invalid-row count"):
            analyze_rows([make_row(i) for i in range(10)])

    def test_non_whole_rate_fails_closed(self):
        rows = [make_row(i) for i in range(72500)]
        rows[0]["rate"] = "541.25"
        with self.assertRaisesRegex(ValueError, "not all whole-rupee"):
            analyze_rows(rows)

    def test_other_date_is_rejected(self):
        rows = [make_row(i) for i in range(72500)]
        rows[0]["date"] = "2024-08-02"
        with self.assertRaisesRegex(ValueError, "only 2024-08-01"):
            analyze_rows(rows)


if __name__ == "__main__":
    unittest.main()
