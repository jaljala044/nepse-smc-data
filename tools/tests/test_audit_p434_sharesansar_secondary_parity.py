import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from audit_p434_sharesansar_secondary_parity import compare_flag


class P434SecondaryParityTests(unittest.TestCase):
    def test_exact_match_is_not_independent_validation_when_ohlc_invalid(self):
        v3 = {"Open":"447","High":"446","Low":"445","Close":"445","Volume":"72"}
        secondary = {"open":"447","high":"446","low":"445","close":"445","volume":"72"}
        status, different, valid = compare_flag({}, v3, secondary)
        self.assertEqual(status, "EXACT_MATCH_NOT_INDEPENDENT_CORROBORATION")
        self.assertEqual(different, "")
        self.assertFalse(valid)

    def test_difference_is_flagged_not_promoted(self):
        v3 = {"Open":"447","High":"446","Low":"445","Close":"445","Volume":"72"}
        secondary = {"open":"445","high":"446","low":"445","close":"445","volume":"72"}
        status, different, valid = compare_flag({}, v3, secondary)
        self.assertEqual(status, "SECONDARY_VALUE_DIFFERENCE_REVIEW")
        self.assertEqual(different, "open")
        self.assertTrue(valid)


if __name__ == "__main__":
    unittest.main()
