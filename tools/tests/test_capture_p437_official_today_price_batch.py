import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from capture_p437_official_today_price_batch import run_batch

class P437BatchTests(unittest.TestCase):
    def test_batch_preserves_all_four_date_results(self):
        def fake(command,**kwargs):
            out=Path(command[7]);out.mkdir(parents=True,exist_ok=True)
            date=command[3];symbol=command[5]
            manifest={"status":"TARGET_ROW_FOUND","returned_business_dates":[date],"target_row_count":1,"symbol_row_count":1,"total_pages":1,"upstream_total_elements":1,"pagination_row_count_matches":True,"captured_pages":[],"target_row":{"symbol":symbol,"businessDate":date}}
            (out/"capture_manifest.json").write_text(json.dumps(manifest))
            return SimpleNamespace(returncode=0,stdout="",stderr="")
        with tempfile.TemporaryDirectory() as tmp:
            result=run_batch(tmp,fake,"2026-11-26T00:00:00Z")
        self.assertEqual(len(result["records"]),4)
        self.assertTrue(all(x["status"]=="TARGET_ROW_FOUND" for x in result["records"]))
        self.assertTrue(all(x["returned_business_dates"]==[x["business_date"]] for x in result["records"]))

    def test_http_failure_is_recorded_not_called_no_trade(self):
        def fake(command,**kwargs):
            out=Path(command[7]);out.mkdir(parents=True,exist_ok=True)
            (out/"capture_error.json").write_text(json.dumps({"http_status":403,"sha256":"abc"}))
            return SimpleNamespace(returncode=1,stdout="",stderr="forbidden")
        with tempfile.TemporaryDirectory() as tmp:
            result=run_batch(tmp,fake,"2026-11-26T00:00:00Z")
        self.assertTrue(all(x["status"]=="CAPTURE_ERROR" for x in result["records"]))
        self.assertTrue(all("NO_TRADE" not in x["status"] for x in result["records"]))

if __name__=="__main__":unittest.main()
