import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from capture_p433_first_trade_floorsheets import capture, validate_rows

class P433CaptureTests(unittest.TestCase):
    def test_valid_target_contract_is_counted_and_hashed(self):
        raw=b"contract_no,calculation_date,stock_symbol,quantity,rate,amount\n20240519001,2024-05-19,NMLBBL,10,100,1000\n"
        with tempfile.TemporaryDirectory() as tmp:
            report=capture(tmp,lambda url:(200,{"Content-Type":"text/csv"},raw),"2026-11-26T00:00:00Z")
            rec=report["records"][0]
            self.assertEqual(rec["capture_status"],"captured")
            self.assertEqual(rec["validation"]["target_symbol_contracts"],1)
            self.assertEqual(rec["response_sha256"],hashlib.sha256(raw).hexdigest())
            self.assertEqual((Path(tmp)/"floorsheet_2024-05-19.csv").read_bytes(),raw)

    def test_duplicate_contracts_and_wrong_dates_fail_validation(self):
        raw=b"contract_no,calculation_date,stock_symbol,quantity,rate,amount\n1,2024-05-18,NMLBBL,10,100,1000\n1,2024-05-19,NMLBBL,10,100,1000\n"
        result=validate_rows(raw,"NMLBBL","2024-05-19")
        self.assertEqual(result["duplicate_contract_ids"],1)
        self.assertEqual(result["date_mismatches"],1)
        self.assertEqual(result["status"],"validation_failed")

    def test_non_csv_html_is_not_saved(self):
        with tempfile.TemporaryDirectory() as tmp:
            report=capture(tmp,lambda url:(200,{"Content-Type":"text/html"},b"<html>blocked</html>"),"2026-11-26T00:00:00Z")
            self.assertTrue(all(r["capture_status"]=="non_csv_response" for r in report["records"]))
            self.assertFalse(list(Path(tmp).glob("*.csv")))

    def test_missing_archive_is_unknown_not_no_trade(self):
        def fail(url): raise OSError("not found")
        with tempfile.TemporaryDirectory() as tmp:
            report=capture(tmp,fail,"2026-11-26T00:00:00Z")
            self.assertTrue(all(r["capture_status"]=="unavailable" for r in report["records"]))
            self.assertIn("remain UNKNOWN",report["interpretation"])

if __name__=="__main__": unittest.main()
