"""Regression tests for two-date official-history pair classification."""
import unittest

from tools.p443_verify_unresolved_pairs import classify_pair


class UnresolvedPairEvidenceTests(unittest.TestCase):
    def test_both_dates_match_but_open_remains_unverified(self):
        result = classify_pair("HLCV_MATCH_OPEN_UNVERIFIED", "HLCV_MATCH_OPEN_UNVERIFIED")
        self.assertEqual(result, "BOTH_DATES_HLCV_EXECUTION_MATCH_OPEN_UNVERIFIED")

    def test_one_date_match_does_not_clear_the_pair(self):
        result = classify_pair("HLCV_MATCH_OPEN_UNVERIFIED", "NO_SECURITY_DATE_EVIDENCE")
        self.assertEqual(result, "ONE_DATE_HLCV_EXECUTION_MATCH_OTHER_UNVERIFIED")

    def test_mismatch_takes_priority_over_partial_match(self):
        result = classify_pair("HLCV_MISMATCH", "HLCV_MATCH_OPEN_UNVERIFIED")
        self.assertEqual(result, "HLCV_MISMATCH_REVIEW")

    def test_conflicting_official_records_are_not_collapsed(self):
        result = classify_pair("CONFLICTING_OFFICIAL_EVIDENCE", "HLCV_MATCH_OPEN_UNVERIFIED")
        self.assertEqual(result, "CONFLICTING_OFFICIAL_EVIDENCE_REVIEW")

    def test_no_evidence_on_either_date_is_explicit(self):
        result = classify_pair("NO_SECURITY_DATE_EVIDENCE", "NO_SECURITY_DATE_EVIDENCE")
        self.assertEqual(result, "NO_SECURITY_DATE_EVIDENCE_BOTH_DATES")


if __name__ == "__main__":
    unittest.main()
