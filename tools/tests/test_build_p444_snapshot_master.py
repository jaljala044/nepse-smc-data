import csv, tempfile, unittest
from pathlib import Path
from build_p444_snapshot_master import normalize

class SnapshotMasterTests(unittest.TestCase):
    def test_normalizes_snapshot_without_inventing_lifecycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            src=Path(tmp)/"in.csv"; dst=Path(tmp)/"out.csv"
            src.write_text("symbol,security_id,security_name,active_status,snapshot_date,source_blob_sha\nABC,1,ABC Limited,A,2026-11-25,"+"a"*40+"\n")
            self.assertEqual(normalize(src,dst),1)
            row=next(csv.DictReader(dst.open()))
            self.assertEqual(row["instrument_type"],"UNKNOWN")
            self.assertEqual(row["effective_from"],"")
            self.assertEqual(row["evidence_tier"],"current_snapshot_only")
            self.assertEqual(row["canonical_promotion_allowed"],"false")

    def test_duplicate_ids_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            src=Path(tmp)/"in.csv"; dst=Path(tmp)/"out.csv"
            line="ABC,1,ABC Limited,A,2026-11-25,"+"a"*40
            src.write_text("symbol,security_id,security_name,active_status,snapshot_date,source_blob_sha\n"+line+"\n"+"XYZ,1,XYZ Limited,A,2026-11-25,"+"b"*40+"\n")
            with self.assertRaises(ValueError): normalize(src,dst)

    def test_missing_provenance_column_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            src=Path(tmp)/"in.csv"; dst=Path(tmp)/"out.csv"
            src.write_text("symbol,security_id\nABC,1\n")
            with self.assertRaises(ValueError): normalize(src,dst)

if __name__ == "__main__": unittest.main()
