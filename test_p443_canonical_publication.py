import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile
from scanner_inputs import canonical_publication as p
from scanner_inputs import retrieve_quarantine_overlay as q


class PublicationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.day = "2026-11-26"
        self.dest = self.root / f"floorsheet_{self.day}.csv"
        self.raw = b"Contract_No,Symbol,Buyer,Seller,Quantity,Rate,Amount\n20261126001,ABC,6,7,10,100,1000\n"
        for name, value in (("load_holds", {}), ("verified_closed_dates", set())):
            ctx = patch.object(p, name, return_value=value)
            ctx.start()
            self.addCleanup(ctx.stop)

    def publish(self, raw=None):
        return p.publish_daily_floorsheet(self.raw if raw is None else raw, self.day, self.dest, self.root / "overlay.csv")

    def test_exclusive_publish_and_identical_rerun(self):
        self.assertEqual(self.publish(), "published")
        self.assertEqual(self.publish(), "unchanged")
        self.assertEqual(self.dest.read_bytes(), self.raw)
        with self.assertRaises(FileExistsError):
            self.publish(self.raw.replace(b"100,1000", b"101,1010"))
        self.assertEqual(self.dest.read_bytes(), self.raw)

    def test_wrong_session(self):
        with self.assertRaises(ValueError):
            self.publish(self.raw.replace(b"20261126", b"20261125"))
        self.assertFalse(self.dest.exists())

    def test_held_security(self):
        with patch.object(p, "load_holds", return_value={("ABC", self.day): "HOLD"}):
            with self.assertRaisesRegex(ValueError, "Quarantined"):
                self.publish()
        self.assertFalse(self.dest.exists())

    def test_duplicate_contract(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.publish(self.raw + self.raw.splitlines(keepends=True)[1])
        self.assertFalse(self.dest.exists())

    def test_missing_overlay(self):
        with patch.object(p, "load_holds", side_effect=FileNotFoundError):
            with self.assertRaises(FileNotFoundError):
                self.publish()
        self.assertFalse(self.dest.exists())


class RetrievalTests(unittest.TestCase):
    def test_pinned_archive_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / "artifact.zip"
            output = root / "overlay.csv"
            raw = b"fixture"
            with ZipFile(archive, "w") as z:
                z.writestr("../untrusted.csv", raw)
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps(dict(
                artifact_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
                overlay_sha256=hashlib.sha256(raw).hexdigest(), overlay_bytes=len(raw))))
            with patch.object(q, "MANIFEST", manifest), patch.object(q, "load_holds", return_value={}):
                q.retrieve(archive, output)
                self.assertEqual(output.read_bytes(), raw)
                self.assertFalse((root.parent / "untrusted.csv").exists())
                output.unlink()
                archive.write_bytes(archive.read_bytes() + b"x")
                with self.assertRaisesRegex(ValueError, "digest mismatch"):
                    q.retrieve(archive, output)
                self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
