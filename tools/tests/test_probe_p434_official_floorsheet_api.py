import json
import tempfile
import unittest
from pathlib import Path
from probe_p434_official_floorsheet_api import probe

class P434ProbeTests(unittest.TestCase):
    def test_token_values_are_never_persisted(self):
        def fake(method,url,body=None):
            if url.endswith("/api/authenticate/prove"):
                return 200,{"Content-Type":"application/json"},json.dumps({"accessToken":"SECRET-A","refreshToken":"SECRET-R","salt1":"123","serverTime":1234}).encode()
            if url.endswith("/api/nots/nepse-data/market-open"):
                return 200,{"Content-Type":"application/json"},b'{"id":7,"asOf":"2024-01-01T00:00:00"}'
            if "/api/nots/security?" in url:
                return 401,{"Content-Type":"application/json"},b'{"message":"unauthorized"}'
            return 401,{"Content-Type":"application/json"},b'{"message":"unauthorized"}'
        with tempfile.TemporaryDirectory() as tmp:
            result=probe(tmp,fake,"2026-11-26T00:00:00Z")
            token=next(x for x in result["records"] if x["name"]=="token_prove")
            self.assertFalse(token["body_saved"])
            self.assertTrue(token["token_fields_present"]["accessToken"])
            self.assertFalse(any("SECRET" in p.read_text(errors="ignore") for p in Path(tmp).glob("*")))

    def test_security_id_failure_skips_company_requests(self):
        calls=[]
        def fake(method,url,body=None):
            calls.append((method,url,body))
            if url.endswith("/api/nots/nepse-data/market-open"):return 401,{},b""
            if "/api/nots/security?" in url:return 403,{},b""
            if url.endswith("/api/authenticate/prove"):return 403,{},b""
            raise AssertionError("company request should not be sent without security id")
        with tempfile.TemporaryDirectory() as tmp:
            result=probe(tmp,fake,"2026-11-26T00:00:00Z")
            skipped=[x for x in result["records"] if x.get("status")=="skipped_security_id_unavailable"]
            self.assertEqual(len(skipped),4)

    def test_page_zero_response_records_pagination_metadata(self):
        def fake(method,url,body=None):
            if url.endswith("/api/nots/nepse-data/market-open"):return 200,{},b'{"id":5}'
            if "/api/nots/security?" in url:return 200,{},b'[{"id":1001,"symbol":"NMLBBL"},{"id":1002,"symbol":"SMPDA"}]'
            if url.endswith("/api/authenticate/prove"):return 401,{},b'{}'
            if method=="POST":return 200,{},b'{"floorsheets":{"content":[{"contractId":1}],"totalElements":1,"totalPages":1}}'
            raise AssertionError(url)
        with tempfile.TemporaryDirectory() as tmp:
            result=probe(tmp,fake,"2026-11-26T00:00:00Z")
            pages=[x for x in result["records"] if x.get("status")=="page0_captured"]
            self.assertEqual(len(pages),4)
            self.assertEqual(pages[0]["response_summary"]["total_elements"],1)

if __name__=="__main__":unittest.main()
