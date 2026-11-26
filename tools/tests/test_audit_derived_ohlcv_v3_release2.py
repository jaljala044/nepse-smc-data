import csv
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from audit_derived_ohlcv_v3_release import audit


def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def write_csv(path, rows, fields=None):
    fields = fields or (list(rows[0]) if rows else [])
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


class DerivedOhlcvV3AuditTests(unittest.TestCase):
    def fixture(self, root, bad_high=False):
        v2, v3, raw = root / "v2", root / "v3", root / "raw"
        v2.mkdir(); v3.mkdir(); raw.mkdir()
        raw_bytes = b"Date,Open,High,Low,Close,Volume\n2026-04-24,449.9,449.8,440.5,445.1,4553\n"
        v2_bytes = raw_bytes
        v3_high = "450.0" if bad_high else "449.8"
        v3_bytes = f"Date,Open,High,Low,Close,Volume\n2026-04-24,445.0,{v3_high},440.5,445.1,4553\n".encode()
        (raw / "TEST_OHLCV.csv").write_bytes(raw_bytes)
        (v2 / "TEST_OHLCV.csv").write_bytes(v2_bytes)
        (v3 / "TEST_OHLCV.csv").write_bytes(v3_bytes)
        v2_manifest = [{"symbol":"TEST","raw_source_blob_sha":blob(raw_bytes),"derived_blob_sha":blob(v2_bytes),"rows":1}]
        v3_manifest = [{"symbol":"TEST","raw_source_blob_sha":blob(raw_bytes),"v2_source_blob_sha":blob(v2_bytes),"derived_blob_sha":blob(v3_bytes),"rows":1}]
        write_csv(v2 / "manifest.csv", v2_manifest)
        write_csv(v3 / "manifest.csv", v3_manifest)
        prov_fields = ["symbol","official_business_date","action","official_payload_sha256"]
        write_csv(v2 / "provenance_ledger.csv", [], prov_fields)
        write_csv(v3 / "provenance_ledger.csv", [{
            "symbol":"TEST","official_business_date":"2026-04-24",
            "action":"OFFICIAL_OPEN_FIELD_CORRECTION","official_payload_sha256":"payload",
        }], prov_fields)
        corr_fields = ["symbol","date","field","raw_value","derived_value","source","source_url","reason","status"]
        write_csv(v2 / "corrections.csv", [], corr_fields)
        write_csv(v3 / "corrections.csv", [{
            "symbol":"TEST","date":"2026-04-24","field":"Open","raw_value":"449.9",
            "derived_value":"445.0","source":"NEPSE","source_url":"https://www.nepalstock.com/api",
            "reason":"official","status":"applied_in_derived_v3",
        }], corr_fields)
        matrix_fields = [
            "symbol","business_date","candidate_open","official_open","official_high","official_low",
            "official_close","official_volume","official_payload_sha256",
        ]
        matrix = root / "matrix.csv"
        write_csv(matrix, [{
            "symbol":"TEST","business_date":"2026-04-24","candidate_open":"449.9","official_open":"445.0",
            "official_high":"449.8","official_low":"440.5","official_close":"445.1",
            "official_volume":"4553","official_payload_sha256":"payload",
        }], matrix_fields)
        correction_fields = ["symbol","business_date","field","candidate_value","official_value","disposition"]
        correction = root / "correction.csv"
        write_csv(correction, [{
            "symbol":"TEST","business_date":"2026-04-24","field":"Open","candidate_value":"449.9","official_value":"445.0",
            "disposition":"PRIMARY_OFFICIAL_NEPSE_EOD_OPEN_CORRECTION",
        }], correction_fields)
        return v2, v3, raw, matrix, correction

    def test_audit_accepts_official_open_only_change_and_source_preservation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            v2, v3, raw, matrix, correction = self.fixture(root)
            totals = audit(v2, v3, raw, matrix, correction, root / "audit",
                           expected_symbols=1, expected_corrections=1,
                           expected_invariant_flags=0, expected_open_flags=0)
            self.assertEqual(totals["official_open_corrections_verified"], 1)
            self.assertEqual(totals["unapproved_v2_to_v3_changes"], 0)
            self.assertEqual(totals["remaining_ohlcv_invariant_flags"], 0)

    def test_audit_rejects_non_open_field_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            v2, v3, raw, matrix, correction = self.fixture(root, bad_high=True)
            with self.assertRaises(ValueError):
                audit(v2, v3, raw, matrix, correction, root / "audit",
                      expected_symbols=1, expected_corrections=1,
                      expected_invariant_flags=0, expected_open_flags=0)


if __name__ == "__main__":
    unittest.main()
