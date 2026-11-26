"""Regression tests for equity-first unresolved repeated-candle triage."""
import unittest

from tools.p443_equity_first_repeat_review import classify


class EquityFirstRepeatReviewTests(unittest.TestCase):
    def test_equity_and_fund_are_prioritized_without_promotion(self):
        rows = [
            {"symbol": "AAA", "pair_classification": "BOTH_OPEN_TUPLE_UNVERIFIED"},
            {"symbol": "FUND", "pair_classification": "INSUFFICIENT_SESSION_EVIDENCE"},
        ]
        master = {
            "AAA": "current_equity_first_pass",
            "FUND": "current_mutual_fund",
        }
        result = list(classify(rows, master))
        self.assertEqual([r["review_priority"] for r in result],
                         ["EQUITY_RECOVERY_PRIORITY", "DEFER_MUTUAL_FUND"])
        self.assertTrue(all(r["promotion_allowed"] == "false" for r in result))

    def test_unknown_and_unclassified_instruments_are_held(self):
        rows = [
            {"symbol": "OLD", "pair_classification": "INSUFFICIENT_SESSION_EVIDENCE"},
            {"symbol": "MISSING", "pair_classification": "BOTH_OPEN_TUPLE_UNVERIFIED"},
        ]
        result = list(classify(rows, {"OLD": "delisted_or_unclassified"}))
        self.assertEqual([r["review_priority"] for r in result],
                         ["HOLD_UNCLASSIFIED", "HOLD_UNCLASSIFIED"])
        self.assertEqual([r["instrument_classification"] for r in result],
                         ["delisted_or_unclassified", "missing_master"])
        self.assertTrue(all(r["promotion_allowed"] == "false" for r in result))

    def test_recorded_closure_and_holiday_pairs_are_not_in_this_queue(self):
        rows = [
            {"symbol": "AAA", "pair_classification": "PAIR_CONTAINS_RECORDED_CLOSURE"},
            {"symbol": "AAA", "pair_classification": "PAIR_CONTAINS_HISTORICAL_LISTED_HOLIDAY"},
        ]
        self.assertEqual(list(classify(rows, {"AAA": "current_equity_first_pass"})), [])


if __name__ == "__main__":
    unittest.main()
