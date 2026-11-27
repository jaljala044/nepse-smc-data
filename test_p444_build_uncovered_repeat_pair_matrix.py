import unittest
from tools.p444_build_uncovered_repeat_pair_matrix import identity_fields, session_fields

class P444MatrixTests(unittest.TestCase):
    def test_current_snapshot_id_is_not_historical_id(self):
        x=identity_fields({"historical_stable_id":"","historical_effective_date_verified":"false","current_snapshot_security_id":"8041"})
        self.assertEqual(x["identity_scope"],"current_snapshot_only")
        self.assertEqual(x["historical_stable_id"],"")
    def test_historical_id_requires_verified_interval(self):
        x=identity_fields({"historical_stable_id":"8041","historical_effective_date_verified":"false","current_snapshot_security_id":"8041"})
        self.assertEqual(x["identity_scope"],"current_snapshot_only")
    def test_missing_session_stays_unknown(self):
        self.assertEqual(session_fields("ABC","2024-01-01",{}, {})["status"],"UNKNOWN_NO_PINNED_SESSION_EVIDENCE")
    def test_market_closed_and_security_execution_conflict_is_visible(self):
        closed={"2024-01-02":[{"source_id":"calendar","evidence_uri":"uri"}]}
        execution={("ABC","2024-01-02"):[{"source_id":"eod","source_capture_file":"capture.json","raw_evidence_sha256":"hash","security_id":"1","total_trades":"1","total_traded_quantity":"10","total_traded_value":"100","retrieved_at_utc":"time"}]}
        self.assertEqual(session_fields("ABC","2024-01-02",closed,execution)["status"],"CONFLICTING_MARKET_CLOSED_AND_SECURITY_TRADE")

if __name__=="__main__": unittest.main()
