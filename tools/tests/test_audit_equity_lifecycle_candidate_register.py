import unittest
from pathlib import Path
from audit_equity_lifecycle_candidate_register import audit
ROOT=Path(__file__).resolve().parents[2]
class EquityLifecycleRegisterTests(unittest.TestCase):
    def test_imported_register_is_consistent_and_nonpromoting(self):
        r=audit(ROOT/"reference/nepse_equity_lifecycle_coverage_input_2026-11-26.csv",ROOT/"reference/nepse_security_lifecycle_events_2026-11-26.csv",ROOT/"reference/nepse_official_security_list_2026-11-25.raw.json")
        self.assertEqual(r["lifecycle_rows"],281)
        self.assertEqual(r["typed_events"],6)
        self.assertEqual(r["dated_secondary_starts"],44)
        self.assertEqual(r["blank_unverified_starts"],237)
        self.assertEqual(r["current_official_id_symbol_matches"],281)
        self.assertEqual(r["primary_first_trade_proofs"],0)
        self.assertFalse(r["promotion_allowed"])
if __name__=="__main__":unittest.main()
