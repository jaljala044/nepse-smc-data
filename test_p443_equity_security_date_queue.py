"""Regression tests for unique equity security-date evidence requests."""
import unittest

from tools.p443_equity_security_date_queue import build


class EquitySecurityDateQueueTests(unittest.TestCase):
    def test_deduplicates_security_dates_and_keeps_open_pair_priority(self):
        rows = [
            {
                "symbol": "AAA", "date": "2025-01-02", "row": "3",
                "previous_date": "2025-01-01", "previous_row": "2",
                "path": "ohlcv/AAA.csv", "blob_sha": "abc",
                "pair_classification": "BOTH_OPEN_TUPLE_UNVERIFIED",
                "review_priority": "EQUITY_RECOVERY_PRIORITY",
            },
            {
                "symbol": "AAA", "date": "2025-01-03", "row": "4",
                "previous_date": "2025-01-02", "previous_row": "3",
                "path": "ohlcv/AAA.csv", "blob_sha": "abc",
                "pair_classification": "INSUFFICIENT_SESSION_EVIDENCE",
                "review_priority": "EQUITY_RECOVERY_PRIORITY",
            },
        ]
        requests, pairs = build(rows)
        self.assertEqual(dict(pairs), {
            "BOTH_OPEN_TUPLE_UNVERIFIED": 1,
            "INSUFFICIENT_SESSION_EVIDENCE": 1,
        })
        self.assertEqual(len(requests), 3)
        self.assertEqual(len(requests[("AAA", "2025-01-02")]), 2)
        self.assertIn(
            "BOTH_OPEN_TUPLE_UNVERIFIED",
            {ref[3] for ref in requests[("AAA", "2025-01-02")]}
        )

    def test_non_equity_priority_rows_are_not_included(self):
        rows = [{
            "symbol": "FUND", "date": "2025-01-02", "row": "3",
            "previous_date": "2025-01-01", "previous_row": "2",
            "path": "ohlcv/FUND.csv", "blob_sha": "def",
            "pair_classification": "INSUFFICIENT_SESSION_EVIDENCE",
            "review_priority": "DEFER_MUTUAL_FUND",
        }]
        requests, pairs = build(rows)
        self.assertEqual(dict(requests), {})
        self.assertEqual(dict(pairs), {})


if __name__ == "__main__":
    unittest.main()
