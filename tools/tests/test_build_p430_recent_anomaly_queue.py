import csv
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from build_p430_recent_anomaly_queue import build


def write_csv(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


class P430RecentAnomalyQueueTests(unittest.TestCase):
    def test_extracts_exact_recent_flags_and_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            v2 = root / "v2"
            v2.mkdir()
            (v2 / "TEST_OHLCV.csv").write_text(
                "Date,Open,High,Low,Close,Volume\n"
                "2026-04-24,449.9,449.8,440.5,445.1,4553\n",
                encoding="utf-8",
            )
            flags = root / "flags.csv"
            write_csv(flags, ["symbol", "date", "flag", "details"], [
                {"symbol":"TEST","date":"2026-04-24","flag":"OPEN_OUTSIDE_RANGE","details":"fixture"},
                {"symbol":"OLD","date":"2017-01-01","flag":"OPEN_OUTSIDE_RANGE","details":"excluded"},
            ])
            mapping = root / "mapping.csv"
            write_csv(mapping, ["symbol", "security_id"], [{"symbol":"TEST","security_id":"123"}])
            output = root / "queue.csv"
            rows = build(v2, flags, mapping, output, expected_count=1)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["open"], "449.9")
            self.assertEqual(rows[0]["high"], "449.8")
            self.assertEqual(rows[0]["turnover"], "")
            with output.open(newline="", encoding="utf-8") as fh:
                self.assertEqual(len(list(csv.DictReader(fh))), 1)

    def test_rejects_missing_mapping_and_non_open_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            v2 = root / "v2"
            v2.mkdir()
            (v2 / "TEST_OHLCV.csv").write_text(
                "Date,Open,High,Low,Close,Volume\n2026-04-24,449.9,449.8,440.5,445.1,4553\n",
                encoding="utf-8",
            )
            flags = root / "flags.csv"
            write_csv(flags, ["symbol", "date", "flag", "details"], [
                {"symbol":"TEST","date":"2026-04-24","flag":"CLOSE_OUTSIDE_RANGE","details":"fixture"},
            ])
            mapping = root / "mapping.csv"
            write_csv(mapping, ["symbol", "security_id"], [{"symbol":"TEST","security_id":"123"}])
            with self.assertRaises(ValueError):
                build(v2, flags, mapping, root / "queue.csv", expected_count=1)


if __name__ == "__main__":
    unittest.main()
