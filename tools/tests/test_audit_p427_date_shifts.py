import csv
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from audit_p427_date_shifts import build


class P427DateShiftAuditTests(unittest.TestCase):
    def test_one_day_shift_requires_raw_match_calendar_and_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw_dir = root / "raw"
            snapshot_dir = root / "snapshots"
            raw_dir.mkdir()
            snapshot_dir.mkdir()
            queue = root / "all_candidates.csv"
            queue.write_text(
                "symbol,date,status,calendar_status,open,high,low,close,volume,turnover,external_sha256,derived_sha256\n"
                "TEST,2026-03-01,ALREADY_RECOVERED_DATE_SHIFT,verified_open_observed,100,105,98,103,1000,102000,extsha,derivedsha\n",
                encoding="utf-8",
            )
            (raw_dir / "TEST_OHLCV.csv").write_text(
                "Date,Open,High,Low,Close,Volume\n"
                "2026-03-02,100,105,98,103,1000\n",
                encoding="utf-8",
            )
            (root / "calendar.csv").write_text(
                "date,status\n"
                "2026-03-01,verified_open_observed\n"
                "2026-03-02,verified_closed\n",
                encoding="utf-8",
            )
            (snapshot_dir / "2026_03_02.csv").write_text(
                "S.No,Symbol,Conf.,Open,High,Low,Close,LTP,Close - LTP,Close - LTP %,VWAP,Vol,Prev. Close,Turnover,Trans.\n"
                "1,TEST,-,100,105,98,103,103,0,0,102,1000,100,102000,10\n",
                encoding="utf-8",
            )
            output = root / "matrix.csv"
            rows = build(queue, raw_dir, root / "calendar.csv", snapshot_dir, output, expected_count=1)
            self.assertEqual(rows[0]["raw_tuple_matches"], "TRUE")
            self.assertEqual(rows[0]["shifted_snapshot_tuple_matches"], "TRUE")
            self.assertEqual(rows[0]["disposition"], "SECONDARY_CORROBORATED_ONE_DAY_DATE_SHIFT_PRIMARY_PENDING")
            self.assertEqual(rows[0]["raw_date_session_status"], "verified_closed")
            self.assertTrue(rows[0]["raw_file_sha256_actual"])
            with output.open(newline="", encoding="utf-8") as fh:
                saved = list(csv.DictReader(fh))
            self.assertEqual(saved[0]["symbol"], "TEST")

    def test_closed_date_mismatch_is_not_promoted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw_dir = root / "raw"
            snapshot_dir = root / "snapshots"
            raw_dir.mkdir()
            snapshot_dir.mkdir()
            queue = root / "all_candidates.csv"
            queue.write_text(
                "symbol,date,status,calendar_status,open,high,low,close,volume,turnover,external_sha256,derived_sha256\n"
                "TEST,2026-03-01,ALREADY_RECOVERED_DATE_SHIFT,verified_open_observed,100,105,98,103,1000,102000,extsha,derivedsha\n",
                encoding="utf-8",
            )
            (raw_dir / "TEST_OHLCV.csv").write_text(
                "Date,Open,High,Low,Close,Volume\n"
                "2026-03-02,100,105,98,102,1000\n",
                encoding="utf-8",
            )
            (root / "calendar.csv").write_text(
                "date,status\n2026-03-01,verified_open_observed\n2026-03-02,verified_closed\n",
                encoding="utf-8",
            )
            (snapshot_dir / "2026_03_02.csv").write_text(
                "S.No,Symbol,Conf.,Open,High,Low,Close,LTP,Close - LTP,Close - LTP %,VWAP,Vol,Prev. Close,Turnover,Trans.\n"
                "1,TEST,-,100,105,98,103,103,0,0,102,1000,100,102000,10\n",
                encoding="utf-8",
            )
            rows = build(queue, raw_dir, root / "calendar.csv", snapshot_dir, root / "matrix.csv", expected_count=1)
            self.assertEqual(rows[0]["raw_tuple_matches"], "FALSE")
            self.assertEqual(rows[0]["disposition"], "UNKNOWN_SHIFT_REQUIRES_ROW_REVIEW")


if __name__ == "__main__":
    unittest.main()
