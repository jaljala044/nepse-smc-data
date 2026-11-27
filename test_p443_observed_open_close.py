import unittest
from datetime import time
from decimal import Decimal
from tools.p443_observed_open_close import trade_time,boundaries

class ObservedBoundaryTests(unittest.TestCase):
    def test_unsorted_execution_order(self):
        self.assertEqual(boundaries([(time(14),Decimal(12)),(time(11),Decimal(10)),(time(12),Decimal(15))]),("OBSERVED_BOUNDARIES",Decimal(10),Decimal(12)))
    def test_missing_time(self):
        self.assertEqual(boundaries([(None,Decimal(10)),(time(14),Decimal(12))]),("TIMESTAMP_INCOMPLETE",None,None))
    def test_boundary_conflict(self):
        self.assertEqual(boundaries([(time(11),Decimal(10)),(time(11),Decimal(11)),(time(14),Decimal(12))]),("AMBIGUOUS_BOUNDARY_TIE",None,None))
    def test_equal_price_ties(self):
        self.assertEqual(boundaries([(time(11),Decimal(10)),(time(11),Decimal(10))]),("OBSERVED_BOUNDARIES",Decimal(10),Decimal(10)))
    def test_empty(self):
        self.assertEqual(boundaries([]),("NO_OBSERVED_CONTRACT_UNKNOWN",None,None))
    def test_timestamp_aliases(self):
        self.assertEqual(trade_time({"time":"11:02:03","tradeTime":"2026-06-26T11:02:03"},"2026-06-26"),time(11,2,3))
    def test_invalid_timestamp(self):
        for r in ({},{"time":"25:00:00"},{"time":"2026-06-25T11:02:03"},{"time":"2026-06-26T11:02:03+05:45"},{"time":"11:00:00","tradeTime":"11:00:01"}):
            with self.subTest(row=r):
                with self.assertRaises(ValueError):trade_time(r,"2026-06-26")
if __name__=="__main__":unittest.main()
