import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from scanner_inputs import retrieve_drive_quarantine as d

class DriveRetrievalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name) / "overlay.csv"
        self.response = MagicMock()
        self.response.status_code = 200
        self.response.__enter__.return_value = self.response
        self.response.iter_content.return_value = [b"abc"]
        self.session = MagicMock()
        self.session.__enter__.return_value = self.session
        self.session.get.return_value = self.response
        for p in (patch("google.auth.default",return_value=(object(),None)),patch("google.auth.transport.requests.AuthorizedSession",return_value=self.session),patch.object(d,"EXPECTED_BYTES",3),patch.object(d,"load_holds",return_value={("ABC","2026-01-01"):"HOLD"})):
            p.start()
            self.addCleanup(p.stop)
    def test_valid_retrieval(self):
        d.retrieve(self.out)
        self.assertEqual(self.out.read_bytes(),b"abc")
        self.assertFalse(self.session.get.call_args.kwargs["allow_redirects"])
    def test_http_denial(self):
        self.response.status_code=403
        with self.assertRaises(RuntimeError):
            d.retrieve(self.out)
        self.assertEqual(list(self.out.parent.iterdir()),[])
    def test_truncated(self):
        self.response.iter_content.return_value=[b"a"]
        with self.assertRaises(ValueError):
            d.retrieve(self.out)
        self.assertEqual(list(self.out.parent.iterdir()),[])
    def test_oversized(self):
        self.response.iter_content.return_value=[b"abcd"]
        with self.assertRaises(ValueError):
            d.retrieve(self.out)
        self.assertEqual(list(self.out.parent.iterdir()),[])
    def test_invalid_overlay(self):
        with patch.object(d,"load_holds",side_effect=ValueError("digest mismatch")):
            with self.assertRaises(ValueError):
                d.retrieve(self.out)
        self.assertEqual(list(self.out.parent.iterdir()),[])
    def test_no_overwrite(self):
        self.out.write_bytes(b"original")
        with self.assertRaises(FileExistsError):
            d.retrieve(self.out)
        self.assertEqual(self.out.read_bytes(),b"original")
    def test_missing_credentials(self):
        with patch("google.auth.default",side_effect=RuntimeError("missing credentials")):
            with self.assertRaises(RuntimeError):
                d.retrieve(self.out)
        self.assertFalse(self.out.exists())

if __name__=="__main__":
    unittest.main()
