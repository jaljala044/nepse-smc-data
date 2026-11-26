import json
import tempfile
import unittest
from pathlib import Path
from capture_p436_official_eod_history import capture, find_rows, find_total

class P436OfficialEodHistoryTests(unittest.TestCase):
    def test_row_collection_and_pagination_metadata(self):
        obj={"content":[{"businessDate":"2024-05-19"}],"totalElements":1,"totalPages":1}
        rows,path=find_rows(obj)
        self.assertEqual(len(rows),1)
        self.assertEqual(path,"$.content")
        self.assertEqual(find_total(obj),(1,1,"$"))

    def test_month_window_finds_candidate_and_prior_rows(self):
        token={"accessToken":"SECRET","refreshToken":"REFRESH","salt1":1,"salt2":2,"salt3":3,"salt4":4,"salt5":5,"serverTime":1}
        def fake(method,url,body=None,headers=None):
            if url.endswith("/api/authenticate/prove"):return 200,{},json.dumps(token).encode()
            if url.endswith("/api/nots/security?nonDelisted=true"):return 200,{},b'[{"id":396,"symbol":"NMLBBL"},{"id":2896,"symbol":"SMPDA"}]'
            if "startDate=2024-05-01" in url:
                rows=[
                    {"businessDate":"2024-05-19","symbol":"NMLBBL","totalTradedQuantity":864,"openPrice":599.6,"highPrice":646.6,"lowPrice":599.6,"closePrice":646.6},
                ]
            elif "startDate=2024-08-01" in url:
                rows=[
                    {"businessDate":"2024-08-18","symbol":"SMPDA","totalTradedQuantity":5314,"openPrice":1078.1,"highPrice":1162.7,"lowPrice":1078.1,"closePrice":1162.7},
                ]
            else:
                rows=[{"businessDate":"2026-11-25","symbol":"NMLBBL","totalTradedQuantity":100,"openPrice":10,"highPrice":11,"lowPrice":9,"closePrice":10}]
            payload={"content":rows,"totalElements":len(rows),"totalPages":1}
            return 200,{"Content-Type":"application/json"},json.dumps(payload).encode()
        with tempfile.TemporaryDirectory() as tmp:
            result=capture(tmp,fake,lambda obj,path:("AUTH_SECRET","REFRESH_SECRET"),"2026-11-26T00:00:00Z")
            self.assertEqual(len(result["windows"]),4)
            candidate=next(x for x in result["target_results"] if x["business_date"]=="2024-05-19")
            prior=next(x for x in result["target_results"] if x["business_date"]=="2024-05-16")
            self.assertTrue(candidate["evidence_gate_pass"])\n            self.assertEqual(result["windows"][2]["start_date"],"2025-11-26")
            self.assertEqual(prior["status"],"no_record_returned")
            self.assertFalse(prior["evidence_gate_pass"])
            self.assertTrue((Path(tmp)/"NMLBBL_2024-05-01_2024-05-31_page_0.json").exists())
            report=(Path(tmp)/"capture_report.json").read_text()
            self.assertNotIn("AUTH_SECRET",report)
            self.assertNotIn("REFRESH_SECRET",report)

    def test_missing_pagination_or_wrong_date_fails_closed(self):
        token={"accessToken":"SECRET","refreshToken":"REFRESH","salt1":1,"salt2":2,"salt3":3,"salt4":4,"salt5":5,"serverTime":1}
        def fake(method,url,body=None,headers=None):
            if url.endswith("/api/authenticate/prove"):return 200,{},json.dumps(token).encode()
            if url.endswith("/api/nots/security?nonDelisted=true"):return 200,{},b'[{"id":396,"symbol":"NMLBBL"},{"id":2896,"symbol":"SMPDA"}]'
            if "startDate=2024-05-01" in url:
                rows=[{"businessDate":"2024-05-18","symbol":"NMLBBL","totalTradedQuantity":864,"openPrice":10,"highPrice":11,"lowPrice":9,"closePrice":10}]
                return 200,{},json.dumps({"content":rows}).encode()
            return 200,{},json.dumps({"content":[],"totalElements":0,"totalPages":0}).encode()
        with tempfile.TemporaryDirectory() as tmp:
            result=capture(tmp,fake,lambda obj,path:("A","R"),"2026-11-26T00:00:00Z")
        candidate=next(x for x in result["target_results"] if x["business_date"]=="2024-05-19")
        self.assertFalse(candidate["evidence_gate_pass"])
        self.assertFalse(candidate["window_pagination_complete"])

if __name__=="__main__":unittest.main()
