import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scanner_inputs import prepare_scanner_inputs as mod

FIELDS = ["symbol", "date", "open", "high", "low", "close", "volume"]

def candle(**kwargs):
    return dict(dict(zip(FIELDS, ["ABC", "2026-01-04", "10", "11", "9", "10", "5"])), **kwargs)

class QuarantineTests(unittest.TestCase):
    def test_weekly_aggregation(self):
        data = [candle(date="2026-01-05", open="12", high="15", low="10", close="14", volume="7"),
                candle(), candle(date="2026-01-11"), candle(symbol="XYZ")]
        result = mod.aggregate_daily(data, "weekly", set())
        self.assertEqual(len(result), 3)
        b = result[0]
        self.assertEqual(b["date"], "2026-01-05")
        self.assertEqual([b[k] for k in ("open", "high", "low", "close", "volume")], [10, 15, 9, 14, 12])

    def test_month_boundary(self):
        data = [candle(date="2026-01-31"), candle(date="2026-02-01")]
        self.assertEqual(len(mod.aggregate_daily(data, "monthly", set())), 2)

    def test_aggregate_rejects_invalid(self):
        with self.assertRaises(ValueError):
            mod.aggregate_daily([candle(open="0")], "weekly", set())

    def test_valid(self):
        mod.validate_daily([candle(), candle(date="2026-01-05")], set())

    def test_bad_values(self):
        for change in [dict(open="0"), dict(low="-1"), dict(high="8"), dict(close="12"),
                       dict(volume="-1"), dict(volume="NaN"), dict(high="Infinity"),
                       dict(date="2026-02-30"), dict(symbol=" "), dict(open="bad")]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                mod.validate_daily([candle(**change)], set())

    def test_duplicate_normalized_key(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            mod.validate_daily([candle(), candle(symbol=" abc ", date="2026-01-04 ")], set())

    def test_closed_session(self):
        with self.assertRaisesRegex(ValueError, "closed session"):
            mod.validate_daily([candle()], {"2026-01-04"})

    def test_calendar_missing_or_conflicting(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "reference").mkdir()
            calendar = root / "reference/nepse_canonical_session_calendar_2025-2026.csv"
            positive = root / "reference/nepse_positive_open_sessions_2025-11-26_2026-11-25.csv"
            calendar.write_text("date,status,scope\n2026-01-04,verified_closed,all_securities\n")
            positive.write_text("date,status\n2026-01-04,verified_open\n")
            with patch.object(mod, "SUPPLEMENT", root / "scanner_inputs"):
                with self.assertRaisesRegex(ValueError, "conflicting"):
                    mod.verified_closed_dates()
                positive.unlink()
                with self.assertRaises(FileNotFoundError):
                    mod.verified_closed_dates()

    def test_rejected_original_not_published(self):
        self.check_prepare(candle(open="0"), None, False)

    def test_rejected_supplement_not_published(self):
        self.check_prepare(candle(), candle(symbol="XYZ", high="8"), False)

    def test_valid_stage_published(self):
        self.check_prepare(candle(), candle(symbol="XYZ"), True)

    def check_prepare(self, original_row, supplemental_row, success):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original, supplement, output = [root / x for x in ("original", "supplement", "output")]
            original.mkdir()
            supplement.mkdir()
            source = original / "daily_prices.csv"
            mod.write(source, FIELDS, [original_row])
            before = source.read_bytes()
            stale = original / "weekly_prices.csv"
            stale.write_text("stale\\n")
            mod.write(supplement / "benchmark_daily.csv", FIELDS, [supplemental_row] if supplemental_row else [])
            for name in ("sectors", "sector_data", "corporate_actions", "broker_summary"):
                (original / (name + ".csv")).write_text("fixture\n")
            with patch.object(mod, "SUPPLEMENT", supplement), patch.object(mod, "verified_closed_dates", return_value=set()):
                if success:
                    mod.prepare(original, output)
                    self.assertEqual(len(list(mod.rows(output / "daily_prices.csv"))), 2)
                    for period in ("weekly", "monthly"):
                        self.assertEqual(len(list(mod.rows(output / (period + "_prices.csv")))), 2)
                    self.assertEqual(stale.read_text(), "stale\\n")
                else:
                    with self.assertRaises(ValueError):
                        mod.prepare(original, output)
                    self.assertFalse(output.exists())
            self.assertEqual(source.read_bytes(), before)

if __name__ == "__main__":
    unittest.main()
