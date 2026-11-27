"""Regression tests for authenticated Drive quarantine retrieval."""
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from scanner_inputs import retrieve_drive_quarantine as retrieve


class FakeResponse:
    status_code = 200

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def iter_content(self, chunk_size):
        self.chunk_size = chunk_size
        yield b"overlay"
        

class FakeSession:
    def __init__(self):
        self.response = FakeResponse()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def get(self, *args, **kwargs):
        self.request = (args, kwargs)
        return self.response


class DriveRetrievalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.output = Path(self.tmp.name) / "overlay.csv"
        self.session = FakeSession()
        self.google = types.ModuleType("google")
        self.auth = types.ModuleType("google.auth")
        self.transport = types.ModuleType("google.auth.transport")
        self.requests = types.ModuleType("google.auth.transport.requests")
        self.auth.default = Mock(return_value=(object(), None))
        self.requests.AuthorizedSession = Mock(return_value=self.session)
        self.google.auth = self.auth
        self.auth.transport = self.transport
        self.transport.requests = self.requests
        self.modules = {
            "google": self.google,
            "google.auth": self.auth,
            "google.auth.transport": self.transport,
            "google.auth.transport.requests": self.requests,
        }

    def test_output_created_only_after_full_quarantine_validation(self):
        with patch.dict(sys.modules, self.modules), \
             patch.object(retrieve, "EXPECTED_BYTES", 7), \
             patch.object(retrieve, "load_holds", return_value={("ABC", "2026-01-01"): "HOLD"}) as validate:
            retrieve.retrieve(self.output)
        self.assertEqual(self.output.read_bytes(), b"overlay")
        validate.assert_called_once()
        self.assertEqual(validate.call_args.args[0].read_bytes(), b"overlay")
        self.auth.default.assert_called_once_with(scopes=["https://www.googleapis.com/auth/drive.readonly"])
        self.assertEqual(self.session.request[1]["allow_redirects"], False)

    def test_size_mismatch_never_creates_output(self):
        with patch.dict(sys.modules, self.modules), \
             patch.object(retrieve, "EXPECTED_BYTES", 8), \
             patch.object(retrieve, "load_holds") as validate:
            with self.assertRaisesRegex(ValueError, "size mismatch"):
                retrieve.retrieve(self.output)
        self.assertFalse(self.output.exists())
        validate.assert_not_called()

    def test_quarantine_validation_failure_never_creates_output(self):
        with patch.dict(sys.modules, self.modules), \
             patch.object(retrieve, "EXPECTED_BYTES", 7), \
             patch.object(retrieve, "load_holds", side_effect=ValueError("digest/schema mismatch")):
            with self.assertRaisesRegex(ValueError, "digest/schema mismatch"):
                retrieve.retrieve(self.output)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
