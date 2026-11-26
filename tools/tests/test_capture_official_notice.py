import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from capture_official_notice import capture_notice


class FakeResponse:
    status = 200
    headers = {"Content-Type": "application/pdf", "Content-Length": "5"}

    def __init__(self, body=b"PDF!!", url="https://www.nepalstock.com.np/notice.pdf"):
        self.body = body
        self.url = url

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.body

    def geturl(self):
        return self.url


class CaptureOfficialNoticeTests(unittest.TestCase):
    def test_captures_raw_bytes_and_hash_without_calendar_promotion(self):
        with tempfile.TemporaryDirectory() as tmp, patch("capture_official_notice.urlopen", return_value=FakeResponse()):
            result = capture_notice("https://www.nepalstock.com.np/notice.pdf", "nepse-2026-01", tmp)
            self.assertEqual(result["raw_evidence_sha256"], hashlib.sha256(b"PDF!!").hexdigest())
            self.assertEqual(Path(result["raw_evidence_path"]).read_bytes(), b"PDF!!")
            self.assertFalse(result["calendar_populated"])
            self.assertTrue(Path(tmp, f"nepse-2026-01-{result['raw_evidence_sha256']}.json").exists())

    def test_non_official_url_rejected(self):
        with self.assertRaisesRegex(ValueError, "approved NEPSE or SEBON"):
            capture_notice("https://example.com/notice.pdf", "x", tempfile.gettempdir())

    def test_redirect_to_non_official_host_rejected(self):
        with tempfile.TemporaryDirectory() as tmp, patch(
            "capture_official_notice.urlopen",
            return_value=FakeResponse(url="https://example.com/redirect")
        ):
            with self.assertRaisesRegex(ValueError, "redirect target"):
                capture_notice("https://www.nepalstock.com.np/notice.pdf", "x", tmp)

    def test_publication_timestamp_requires_timezone(self):
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            capture_notice("https://www.nepalstock.com.np/notice.pdf", "x",
                           tempfile.gettempdir(), "2026-01-01T10:00:00")

    def test_empty_response_rejected(self):
        with tempfile.TemporaryDirectory() as tmp, patch(
            "capture_official_notice.urlopen", return_value=FakeResponse(body=b"")
        ):
            with self.assertRaisesRegex(ValueError, "response is empty"):
                capture_notice("https://www.nepalstock.com.np/notice.pdf", "x", tmp)


if __name__ == "__main__":
    unittest.main()
