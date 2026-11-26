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


class FloorsheetTests(unittest.TestCase):
    fields = ["contract_no", "trade_date", "symbol", "buyer", "seller", "quantity", "rate", "amount", "id"]

    def trade(self, **changes):
        return dict(dict(zip(self.fields, ["123", "2026-01-04", "ABC", "48", "6", "10", "12.50", "125.00", "456"])), **changes)

    def check_rows(self, records, error=None, closed=None, fields=None):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "floorsheet.csv"
            mod.write(path, fields or self.fields, records)
            before = path.read_bytes()
            if error:
                with self.assertRaisesRegex(ValueError, error):
                    mod.validate_floorsheet(path, closed or set())
            else:
                mod.validate_floorsheet(path, closed or set())
            self.assertEqual(before, path.read_bytes())

    def test_valid_trade(self):
        self.check_rows([self.trade(), self.trade(id="457", contract_no="124")])

    def test_duplicate_identity(self):
        self.check_rows([self.trade(), self.trade()], "duplicate")

    def test_missing_fields(self):
        for field in ("contract_no", "symbol", "buyer", "seller", "id"):
            with self.subTest(field=field):
                self.check_rows([self.trade(**{field: ""})], "Missing")

    def test_invalid_numeric(self):
        for changes in ({"quantity":"0"}, {"quantity":"1.5"}, {"rate":"-1"}, {"amount":"NaN"}, {"rate":"Infinity"}):
            with self.subTest(changes=changes):
                self.check_rows([self.trade(**changes)], "Invalid trade")

    def test_amount_mismatch(self):
        self.check_rows([self.trade(amount="124")], "amount mismatch")

    def test_closed_date(self):
        self.check_rows([self.trade()], "closed session", {"2026-01-04"})

    def test_invalid_date(self):
        self.check_rows([self.trade(trade_date="2026-02-30")], "Rejected floorsheet row")

    def test_empty(self):
        self.check_rows([], "Empty floorsheet")

    def test_missing_header(self):
        self.check_rows([self.trade()], "Missing required", fields=self.fields[:-2])

    def test_blocked_blob_and_unsupported(self):
        import hashlib
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "floorsheet.csv.gz"
            raw = b"fixture"
            path.write_bytes(raw)
            # Git blob object header uses a NUL byte.
            fingerprint = hashlib.sha1(("blob " + str(len(raw))).encode() + bytes([0]) + raw).hexdigest()
            with patch.object(mod, "BLOCKED_FLOORSHEET_BLOBS", {fingerprint}):
                with self.assertRaisesRegex(ValueError, "Quarantined"):
                    mod.validate_floorsheet(path, set())
            with self.assertRaisesRegex(ValueError, "Unsupported"):
                mod.validate_floorsheet(path, set())

    def test_decompressed_quarantine_payloads_are_blocked(self):
        from types import SimpleNamespace
        expected = {
            "441f2b64106b48086a0326604ab92c40f2e02fa163bca97cfe17385c9f88ebc8",
            "beee6326be30d364eb6b0c55a2c36d9aa847daeb0af1bf5ddb2e4d3b82850433",
        }
        self.assertEqual(mod.BLOCKED_FLOORSHEET_SHA256, expected)
        self.assertIn("0dd938bc5e6bfd50fa09bf85f0836d443ab15983", mod.BLOCKED_FLOORSHEET_BLOBS)
        self.assertIn("49d6498b30681b7896b6c5c824b518e50f941d", mod.BLOCKED_FLOORSHEET_BLOBS)
        for fingerprint in expected:
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "floorsheet.csv"
                path.write_bytes(b"decompressed archive payload")
                fake = SimpleNamespace(hexdigest=lambda: fingerprint)
                with patch.object(mod.hashlib, "sha256", return_value=fake):
                    with self.assertRaisesRegex(ValueError, "Quarantined"):
                        mod.validate_floorsheet(path, set())

    def test_stage_rejects_invalid_floorsheet(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original, supplement, output = [root / x for x in ("original", "supplement", "output")]
            original.mkdir()
            supplement.mkdir()
            mod.write(original / "daily_prices.csv", FIELDS, [candle()])
            mod.write(supplement / "benchmark_daily.csv", FIELDS, [])
            for name in ("sectors", "sector_data", "corporate_actions"):
                (original / (name + ".csv")).write_text("fixture")
            source = original / "floorsheet.csv"
            mod.write(source, self.fields, [self.trade(amount="1")])
            before = source.read_bytes()
            with patch.object(mod, "SUPPLEMENT", supplement), patch.object(mod, "verified_closed_dates", return_value=set()):
                with self.assertRaisesRegex(ValueError, "amount mismatch"):
                    mod.prepare(original, output)
            self.assertFalse(output.exists())
            self.assertEqual(source.read_bytes(), before)

if __name__ == "__main__":
    unittest.main()
