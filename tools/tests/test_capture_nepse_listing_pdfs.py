import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from capture_nepse_listing_pdfs import capture

class OfficialListingPdfCaptureTests(unittest.TestCase):
    def test_pdf_is_preserved_and_hashed(self):
        body=b"%PDF-1.7\nmock official notice"
        with tempfile.TemporaryDirectory() as tmp:
            report=capture(tmp, lambda url:(200,{"Content-Type":"application/pdf"},body), "2026-11-26T00:00:00Z")
            self.assertEqual([d["capture_status"] for d in report["documents"]],["captured","captured"])
            for doc in report["documents"]:
                path=Path(tmp)/doc["filename"]
                self.assertEqual(path.read_bytes(),body)
                self.assertEqual(doc["response_sha256"],hashlib.sha256(body).hexdigest())
            saved=json.loads((Path(tmp)/"capture_report.json").read_text())
            self.assertEqual(saved["first_trade_disposition"]["NMLBBL"]["status"],"UNKNOWN")

    def test_non_pdf_response_is_not_promoted(self):
        with tempfile.TemporaryDirectory() as tmp:
            report=capture(tmp, lambda url:(200,{"Content-Type":"text/html"},b"<html>blocked</html>"), "2026-11-26T00:00:00Z")
            self.assertEqual([d["capture_status"] for d in report["documents"]],["non_pdf_response","non_pdf_response"])
            self.assertFalse(any(Path(tmp).glob("*.pdf")))

    def test_transport_failure_is_recorded(self):
        def fail(url):
            raise OSError("blocked by upstream")
        with tempfile.TemporaryDirectory() as tmp:
            report=capture(tmp, fail, "2026-11-26T00:00:00Z")
            self.assertEqual([d["capture_status"] for d in report["documents"]],["unavailable","unavailable"])
            self.assertTrue(all("blocked by upstream" in d["error"] for d in report["documents"]))

if __name__=="__main__": unittest.main()
