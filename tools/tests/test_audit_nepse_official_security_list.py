import json, tempfile, unittest
from pathlib import Path
from audit_nepse_official_security_list import audit

ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/"reference/nepse_official_security_list_2026-11-25.raw.json"
CROSS=ROOT/"reference/nepse_equity_security_id_crosswalk_2026-11-26.csv"

class OfficialSecurityListTests(unittest.TestCase):
    def test_official_snapshot_and_equity_crosswalk_match(self):
        result=audit(RAW,CROSS)
        self.assertEqual(result["official_record_count"],573)
        self.assertEqual(result["raw_active_status_counts"],{"A":546,"S":27})
        self.assertEqual(result["equity_crosswalk_matches"],281)
        self.assertFalse(result["promotion_allowed"])
    def test_modified_raw_bytes_fail_sha_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw=Path(tmp)/"raw.json"
            raw.write_bytes(RAW.read_bytes()+b" ")
            with self.assertRaisesRegex(ValueError,"SHA-256 mismatch"): audit(raw,CROSS)

if __name__=="__main__":unittest.main()
