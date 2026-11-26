import csv
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from build_p424_conflict_matrix import build_matrix


class P424ConflictMatrixTests(unittest.TestCase):
    def test_builds_exact_row_comparison_and_keeps_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw_dir = root / "raw"
            raw_dir.mkdir()
            ext = root / "external.csv"
            ext.write_text(
                "date,symbol,external_open,external_high,external_low,external_close,external_volume,external_turnover,source_repository,source_commit,source_path\n"
                "2025-07-28,TEST,10,12,9,11,100,1100,source/repo,abc123,data.csv\n",
                encoding="utf-8",
            )
            (raw_dir / "TEST_OHLCV.csv").write_text(
                "Date,Open,High,Low,Close,Volume\n"
                "2025-07-28,10,12,9,10,90\n",
                encoding="utf-8",
            )
            output = root / "matrix.csv"
            rows = build_matrix(ext, raw_dir, output)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["ohlcv_equal"], "FALSE")
            self.assertEqual(rows[0]["close_delta_external_minus_smc"], "1")
            self.assertEqual(rows[0]["volume_delta_external_minus_smc"], "10")
            self.assertEqual(rows[0]["canonical_disposition"], "UNKNOWN_SOURCE_CONFLICT")
            self.assertEqual(rows[0]["primary_source_window"], "OUTSIDE_OFFICIAL_365D_HISTORY_WINDOW")
            with output.open(newline="", encoding="utf-8") as fh:
                saved = list(csv.DictReader(fh))
            self.assertEqual(saved[0]["symbol"], "TEST")

    def test_missing_raw_date_is_not_silently_filled(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw_dir = root / "raw"
            raw_dir.mkdir()
            ext = root / "external.csv"
            ext.write_text(
                "date,symbol,external_open,external_high,external_low,external_close,external_volume\n"
                "2025-07-28,TEST,10,12,9,11,100\n",
                encoding="utf-8",
            )
            (raw_dir / "TEST_OHLCV.csv").write_text(
                "Date,Open,High,Low,Close,Volume\n"
                "2025-07-29,10,12,9,11,100\n",
                encoding="utf-8",
            )
            rows = build_matrix(ext, raw_dir, root / "matrix.csv")
            self.assertEqual(rows[0]["ohlcv_equal"], "UNKNOWN_RAW_DATE_NOT_UNIQUE")
            self.assertEqual(rows[0]["canonical_disposition"], "UNKNOWN_SOURCE_CONFLICT")


if __name__ == "__main__":
    unittest.main()
