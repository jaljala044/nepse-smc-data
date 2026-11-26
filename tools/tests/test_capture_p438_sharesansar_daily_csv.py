import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from capture_p438_sharesansar_daily_csv import git_blob_sha, audit_csv, capture

HEADER="S.No,Symbol,Conf.,Open,High,Low,Close,VWAP,Vol,Prev. Close,Turnover,Trans.,Diff,Range,Diff %,Range %,VWAP %,120 Days,180 Days,52 Weeks High,52 Weeks Low"
def csvrow(n,symbol,open_,high,low,close,volume,turnover,trans):
 return f'{n},{symbol},-,{open_},{high},{low},{close},{close},{volume},0,{turnover},{trans},0,0,0,0,0,0,0,0,0'
class P438ShareSansarTests(unittest.TestCase):
    def test_git_blob_hash_known_vector(self):
        self.assertEqual(git_blob_sha(b"hello\n"),"ce013625030ba8dba906f756967f9e9ca394464a")

    def test_candidate_row_matches_floorsheet_values(self):
        raw=(HEADER+"\n"+csvrow(1,"NMLBBL","599.60","646.60","599.60","646.60","864.00","557461.60","15")+"\n").encode()
        rec={"date":"2024-05-19","target_symbol":"NMLBBL","target_role":"candidate","expected_rows":1}
        result=audit_csv(raw,rec)
        self.assertEqual(result["target_row_count"],1)
        self.assertTrue(result["candidate_fields_match"])
        self.assertTrue(result["expected_candidate_parity"]["floorsheet_row_count"])

    def test_prior_absence_is_secondary_only_and_market_table_nonempty(self):
        raw=(HEADER+"\n"+csvrow(1,"ACLBSL","882.10","955.00","866.00","945.00","37972.00","35309985.60","370")+"\n").encode()
        rec={"date":"2024-05-16","target_symbol":"NMLBBL","target_role":"prior","expected_rows":1}
        result=audit_csv(raw,rec)
        self.assertTrue(result["target_absent_in_secondary_table"])
        self.assertEqual(result["row_count"],1)
        self.assertNotIn("NO_TRADE",str(result))

    def test_capture_verifies_pinned_size_and_git_blob(self):
        raw=b"source README: ShareSansar today's-share-price page; market was closed on holidays."
        record={"name":"README.md","path":"README.md","size_bytes":len(raw),"git_blob_sha":git_blob_sha(raw),"kind":"readme"}
        with patch("capture_p438_sharesansar_daily_csv.FILES",[record]):
            with tempfile.TemporaryDirectory() as tmp:
                result=capture(tmp,lambda url:(200,raw),"2026-11-26T00:00:00Z")
                self.assertEqual(result["files"][0]["status"],"CAPTURED")
                self.assertTrue(result["source_capture_policy_verified"])
                self.assertEqual((Path(tmp)/"README.md").read_bytes(),raw)

    def test_duplicate_symbols_are_detected(self):
        raw=(HEADER+"\n"+csvrow(1,"NMLBBL","1","1","1","1","1","1","1")+"\n"+csvrow(2,"NMLBBL","1","1","1","1","1","1","1")+"\n").encode()
        rec={"date":"2024-05-19","target_symbol":"NMLBBL","target_role":"candidate","expected_rows":2}
        result=audit_csv(raw,rec)
        self.assertEqual(result["duplicate_symbols"],["NMLBBL"])
        self.assertEqual(result["target_row_count"],2)

if __name__=="__main__":unittest.main()
