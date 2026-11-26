import csv
import tempfile
import unittest
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "audit_observed_session_gaps.py"
SPEC = importlib.util.spec_from_file_location("audit_observed_session_gaps", SCRIPT)
ENGINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ENGINE)
audit_symbol = ENGINE.audit_symbol
load_observed_dates = ENGINE.load_observed_dates
load_universe = ENGINE.load_universe


class ObservedSessionGapTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.ohlcv = self.root / "ohlcv"
        self.ohlcv.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def write_csv(self, path, rows, fields):
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def test_missing_row_is_archive_gap_not_no_trade(self):
        path = self.ohlcv / "ABC_OHLCV.csv"
        self.write_csv(path, [{"Date": "2026-11-19", "Volume": "100"}], ["Date", "Volume"])
        result = audit_symbol("ABC", ["2026-11-19", "2026-11-20"], self.ohlcv)
        self.assertEqual(result["missing_archive_date_count"], 1)
        self.assertEqual(result["missing_dates"], ["2026-11-20"])
        self.assertEqual(result["classification"], "ARCHIVE_GAP_REVIEW_REQUIRED")
        self.assertNotIn("NO_TRADE", result["classification"])

    def test_duplicate_observed_date_is_counted(self):
        path = self.ohlcv / "ABC_OHLCV.csv"
        self.write_csv(path, [
            {"Date": "2026-11-19", "Volume": "100"},
            {"Date": "2026-11-19", "Volume": "200"},
        ], ["Date", "Volume"])
        result = audit_symbol("ABC", ["2026-11-19"], self.ohlcv)
        self.assertEqual(result["duplicate_date_count"], 1)
        self.assertEqual(result["present_date_count"], 1)

    def test_missing_file_is_explicit_gap(self):
        result = audit_symbol("XYZ", ["2026-11-19"], self.ohlcv)
        self.assertEqual(result["file_status"], "MISSING_FILE")
        self.assertEqual(result["missing_archive_date_count"], 1)

    def test_calendar_uses_only_positive_observed_status(self):
        p = self.root / "calendar.csv"
        self.write_csv(p, [
            {"date": "2026-11-19", "status": "verified_open_observed"},
            {"date": "2026-11-20", "status": "candidate_open_weekday"},
            {"date": "2026-11-21", "status": "verified_closed"},
        ], ["date", "status"])
        self.assertEqual(load_observed_dates(p), ["2026-11-19"])

    def test_universe_count_guard(self):
        p = self.root / "universe.csv"
        self.write_csv(p, [{"symbol": "ABC"}, {"symbol": "XYZ"}], ["symbol"])
        self.assertEqual(load_universe(p, 2), ["ABC", "XYZ"])
        with self.assertRaises(ValueError):
            load_universe(p, 3)


if __name__ == "__main__":
    unittest.main()
