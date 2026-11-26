import gzip
import hashlib
import tempfile
import unittest
from pathlib import Path
from capture_p433_first_trade_floorsheets import capture, validate_rows

class P433CaptureTests(unittest.TestCase):
    def setUp(self):
        self.raw=b"contract_no,calculation_date,time,stock_symbol,sector,buyer,seller,quantity,rate,amount,id\n20240519001,2024-05-19,,NMLBBL,Bank,1,2,10,100,1000,9001\n"
        self.compressed=gzip.compress(self.raw,mtime=0)
    def test_valid_target_contract_is_counted_and_hashed(self):
        with tempfile.TemporaryDirectory() as tmp:
            report=capture(tmp,lambda url:(200,{"Content-Type":"application/gzip"},self.compressed),"2026-11-26T00:00:00Z",metadata={})
            rec=report["records"][0]
            self.assertEqual(rec["capture_status"],"captured")
            self.assertEqual(rec["validation"]["target_symbol_contracts"],1)
            self.assertEqual(rec["compressed_sha256"],hashlib.sha256(self.compressed).hexdigest())
            self.assertEqual((Path(tmp)/"floorsheet_2024-05-19.csv").read_bytes(),self.raw)
    def test_duplicate_contract_number_within_symbol_fails(self):
        raw=b"contract_no,calculation_date,stock_symbol,quantity,rate,amount,id\n1,2024-05-19,NMLBBL,10,100,1000,11\n1,2024-05-19,NMLBBL,10,100,1000,12\n"
        result=validate_rows(raw,"NMLBBL","2024-05-19")
        self.assertEqual(result["duplicate_contract_numbers_within_symbol"],1)
        self.assertEqual(result["status"],"validation_failed")
    def test_cross_symbol_contract_number_reuse_is_reported_not_misclassified(self):
        raw=b"contract_no,calculation_date,stock_symbol,quantity,rate,amount,id\n1,2024-05-19,NMLBBL,10,100,1000,11\n1,2024-05-19,SMPDA,10,100,1000,12\n"
        result=validate_rows(raw,"NMLBBL","2024-05-19")
        self.assertEqual(result["duplicate_contract_numbers_within_symbol"],0)
        self.assertEqual(result["cross_symbol_contract_number_collisions"],1)
        self.assertEqual(result["unique_record_ids"],2)
        self.assertEqual(result["status"],"validated")
    def test_wrong_dates_fail_validation(self):
        raw=b"contract_no,calculation_date,stock_symbol,quantity,rate,amount,id\n1,2024-05-18,NMLBBL,10,100,1000,11\n"
        result=validate_rows(raw,"NMLBBL","2024-05-19")
        self.assertEqual(result["date_mismatches"],1)
        self.assertEqual(result["status"],"validation_failed")
    def test_non_gzip_response_is_not_saved(self):
        with tempfile.TemporaryDirectory() as tmp:
            report=capture(tmp,lambda url:(200,{"Content-Type":"text/csv"},b"<html>blocked</html>"),"2026-11-26T00:00:00Z",metadata={})
            self.assertTrue(all(r["capture_status"]=="non_gzip_response" for r in report["records"]))
            self.assertFalse(list(Path(tmp).glob("*.csv")))
    def test_missing_archive_is_unknown_not_no_trade(self):
        def fail(url):raise OSError("not found")
        with tempfile.TemporaryDirectory() as tmp:
            report=capture(tmp,fail,"2026-11-26T00:00:00Z",metadata={})
            self.assertTrue(all(r["capture_status"]=="unavailable" for r in report["records"]))
            self.assertIn("remain UNKNOWN",report["interpretation"])
    def test_lfs_hash_mismatch_is_not_promoted(self):
        with tempfile.TemporaryDirectory() as tmp:
            metadata={"floorsheet/2024-05-19.csv.gz":{"size":len(self.compressed),"lfs":{"oid":"0"*64}}}
            report=capture(tmp,lambda url:(200,{},self.compressed),"2026-11-26T00:00:00Z",metadata=metadata)
            self.assertEqual(report["records"][0]["capture_status"],"integrity_failed")

if __name__=="__main__":unittest.main()
