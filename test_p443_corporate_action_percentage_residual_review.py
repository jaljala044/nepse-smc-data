import json
import unittest
from collections import Counter
from decimal import Decimal
from pathlib import Path


ARTIFACT = Path(__file__).parent / "reference" / "P443_CORPORATE_ACTION_PERCENTAGE_RESIDUAL_REVIEW.json"


class CorporateActionPercentageResidualReviewTests(unittest.TestCase):
    """Keep arithmetic residuals distinct from independently verified corporate actions."""
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.records = cls.document["records"]

    def test_declared_counts_match_records(self):
        counts = Counter(record["status"] for record in self.records)
        self.assertEqual(counts, self.document["counts"])
        self.assertEqual(len(self.records), 239)

    def test_source_rows_are_unique_and_have_provenance(self):
        keys = [(r["source_path"], r["source_line"]) for r in self.records]
        self.assertEqual(len(keys), len(set(keys)))
        for record in self.records:
            self.assertTrue(record["symbol"])
            self.assertTrue(record["source_path"])
            self.assertGreater(record["source_line"], 0)
            self.assertTrue(record["raw"])

    def test_zero_residual_candidates_are_exact_and_unapproved(self):
        candidates = [
            r for r in self.records if r["status"] == "ZERO_RESIDUAL_CANDIDATE"
        ]
        self.assertEqual(len(candidates), 207)
        for record in candidates:
            raw = record["raw"]
            bonus_missing = raw.get("bonus_share", "") == ""
            cash_missing = raw.get("cash_dividend", "") == ""
            self.assertNotEqual(bonus_missing, cash_missing, record)
            populated = raw["cash_dividend"] if bonus_missing else raw["bonus_share"]
            missing_field = "bonus_share" if bonus_missing else "cash_dividend"
            total = Decimal(raw["total_dividend"])
            component = Decimal(populated)
            self.assertEqual(total - component, Decimal("0"), record)
            self.assertEqual(record["derived_field"], missing_field)
            self.assertEqual(Decimal(record["derived_value"]), Decimal("0"))
            self.assertFalse(record["independent_verification"])
            self.assertFalse(record["adjustment_allowed"])

    def test_external_evidence_rows_are_not_imputed(self):
        held = [
            r for r in self.records if r["status"] == "EXTERNAL_EVIDENCE_REQUIRED"
        ]
        self.assertEqual(len(held), 32)
        for record in held:
            self.assertEqual(record["derived_field"], "")
            self.assertEqual(record["derived_value"], "")
            self.assertFalse(record["independent_verification"])
            self.assertFalse(record["adjustment_allowed"])

    def test_all_records_remain_unapproved(self):
        for record in self.records:
            self.assertFalse(record["adjustment_allowed"])
            self.assertFalse(record["independent_verification"])


if __name__ == "__main__":
    unittest.main()
