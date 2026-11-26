import csv
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "reconcile_floorsheet_ohlcv.py"
SPEC = importlib.util.spec_from_file_location("reconcile_floorsheet_ohlcv", SCRIPT)
ENGINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ENGINE)


class FloorsheetReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.floors = self.root / "floors"
        self.ohlcv = self.root / "ohlcv"
        self.floors.mkdir()
        self.ohlcv.mkdir()
        self.floor = self.floors / "floorsheet_2026-11-20.csv"
        with self.floor.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["Trading_Date", "Transaction", "Symbol", "Quantity", "Rate"])
            writer.writeheader()
            writer.writerow({"Trading_Date": "2026-11-20", "Transaction": "C-1", "Symbol": "ABC", "Quantity": "10", "Rate": "100"})
        self.ohlcv_file = self.ohlcv / "ABC_OHLCV.csv"
        with self.ohlcv_file.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["Date", "Open", "High", "Low", "Close", "Volume"])
            writer.writeheader()
            writer.writerow({"Date": "2026-11-20", "Open": "100", "High": "100", "Low": "100", "Close": "100", "Volume": "10"})

    def tearDown(self):
        self.temp.cleanup()

    def run_reconcile(self, session="verified_open", complete="false", evidence="", uri="", digest=""):
        manifest = {"floorsheet_complete": complete, "completeness_evidence": evidence, "source_uri": uri, "source_sha256": digest}
        return ENGINE.reconcile_date("2026-11-20", self.floor, self.ohlcv,
                                     {"2026-11-20": session}, {"2026-11-20": manifest})

    def test_positive_contract_is_traded_without_full_file_completeness(self):
        rows = self.run_reconcile()
        abc = next(r for r in rows if r["symbol"] == "ABC")
        self.assertEqual(abc["trade_status"], "TRADED")
        self.assertEqual(abc["contracts"], 1)
        self.assertEqual(abc["floorsheet_quantity"], 10)
        self.assertTrue(abc["volume_match"])

    def test_absence_from_incomplete_file_is_unknown(self):
        rows = self.run_reconcile()
        xyz = next(r for r in rows if r["symbol"] == "XYZ") if any(r["symbol"] == "XYZ" for r in rows) else None
        self.assertIsNone(xyz)
        # A zero-contract symbol can only be assessed when it exists in the OHLCV universe.
        with (self.ohlcv / "XYZ_OHLCV.csv").open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["Date", "Open", "High", "Low", "Close", "Volume"])
            writer.writeheader()
            writer.writerow({"Date": "2026-11-20", "Open": "1", "High": "1", "Low": "1", "Close": "1", "Volume": "0"})
        xyz = next(r for r in self.run_reconcile() if r["symbol"] == "XYZ")
        self.assertEqual(xyz["trade_status"], "UNKNOWN")

    def test_no_trade_requires_verified_open_complete_and_matching_hash(self):
        digest = hashlib.sha256(self.floor.read_bytes()).hexdigest()
        with (self.ohlcv / "XYZ_OHLCV.csv").open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["Date", "Open", "High", "Low", "Close", "Volume"])
            writer.writeheader()
            writer.writerow({"Date": "2026-11-20", "Open": "1", "High": "1", "Low": "1", "Close": "1", "Volume": "0"})
        rows = self.run_reconcile(complete="true", evidence="full-day page audit + zero-tail check",
                                  uri="https://source.example/floorsheet/2026-11-20", digest=digest)
        xyz = next(r for r in rows if r["symbol"] == "XYZ")
        self.assertEqual(xyz["trade_status"], "NO_TRADE")

    def test_closed_session_never_becomes_no_trade(self):
        digest = hashlib.sha256(self.floor.read_bytes()).hexdigest()
        with (self.ohlcv / "XYZ_OHLCV.csv").open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["Date", "Open", "High", "Low", "Close", "Volume"])
            writer.writeheader()
            writer.writerow({"Date": "2026-11-20", "Open": "1", "High": "1", "Low": "1", "Close": "1", "Volume": "0"})
        rows = self.run_reconcile(session="verified_closed", complete="true", evidence="audit",
                                  uri="https://source.example/floorsheet/2026-11-20", digest=digest)
        xyz = next(r for r in rows if r["symbol"] == "XYZ")
        self.assertEqual(xyz["trade_status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
