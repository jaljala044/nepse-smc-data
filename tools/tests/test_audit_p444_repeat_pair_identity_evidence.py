import csv
import tempfile
import unittest
from pathlib import Path

from audit_p444_repeat_pair_identity_evidence import build_matrix, read_csv, REQUIRED_PAIR, REQUIRED_IDENTITY, REQUIRED_EXECUTION

HASH_A = "a" * 64
HASH_B = "b" * 64

class P444EvidenceMatrixTests(unittest.TestCase):
    def pair(self):
        return {"pair_id":"p1","symbol":"ABC","business_date":"2026-01-05",
                "source_path":"archive.csv","source_blob_sha":HASH_A,"source_row":"7"}

    def identity(self, **changes):
        row = {"security_id":"1001","symbol":"ABC","instrument_type":"equity",
               "effective_from":"2025-01-01","effective_to":"",
               "source_url":"https://exchange.example/security-master",
               "retrieved_at":"2026-01-06T00:00:00Z","raw_sha256":HASH_A,
               "authorization_status":"authorized","evidence_tier":"primary"}
        return {**row, **changes}

    def execution(self, **changes):
        row = {"security_id":"1001","business_date":"2026-01-05","traded_quantity":"50",
               "source_url":"https://exchange.example/eod","retrieved_at":"2026-01-06T00:00:00Z",
               "raw_sha256":HASH_B,"authorization_status":"rights_cleared","evidence_tier":"primary"}
        return {**row, **changes}

    def test_exact_effective_id_and_execution_match(self):
        result = build_matrix([self.pair()], [self.identity()], [self.execution()])[0]
        self.assertEqual(result["disposition"], "IDENTITY_AND_EXECUTION_EVIDENCE_MATCHED")
        self.assertEqual(result["resolved_security_id"], "1001")
        self.assertEqual(result["canonical_promotion_allowed"], "false")

    def test_missing_or_unapproved_identity_stays_held(self):
        bad = self.identity(authorization_status="not_assessed")
        result = build_matrix([self.pair()], [bad], [self.execution()])[0]
        self.assertEqual(result["disposition"], "HOLD")
        self.assertEqual(result["reason"], "identity_not_uniquely_proven")

    def test_wrong_date_execution_stays_held(self):
        result = build_matrix([self.pair()], [self.identity()],
                               [self.execution(business_date="2026-01-06")])[0]
        self.assertEqual(result["disposition"], "HOLD")
        self.assertEqual(result["reason"], "no_rights_cleared_execution_on_exact_date")

    def test_overlapping_effective_identity_rows_stay_held(self):
        result = build_matrix([self.pair()],
            [self.identity(), self.identity(security_id="1002")], [self.execution()])[0]
        self.assertEqual(result["disposition"], "HOLD")
        self.assertEqual(result["reason"], "multiple_effective_identity_rows")

    def test_csv_schema_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.csv"
            path.write_text("symbol,date\nABC,2026-01-05\n")
            with self.assertRaises(ValueError):
                read_csv(path, REQUIRED_PAIR)

if __name__ == "__main__":
    unittest.main()
