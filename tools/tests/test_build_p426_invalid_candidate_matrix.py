import csv
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from build_p426_invalid_candidate_matrix import build


class P426InvalidCandidateMatrixTests(unittest.TestCase):
    def test_same_day_snapshot_confirms_invalid_external_candle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            snapshots = root / "snapshots"
            snapshots.mkdir()
            queue = root / "queue.csv"
            queue.write_text(
                "symbol,date,status,calendar_status,open,high,low,close,volume,turnover,external_sha256,derived_sha256\n"
                "TEST,2026-04-24,QUARANTINE_INVALID_EXTERNAL_OHLCV,verified_open_observed,100,99,95,98,1000,98000,extsha,rawsha\n",
                encoding="utf-8",
            )
            (snapshots / "2026_04_24.csv").write_text(
                "S.No,Symbol,Conf.,Open,High,Low,Close,LTP,Close - LTP,Close - LTP %,VWAP,Vol,Prev. Close,Turnover,Trans.\n"
                "1,TEST,-,100,99,95,98,98,0,0,97,1000,99,98000,10\n",
                encoding="utf-8",
            )
            output = root / "matrix.csv"
            rows = build(queue, snapshots, output, expected_count=1)
            self.assertEqual(rows[0]["invalid_reason"], "OPEN_ABOVE_HIGH")
            self.assertEqual(rows[0]["snapshot_ohlc_valid"], "FALSE")
            self.assertEqual(rows[0]["snapshot_matches_external"], "TRUE")
            self.assertEqual(rows[0]["disposition"], "SAME_DAY_SNAPSHOT_CONFIRMS_INVALID_CANDLE")
            with output.open(newline="", encoding="utf-8") as fh:
                saved = list(csv.DictReader(fh))
            self.assertEqual(saved[0]["symbol"], "TEST")

    def test_valid_same_day_snapshot_does_not_promote_external_invalid_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            snapshots = root / "snapshots"
            snapshots.mkdir()
            queue = root / "queue.csv"
            queue.write_text(
                "symbol,date,status,calendar_status,open,high,low,close,volume,turnover,external_sha256,derived_sha256\n"
                "TEST,2026-04-24,QUARANTINE_INVALID_EXTERNAL_OHLCV,verified_open_observed,100,99,95,98,1000,98000,extsha,rawsha\n",
                encoding="utf-8",
            )
            (snapshots / "2026_04_24.csv").write_text(
                "S.No,Symbol,Conf.,Open,High,Low,Close,LTP,Close - LTP,Close - LTP %,VWAP,Vol,Prev. Close,Turnover,Trans.\n"
                "1,TEST,-,98,100,95,98,98,0,0,97,1000,99,98000,10\n",
                encoding="utf-8",
            )
            rows = build(queue, snapshots, root / "matrix.csv", expected_count=1)
            self.assertEqual(rows[0]["snapshot_ohlc_valid"], "TRUE")
            self.assertEqual(rows[0]["snapshot_matches_external"], "FALSE")
            self.assertEqual(rows[0]["disposition"], "SAME_DAY_SNAPSHOT_HAS_VALID_CANDLE_DIFFERENT_OR_EXTERNAL_INVALID")


if __name__ == "__main__":
    unittest.main()
