import json
import tempfile
import unittest
from pathlib import Path
from capture_p436_official_eod_history import capture, find_rows, find_total

class P436OfficialEodHistoryTests(unittest.TestCase):
    def test_row_collection_and_pagination_metadata_are_discovered(self):
        obj={"securityHistory":{"content":[{"businessDate":"2024-05-19"}],"totalElements":1,"totalPages":1}}
        rows,path=find_rows(obj)
        self.assertEqual(len(rows),1)
        self.assertEqual(path,"$.securityHistory.content")
        self.assertEqual(find_total(obj),(1,1,"$.securityHistory"))

    def test_authenticated_capture_preserves_raw_payload_and_exact_date(self):
        token={"accessToken":"SECRET","refreshToken":"REFRESH","salt1":1,"salt2":2,"salt3":3,"salt4":4,"salt5":5,"serverTime":1}
        def fake(method,url,body=None,headers=None):
            if url.endswith("/api/authenticate/prove"):
                return 200,{},json.dumps(token).encode()
            if url.endswith("/api/nots/security?nonDelisted=true"):
                return 200,{},b'[{"id":396,"symbol":"NMLBBL"},{"id":2896,"symbol":"SMPDA"}]'
            date=url.split("startDate=")[1].split("&")[0]
            symbol="NMLBBL" if "/396?" in url else "SMPDA"
            volume={"2024-05-19":864,"2024-05-16":0,"2024-08-18":5314,"2024-08-14":0}[date]
            rows=[] if volume==0 else [{
                "businessDate":date,"symbol":symbol,"totalTradedQuantity":volume,
                "openPrice":10,"highPrice":11,"lowPrice":9,"closePrice":10
            }]
            payload={"securityHistory":{"content":rows,"totalElements":len(rows),"totalPages":1}}
            return 200,{"Content-Type":"application/json"},json.dumps(payload).encode()
        with tempfile.TemporaryDirectory() as tmp:
            result=capture(tmp,fake,lambda obj,path:("AUTH_SECRET","REFRESH_SECRET"),"2026-11-26T00:00:00Z")
            self.assertEqual(len(result["results"]),4)
            self.assertTrue(result["results"][0]["evidence_gate_pass"])
            self.assertTrue(result["results"][1]["pagination_complete"])
            self.assertTrue((Path(tmp)/"NMLBBL_2024-05-19_page_0.json").exists())
            report=(Path(tmp)/"capture_report.json").read_text()
            self.assertNotIn("AUTH_SECRET",report)
            self.assertNotIn("REFRESH_SECRET",report)

    def test_wrong_date_or_missing_pagination_never_passes_gate(self):
        token={"accessToken":"SECRET","refreshToken":"REFRESH","salt1":1,"salt2":2,"salt3":3,"salt4":4,"salt5":5,"serverTime":1}
        def fake(method,url,body=None,headers=None):
            if url.endswith("/api/authenticate/prove"):return 200,{},json.dumps(token).encode()
            if url.endswith("/api/nots/security?nonDelisted=true"):return 200,{},b'[{"id":396,"symbol":"NMLBBL"},{"id":2896,"symbol":"SMPDA"}]'
            date=url.split("startDate=")[1].split("&")[0]
            wrong="2024-05-18" if date=="2024-05-19" else date
            rows=[{"businessDate":wrong,"symbol":"NMLBBL","totalTradedQuantity":864,"openPrice":10,"highPrice":11,"lowPrice":9,"closePrice":10}]
            return 200,{},json.dumps({"securityHistory":{"content":rows}}).encode()
        with tempfile.TemporaryDirectory() as tmp:
            result=capture(tmp,fake,lambda obj,path:("A","R"),"2026-11-26T00:00:00Z")
        self.assertFalse(result["results"][0]["evidence_gate_pass"])
        self.assertFalse(result["results"][0]["pagination_complete"])

if __name__=="__main__":unittest.main()
