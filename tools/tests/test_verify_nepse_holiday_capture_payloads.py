import hashlib
import json
import unittest
from verify_nepse_holiday_capture_payloads import verify, git_blob_sha

class HolidayPayloadVerificationTests(unittest.TestCase):
    def setUp(self):
        self.body = json.dumps([{"holidayDate":"2025-01-01","holidayDescription":"New Year"}]).encode()
        self.sha256 = hashlib.sha256(self.body).hexdigest()
        self.report = {
            "source_url":"https://nepalstock.com.np/api/nots/holiday/list?year=2025",
            "requested_year":2025,"http_status":200,"parsed_record_count":1,
            "response_bytes":len(self.body),"response_sha256":self.sha256
        }
        self.payloads = {
            "SHA256SUMS":f"{self.sha256}  response-body.bin\n".encode(),
            "capture-report.json":json.dumps(self.report).encode(),
            "parsed-response.json":self.body,
            "response-body.bin":self.body,
            "response-headers.json":b'{"content-type":"application/json"}',
            "source-url.txt":self.report["source_url"].encode()+b"\n"
        }
        self.manifest = {"annual_captures":[{
            "year":2025,"files":[
                {"name":name,"size_bytes":len(data),"git_blob_sha":git_blob_sha(data),"url":f"https://example.test/{name}"}
                for name,data in self.payloads.items()
            ]
        }]}

    def test_valid_payloads_pass(self):
        result=verify(self.manifest, lambda url:self.payloads[url.rsplit("/",1)[1]])
        self.assertEqual(result,{"checked_files":6,"errors":[]})

    def test_modified_payload_fails_blob_hash(self):
        changed=dict(self.payloads)
        changed["response-body.bin"]=b"[]"
        result=verify(self.manifest, lambda url:changed[url.rsplit("/",1)[1]])
        self.assertTrue(any("Git blob SHA mismatch" in e for e in result["errors"]))

    def test_raw_and_parsed_json_must_match(self):
        changed=dict(self.payloads)
        changed["parsed-response.json"]=b"[]"
        # Update the manifest hash to isolate the JSON-parity rule.
        rec=next(f for f in self.manifest["annual_captures"][0]["files"] if f["name"]=="parsed-response.json")
        rec["size_bytes"]=2
        rec["git_blob_sha"]=git_blob_sha(b"[]")
        result=verify(self.manifest, lambda url:changed[url.rsplit("/",1)[1]])
        self.assertTrue(any("differs from raw response body" in e for e in result["errors"]))

    def test_report_count_must_match(self):
        changed=dict(self.payloads)
        report=dict(self.report); report["parsed_record_count"]=2
        changed["capture-report.json"]=json.dumps(report).encode()
        rec=next(f for f in self.manifest["annual_captures"][0]["files"] if f["name"]=="capture-report.json")
        rec["size_bytes"]=len(changed["capture-report.json"])
        rec["git_blob_sha"]=git_blob_sha(changed["capture-report.json"])
        result=verify(self.manifest, lambda url:changed[url.rsplit("/",1)[1]])
        self.assertTrue(any("parsed_record_count mismatch" in e for e in result["errors"]))

if __name__=="__main__": unittest.main()
