import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlparse,parse_qs
from capture_p436_official_historical_price_volume import capture, normalize_row

class P436OfficialPriceVolumeTests(unittest.TestCase):
    def test_candidate_ohlcv_matches_and_token_is_redacted(self):
        token={"accessToken":"ACCESS_SECRET","refreshToken":"REFRESH_SECRET","salt1":1,"salt2":2,"salt3":3,"salt4":4,"salt5":5,"serverTime":1795651200000}
        def fake(method,url,body=None,headers=None):
            if url.endswith("/api/authenticate/prove"):return 200,{},json.dumps(token).encode()
            if "/api/nots/security?" in url:return 200,{},b'[{"id":396,"symbol":"NMLBBL"},{"id":2896,"symbol":"SMPDA"}]'
            if "/api/nots/market/history/security/396" in url:
                rows=[{"businessDate":"2024-05-19","openPrice":599.6,"highPrice":646.6,"lowPrice":599.6,"closePrice":646.6,"totalTradedQuantity":864,"totalTradedValue":557461.6}]
                return 200,{},json.dumps({"content":rows,"totalElements":1,"totalPages":1}).encode()
            if "/api/nots/market/history/security/2896" in url:
                rows=[{"businessDate":"2024-08-18","openPrice":1078.1,"highPrice":1162.7,"lowPrice":1078.1,"closePrice":1162.7,"totalTradedQuantity":5314,"totalTradedValue":6175193.8}]
                return 200,{},json.dumps({"content":rows,"totalElements":1,"totalPages":1}).encode()
            raise AssertionError(url)
        with tempfile.TemporaryDirectory() as tmp:
            result=capture(tmp,fake,lambda obj,path:("ACCESS_SECRET","REFRESH_SECRET"),"2026-11-26T00:00:00Z",include_recent_controls=False)
            saved="".join(p.read_text(errors="ignore") for p in Path(tmp).glob("*.json"))
        self.assertNotIn("ACCESS_SECRET",saved)
        self.assertNotIn("REFRESH_SECRET",saved)
        for item in result["security_results"]:
            self.assertTrue(item["candidate_all_expected_fields_match"])
            self.assertEqual(item["prior_rows"],0)

    def test_http_error_does_not_create_zero_trade_assertion(self):
        token={"accessToken":"A","refreshToken":"R","salt1":1,"salt2":2,"salt3":3,"salt4":4,"salt5":5,"serverTime":1795651200000}
        def fake(method,url,body=None,headers=None):
            if url.endswith("/api/authenticate/prove"):return 200,{},json.dumps(token).encode()
            if "/api/nots/security?" in url:return 200,{},b'[{"id":396,"symbol":"NMLBBL"},{"id":2896,"symbol":"SMPDA"}]'
            return 403,{"Content-Type":"text/html"},b"forbidden"
        with tempfile.TemporaryDirectory() as tmp:
            result=capture(tmp,fake,lambda obj,path:("A","R"),"2026-11-26T00:00:00Z",include_recent_controls=False)
        self.assertTrue(all(x["status"]=="request_or_schema_failure" for x in result["security_results"]))
        self.assertTrue(all("prior_rows" not in x for x in result["security_results"]))

    def test_out_of_window_dates_are_flagged(self):
        token={"accessToken":"A","refreshToken":"R","salt1":1,"salt2":2,"salt3":3,"salt4":4,"salt5":5,"serverTime":1795651200000}
        def fake(method,url,body=None,headers=None):
            if url.endswith("/api/authenticate/prove"):return 200,{},json.dumps(token).encode()
            if "/api/nots/security?" in url:return 200,{},b'[{"id":396,"symbol":"NMLBBL"},{"id":2896,"symbol":"SMPDA"}]'
            rows=[{"businessDate":"2026-11-26","openPrice":1,"highPrice":1,"lowPrice":1,"closePrice":1,"totalTradedQuantity":1,"totalTradedValue":1}]
            return 200,{},json.dumps({"content":rows}).encode()
        with tempfile.TemporaryDirectory() as tmp:
            result=capture(tmp,fake,lambda obj,path:("A","R"),"2026-11-26T00:00:00Z",include_recent_controls=False)
        self.assertEqual(result["security_results"][0]["date_mismatches"],1)
        self.assertFalse(result["security_results"][0]["candidate_all_expected_fields_match"])

    def test_normalizer_preserves_official_price_volume_fields(self):
        row=normalize_row({"businessDate":"2024-05-19T00:00:00","openPrice":599.6,"highPrice":646.6,"lowPrice":599.6,"closePrice":646.6,"totalTradedQuantity":864,"totalTradedValue":557461.6})
        self.assertEqual(row["date"],"2024-05-19")
        self.assertEqual(row["volume"],864)
        self.assertEqual(row["turnover"],557461.6)

    def test_recent_window_control_confirms_endpoint_reachability(self):
        token={"accessToken":"A","refreshToken":"R","salt1":1,"salt2":2,"salt3":3,"salt4":4,"salt5":5,"serverTime":1795651200000}
        def fake(method,url,body=None,headers=None):
            if url.endswith("/api/authenticate/prove"):return 200,{},json.dumps(token).encode()
            if "/api/nots/security?" in url:return 200,{},b'[{"id":396,"symbol":"NMLBBL"},{"id":2896,"symbol":"SMPDA"}]'
            if url.endswith("/api/nots/nepse-data/market-open"):return 200,{},b'{"id":80,"asOf":"2026-11-26T15:00:00"}'
            if "/api/nots/market/history/security/" in url:
                rows=[{"businessDate":"2026-11-26","openPrice":1,"highPrice":1,"lowPrice":1,"closePrice":1,"totalTradedQuantity":1,"totalTradedValue":1}]
                return 200,{},json.dumps({"content":rows,"totalElements":1,"totalPages":1}).encode()
            return 200,{},b'{"content":[],"totalElements":0,"totalPages":0}'
        with tempfile.TemporaryDirectory() as tmp:
            result=capture(tmp,fake,lambda obj,path:("A","R"),"2026-11-26T00:00:00Z")
        self.assertEqual(len(result["recent_controls"]),2)
        self.assertTrue(all(x["status"]=="captured" and x["row_count"]==1 for x in result["recent_controls"]))

if __name__=="__main__":unittest.main()
