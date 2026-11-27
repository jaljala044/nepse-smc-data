import csv
import tempfile
import unittest
from pathlib import Path
from scanner_inputs.lifecycle_identity_holds import EXPECTED_SYMBOLS, load_lifecycle_holds
from scanner_inputs.historical_quarantine import reject_held, validate_rows
from scanner_inputs.prepare_scanner_inputs import validate_floorsheet, validate_broker_table

class LifecycleIdentityHoldTests(unittest.TestCase):
    def test_register_loads_all_26_as_symbol_wide_holds(self):
        holds = load_lifecycle_holds()
        self.assertEqual(len(holds), 26)
        self.assertEqual({symbol for symbol, day in holds if day == "*"}, EXPECTED_SYMBOLS)
        with self.assertRaisesRegex(ValueError, "Quarantined lifecycle identity"):
            reject_held("JALPA", "2020-01-02", holds)

    def test_unlisted_symbol_is_not_blocked_by_lifecycle_register(self):
        reject_held("NOTINREGISTER", "2026-11-26", load_lifecycle_holds())


    def test_daily_ohlcv_path_rejects_symbol_wide_hold(self):
        with self.assertRaisesRegex(ValueError, "Quarantined lifecycle identity"):
            validate_rows([{"symbol": "jalpa", "date": "2026-11-26"}], load_lifecycle_holds())

    def test_floorsheet_path_rejects_symbol_wide_hold(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "floorsheet.csv"
            path.write_text("""Contract_No,date,Symbol,Buyer,Seller,Quantity,Rate,Amount
20261126001,2026-11-26,JALPA,6,7,10,100,1000
""")
            with self.assertRaisesRegex(ValueError, "Quarantined lifecycle identity"):
                validate_floorsheet(path, set(), load_lifecycle_holds())

    def test_broker_summary_path_rejects_symbol_wide_hold(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broker_summary.csv"
            path.write_text("""symbol,date,broker,buy_qty,sell_qty,buy_value,sell_value
JALPA,2026-11-26,6,10,0,1000,0
""")
            with self.assertRaisesRegex(ValueError, "Quarantined lifecycle identity"):
                validate_broker_table(path, set(), load_lifecycle_holds())

    def test_missing_register_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                load_lifecycle_holds(Path(tmp) / "missing.csv")

    def test_incomplete_register_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.csv"
            with path.open("w", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=["symbol", "disposition", "effective_date_confidence"])
                writer.writeheader()
                writer.writerow({"symbol": "JALPA", "disposition": "HOLD_UNKNOWN", "effective_date_confidence": "none"})
            with self.assertRaisesRegex(ValueError, "coverage mismatch"):
                load_lifecycle_holds(path)

    def test_non_hold_or_verified_row_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.csv"
            with path.open("w", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=["symbol", "disposition", "effective_date_confidence"])
                writer.writeheader()
                for symbol in sorted(EXPECTED_SYMBOLS):
                    writer.writerow({"symbol": symbol, "disposition": "HOLD_UNKNOWN", "effective_date_confidence": "none"})
                writer.writerow({"symbol": "EXTRA", "disposition": "PROMOTED", "effective_date_confidence": "verified"})
            with self.assertRaisesRegex(ValueError, "non-held"):
                load_lifecycle_holds(path)

if __name__ == "__main__":
    unittest.main()
