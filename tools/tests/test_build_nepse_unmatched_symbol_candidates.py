import csv,unittest
from pathlib import Path
from build_nepse_unmatched_symbol_candidates import build
ROOT=Path(__file__).resolve().parents[2]
class UnmatchedSymbolCandidateTests(unittest.TestCase):
    def test_candidates_and_name_hints_are_fail_closed(self):
        a,b,r=build(ROOT/"reference/nepse_official_security_list_2026-11-25.raw.json",ROOT/"reference/p429_official_security_ohlcv_reconciliation_2026-11-26.csv")
        self.assertEqual((len(a),r["reversible_escape_candidates"],r["nonmatching_stems"]),(37,8,29))
        self.assertEqual((len(b),r["name_hint_counts"]["PROMOTER_NAME_HINT"],r["name_hint_counts"]["DEBT_NAME_HINT"],r["name_hint_counts"]["FUND_NAME_HINT"],r["no_name_hint_count"]),(85,46,8,1,30))
        self.assertTrue(all(x["instrument_type"]=="UNKNOWN" for x in b))
        self.assertTrue(all(x["disposition"]=="REVERSIBLE_ESCAPE_CANDIDATE_NOT_CONFIRMED" for x in a if x["candidate_exact_match"]=="true"))
if __name__=="__main__":unittest.main()
