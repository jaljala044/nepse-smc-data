import sys, unittest
from decimal import Decimal
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reconstruct import aggregate_transactions

class AggregationTests(unittest.TestCase):
    def setUp(self):
        self.lookup = {"1": {"symbol": "AAA"}}

    def test_extrema_volume_turnover_and_ordered_open_close(self):
        rows = [
            [2025072800000001, 1, 1, 2, 3, 10.5, 31.5, "10:00:00"],
            [2025072800000002, 1, 1, 2, 4, 12.0, 48.0, "10:01:00"],
        ]
        got, audit = aggregate_transactions(rows, self.lookup, ["AAA"])
        self.assertEqual(got["AAA"]["open"], Decimal("10.5"))
        self.assertEqual(got["AAA"]["close"], Decimal("12.0"))
        self.assertEqual(got["AAA"]["high"], Decimal("12.0"))
        self.assertEqual(got["AAA"]["low"], Decimal("10.5"))
        self.assertEqual(got["AAA"]["volume"], Decimal("7"))
        self.assertEqual(got["AAA"]["turnover"], Decimal("79.5"))
        self.assertEqual(audit["malformed_rows"], [])

    def test_blank_timestamps_fail_closed_for_open_close(self):
        rows = [[2025072800000001,1,1,2,3,10,30,""],[2025072800000002,1,1,2,4,12,48,""]]
        got, _ = aggregate_transactions(rows, self.lookup, ["AAA"])
        self.assertEqual(got["AAA"]["open"], "UNKNOWN")
        self.assertEqual(got["AAA"]["close"], "UNKNOWN")
        self.assertEqual(got["AAA"]["high"], Decimal("12"))

    def test_malformed_row_is_reported_not_silently_dropped(self):
        got, audit = aggregate_transactions([[1,2]], self.lookup, ["AAA"])
        self.assertEqual(audit["malformed_rows"], [0])
        self.assertEqual(got["AAA"]["volume"], "UNKNOWN")

    def test_duplicate_contract_id_marks_symbol_incomplete(self):
        row = [2025072800000001,1,1,2,3,10,30,"10:00:00"]
        got, audit = aggregate_transactions([row,row], self.lookup, ["AAA"])
        self.assertEqual(len(audit["duplicate_contract_ids"]), 1)
        self.assertTrue(got["AAA"]["incomplete"])
        self.assertEqual(got["AAA"]["volume"], "UNKNOWN")

    def test_absent_target_symbol_is_unknown(self):
        got, _ = aggregate_transactions([], self.lookup, ["AAA"])
        self.assertEqual(got["AAA"]["trade_count"], 0)
        self.assertEqual(got["AAA"]["high"], "UNKNOWN")

if __name__ == "__main__": unittest.main()
