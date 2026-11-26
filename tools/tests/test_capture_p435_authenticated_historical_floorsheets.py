import base64
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from capture_p435_authenticated_historical_floorsheets import (
    WASM_B64, WASM_GIT_BLOB_SHA, git_blob_sha, compute_floor_payload_id,
    capture, token_parser
)

class P435AuthenticatedFloorsheetTests(unittest.TestCase):
    def test_pinned_wasm_blob_hash(self):
        wasm=base64.b64decode(WASM_B64)
        self.assertEqual(git_blob_sha(wasm),WASM_GIT_BLOB_SHA)
        self.assertEqual(len(wasm),750)

    def test_payload_id_is_deterministic(self):
        self.assertEqual(compute_floor_payload_id(5,[10,20,30,40,50],26),
                         (312+5+52)+40*26-30)

    def test_wasm_token_parser_removes_inserted_characters(self):
        salts=[1,2,3,4,5]
        fake={"salt1":salts[0],"salt2":salts[1],"salt3":salts[2],"salt4":salts[3],"salt5":salts[4],
              "accessToken":"A"*120,"refreshToken":"B"*120}
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"css.wasm";path.write_bytes(base64.b64decode(WASM_B64))
            access,refresh=token_parser(fake,path)
        self.assertLess(len(access),120)
        self.assertLess(len(refresh),120)
        self.assertTrue(set(access)<=set("A"))
        self.assertTrue(set(refresh)<=set("B"))

    def test_authenticated_capture_keeps_tokens_out_of_artifacts(self):
        day=int(datetime(2026,11,26,tzinfo=timezone.utc).timestamp()*1000)
        token={"accessToken":"ACCESS_SECRET","refreshToken":"REFRESH_SECRET",
               "salt1":10,"salt2":20,"salt3":30,"salt4":40,"salt5":50,"serverTime":day}
        def fake(method,url,body=None,headers=None):
            if url.endswith("/api/authenticate/prove"):return 200,{"Content-Type":"application/json"},json.dumps(token).encode()
            if url.endswith("/api/nots/nepse-data/market-open"):return 200,{},b'{"id":5,"asOf":"2026-11-26T10:00:00"}'
            if "/api/nots/security?" in url:return 200,{},b'[{"id":100,"symbol":"NMLBBL"},{"id":200,"symbol":"SMPDA"}]'
            query=parse_qs(urlparse(url).query);date=query["businessDate"][0]
            symbol="NMLBBL" if "/100?" in url else "SMPDA"
            qty={"2024-05-19":864,"2024-05-16":0,"2024-08-18":5314,"2024-08-14":0}[date]
            content=[] if qty==0 else [{"contractId":f"{date.replace('-','')}1","businessDate":date,"contractQuantity":qty,"contractRate":100,"contractAmount":qty*100}]
            response={"floorsheets":{"content":content,"totalElements":len(content),"totalPages":1 if content else 0}}
            return 200,{"Content-Type":"application/json"},json.dumps(response).encode()
        def fake_parser(obj,path):return ("ACCESS_SECRET","REFRESH_SECRET")
        with tempfile.TemporaryDirectory() as tmp:
            result=capture(tmp,fake,fake_parser,"2026-11-26T00:00:00Z",include_controls=False)
            saved="".join(p.read_text(errors="ignore") for p in Path(tmp).glob("*.json"))
            self.assertNotIn("ACCESS_SECRET",saved)
            self.assertNotIn("REFRESH_SECRET",saved)
            self.assertEqual(len(result["floor_results"]),4)
            self.assertTrue(result["floor_results"][0]["evidence_gate_pass"])
            self.assertTrue(result["floor_results"][2]["evidence_gate_pass"])

    def test_missing_total_elements_fails_evidence_gate(self):
        day=int(datetime(2026,11,26,tzinfo=timezone.utc).timestamp()*1000)
        token={"accessToken":"A","refreshToken":"R","salt1":10,"salt2":20,"salt3":30,"salt4":40,"salt5":50,"serverTime":day}
        def fake(method,url,body=None,headers=None):
            if url.endswith("/api/authenticate/prove"):return 200,{},json.dumps(token).encode()
            if url.endswith("/api/nots/nepse-data/market-open"):return 200,{},b'{"id":5}'
            if "/api/nots/security?" in url:return 200,{},b'[{"id":100,"symbol":"NMLBBL"},{"id":200,"symbol":"SMPDA"}]'
            date=parse_qs(urlparse(url).query)["businessDate"][0]
            content=[{"contractId":"1","businessDate":date,"contractQuantity":864,"contractRate":100,"contractAmount":86400}] if date=="2024-05-19" else []
            return 200,{},json.dumps({"floorsheets":{"content":content,"totalPages":1}}).encode()
        with tempfile.TemporaryDirectory() as tmp:
            result=capture(tmp,fake,lambda obj,path:("A","R"),"2026-11-26T00:00:00Z",include_controls=False)
            self.assertFalse(result["floor_results"][0]["evidence_gate_pass"])

    def test_403_retries_utc_day_and_uses_source_clients_page_zero_shape(self):
        from datetime import datetime, timezone
        server_time=int(datetime(2026,11,26,18,30,tzinfo=timezone.utc).timestamp()*1000)
        token={"accessToken":"A","refreshToken":"R","salt1":10,"salt2":20,"salt3":30,"salt4":40,"salt5":50,"serverTime":server_time}
        post_calls=[]
        def fake(method,url,body=None,headers=None):
            if url.endswith("/api/authenticate/prove"):return 200,{},json.dumps(token).encode()
            if url.endswith("/api/nots/nepse-data/market-open"):return 200,{},b'{"id":5}'
            if "/api/nots/security?" in url:return 200,{},b'[{"id":100,"symbol":"NMLBBL"},{"id":200,"symbol":"SMPDA"}]'
            if method=="POST":
                post_calls.append((url,body))
                if len(post_calls)%2==1:return 403,{"Content-Type":"text/html"},b"forbidden"
                date=parse_qs(urlparse(url).query)["businessDate"][0]
                qty={"2024-05-19":864,"2024-05-16":0,"2024-08-18":5314,"2024-08-14":0}[date]
                content=[] if qty==0 else [{"contractId":date.replace("-",""),"businessDate":date,"contractQuantity":qty,"contractRate":100,"contractAmount":qty*100}]
                return 200,{},json.dumps({"floorsheets":{"content":content,"totalElements":len(content),"totalPages":1 if content else 0}}).encode()
            raise AssertionError(url)
        with tempfile.TemporaryDirectory() as tmp:
            result=capture(tmp,fake,lambda obj,path:("A","R"),"2026-11-26T00:00:00Z")
        self.assertEqual(len(post_calls),8)
        self.assertTrue(all("page=0" not in url for url,_ in post_calls))
        self.assertTrue(all("id" in body for _,body in post_calls))
        self.assertEqual(result["floor_results"][0]["pages"][0]["payload_day_used"],26)

    def test_current_session_control_routes_are_probed(self):
        day=int(datetime(2026,11,26,tzinfo=timezone.utc).timestamp()*1000)
        token={"accessToken":"A","refreshToken":"R","salt1":10,"salt2":20,"salt3":30,"salt4":40,"salt5":50,"serverTime":day}
        def fake(method,url,body=None,headers=None):
            if url.endswith("/api/authenticate/prove"):return 200,{},json.dumps(token).encode()
            if url.endswith("/api/nots/nepse-data/market-open"):return 200,{},b'{"id":5,"asOf":"2026-11-26T15:00:00"}'
            if "/api/nots/security?" in url:return 200,{},b'[{"id":100,"symbol":"NMLBBL"},{"id":200,"symbol":"SMPDA"}]'
            if method=="POST":
                if "/api/nots/nepse-data/floorsheet" in url or "businessDate=2026-11-26" in url:
                    return 200,{},b'{"floorsheets":{"content":[],"totalElements":0,"totalPages":0}}'
                date=parse_qs(urlparse(url).query)["businessDate"][0]
                qty={"2024-05-19":864,"2024-05-16":0,"2024-08-18":5314,"2024-08-14":0}[date]
                content=[] if qty==0 else [{"contractId":date.replace("-",""),"businessDate":date,"contractQuantity":qty,"contractRate":100,"contractAmount":qty*100}]
                return 200,{},json.dumps({"floorsheets":{"content":content,"totalElements":len(content),"totalPages":1 if content else 0}}).encode()
            raise AssertionError(url)
        with tempfile.TemporaryDirectory() as tmp:
            result=capture(tmp,fake,lambda obj,path:("A","R"),"2026-11-26T00:00:00Z")
        self.assertEqual(len(result["control_results"]),3)
        self.assertTrue(all(x["status"]=="page0_captured" for x in result["control_results"]))

if __name__=="__main__":unittest.main()
