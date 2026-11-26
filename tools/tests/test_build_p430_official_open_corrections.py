import csv
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from build_p430_official_open_corrections import build


def write_csv(path, rows):
    fields = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


class P430OfficialOpenCorrectionTests(unittest.TestCase):
    def base(self):
        return {
            "symbol": "TEST", "business_date": "2026-04-24",
            "candidate_open": "449.9", "candidate_high": "449.8",
            "candidate_low": "440.5", "candidate_close": "445.1",
            "candidate_volume": "4553",
            "official_open": "445.0", "official_high": "449.8",
            "official_low": "440.5", "official_close": "445.1",
            "official_volume": "4553",
            "official_capture_status": "OFFICIAL_CAPTURE_ACCEPTED",
            "official_row_count": "1", "official_quality_flags": "",
            "official_security_id": "180", "mapping_security_id": "180",
            "official_payload_sha256": "abc123",
            "official_source_url": "https://www.nepalstock.com/api/nots/nepse-data/today-price?businessDate=2026-04-24",
            "official_retrieved_at": "2026-11-26T23:00:00+05:45",
        }

    def test_emits_only_open_correction_with_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            matrix, output = root / "matrix.csv", root / "corrections.csv"
            write_csv(matrix, [self.base()])
            rows = build(matrix, output, expected_count=1)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["field"], "Open")
            self.assertEqual(rows[0]["candidate_value"], "449.9")
            self.assertEqual(rows[0]["official_value"], "445.0")
            self.assertEqual(rows[0]["official_payload_sha256"], "abc123")

    def test_rejects_non_open_difference(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            row = self.base()
            row["official_close"] = "444.0"
            matrix = root / "matrix.csv"
            write_csv(matrix, [row])
            with self.assertRaises(ValueError):
                build(matrix, root / "corrections.csv", expected_count=1)

    def test_rejects_unaccepted_or_unmapped_official_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for field, value in [("official_capture_status", "NO_OFFICIAL_ROW"), ("official_security_id", "999")]:
                row = self.base()
                row[field] = value
                matrix = root / f"{field}.csv"
                write_csv(matrix, [row])
                with self.assertRaises(ValueError):
                    build(matrix, root / f"{field}-out.csv", expected_count=1)


if __name__ == "__main__":
    unittest.main()
