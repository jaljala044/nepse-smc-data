import json
import unittest
from collections import Counter
from decimal import Decimal
from pathlib import Path


ARTIFACT = (
    Path(__file__).parent
    / "reference"
    / "P443_CORPORATE_ACTION_DATE_RECOVERY_QUEUE.json"
)


class CorporateActionDateRecoveryQueueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.normalized = cls.document["normalized_candidates"]
        cls.queue = cls.document["date_recovery_queue"]

    def test_queue_counts_and_approval_boundary(self):
        counts = Counter(row["status"] for row in self.queue)
        self.assertEqual(counts["EXTERNAL_EVIDENCE_REQUIRED"], 30)
        self.assertEqual(counts["ZERO_RESIDUAL_CANDIDATE"], 5)
        self.assertEqual(len(self.queue), 35)
        self.assertEqual(self.document["approved"], 0)
        for row in self.queue:
            self.assertFalse(row["adjustment_allowed"])
            self.assertFalse(row["independent_verification"])

    def test_source_row_provenance_is_unique(self):
        keys = [(row["source_path"], row["source_line"]) for row in self.queue]
        self.assertEqual(len(keys), len(set(keys)))
        for row in self.queue:
            self.assertTrue(row["symbol"])
            self.assertGreater(row["source_line"], 0)
            self.assertTrue(row["raw"])
            self.assertIn("target_equity", row)

    def test_zero_residual_rows_are_arithmetic_only(self):
        for row in self.queue:
            if row["status"] != "ZERO_RESIDUAL_CANDIDATE":
                self.assertEqual(row["derived_field"], "")
                self.assertEqual(row["derived_value"], "")
                continue
            raw = row["raw"]
            bonus_missing = raw.get("bonus_share", "") == ""
            cash_missing = raw.get("cash_dividend", "") == ""
            self.assertNotEqual(bonus_missing, cash_missing, row)
            populated = raw["cash_dividend"] if bonus_missing else raw["bonus_share"]
            self.assertEqual(
                Decimal(raw["total_dividend"]) - Decimal(populated), Decimal("0")
            )
            self.assertEqual(row["derived_field"], "bonus_share" if bonus_missing else "cash_dividend")
            self.assertEqual(Decimal(row["derived_value"]), Decimal("0"))
            self.assertFalse(row["adjustment_allowed"])
            self.assertFalse(row["independent_verification"])

    def test_unl_comma_normalization_preserves_raw_values(self):
        self.assertEqual(len(self.normalized), 2)
        for row in self.normalized:
            self.assertEqual(row["symbol"], "UNL")
            self.assertIn(",", row["raw"]["cash_dividend"])
            self.assertIn(",", row["raw"]["total_dividend"])
            self.assertEqual(
                Decimal(row["normalized_cash"]),
                Decimal(row["raw"]["cash_dividend"].replace(",", "")),
            )
            self.assertEqual(
                Decimal(row["normalized_total"]),
                Decimal(row["raw"]["total_dividend"].replace(",", "")),
            )
            self.assertEqual(Decimal(row["normalized_cash"]), Decimal(row["normalized_total"]))
            self.assertEqual(Decimal(row["derived_bonus"]), Decimal("0"))
            self.assertEqual(
                row["status"], "ZERO_RESIDUAL_FORMAT_NORMALIZED_CANDIDATE"
            )
            self.assertFalse(row["adjustment_allowed"])


if __name__ == "__main__":
    unittest.main()
