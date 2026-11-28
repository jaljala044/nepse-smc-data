import csv
import json
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scanner_inputs import prepare_scanner_inputs as prep

PRICE = ("open", "high", "low", "close", "volume")
KEY = ("symbol", "date")
BROKER = ("buy_qty", "sell_qty", "buy_value", "sell_value")
ROOT = Path(__file__).resolve().parents[2]

def price(symbol="ABC", day="2026-11-26", **changes):
    return dict(symbol=symbol,date=day,open="100",high="110",low="90",
                close="105",volume="1000", **{}) | changes

class DuplicateGateTests(unittest.TestCase):
    def test_identical_numeric_prices(self):
        self.assertEqual(len(list(prep.unique_rows(
            [price(),price(" abc ",close="105.00")],KEY,PRICE))),1)

    def test_conflicting_prices_rejected(self):
        with self.assertRaisesRegex(ValueError,"Conflicting duplicate"):
            list(prep.unique_rows([price(),price(close="106")],KEY,PRICE))

    def test_same_price_different_session_preserved(self):
        self.assertEqual(len(list(prep.unique_rows(
            [price(),price(day="2026-11-27")],KEY,PRICE))),2)

    def test_invalid_dates_and_nonfinite_values(self):
        for row in [price(day="20261126"),price(volume="NaN"),price(high="Infinity")]:
            with self.subTest(row=row), self.assertRaises(ValueError):
                list(prep.unique_rows([row],KEY,PRICE))

    def test_broker_normalization(self):
        a=dict(symbol="ABC",date="2026-11-26",broker="01",buy_qty="10",
               sell_qty="5",buy_value="1000",sell_value="500")
        b=dict(a,broker="1",buy_value="1000.00")
        fields=KEY+("broker",)
        self.assertEqual(len(list(prep.unique_rows([a,b],fields,BROKER))),1)
        with self.assertRaises(ValueError):
            list(prep.unique_rows([a,dict(b,sell_qty="6")],fields,BROKER))

    def test_original_data_unchanged_and_failed_output_absent(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            original=root/"original"
            original.mkdir()
            path=original/"daily_prices.csv"
            prep.write(path,KEY+PRICE,[price(),price(close="106")])
            before=path.read_bytes()
            with self.assertRaises(ValueError):
                prep.prepare(original,root/"output")
            self.assertEqual(path.read_bytes(),before)
            self.assertFalse((root/"output").exists())

    def test_quarantine_manifest_matches_raw_payloads(self):
        manifest=json.loads((ROOT/"reference/P443_CROSS_REPOSITORY_DATE_QUARANTINE_2026-11-28.json").read_text())
        self.assertEqual(len(manifest["records"]),4)
        for record in manifest["records"]:
            raw=(ROOT/record["path"]).read_bytes()
            sha=hashlib.sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest()
            self.assertEqual(sha,record["blob_sha"])
            rows=json.loads(raw)["floorsheets"]["content"]
            self.assertEqual(len(rows),500)
            self.assertEqual({x["businessDate"] for x in rows},{"2026-11-26"})
            self.assertNotIn(record["requested_date"],record["actual_dates"])
            self.assertFalse(record["canonical_ingestion_allowed"])

    def test_prepare_preserves_raw_inputs_and_duplicate_disposition_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            original = root / "original"
            supplement = root / "supplement"
            original.mkdir()
            (supplement / "price_gap_fills").mkdir(parents=True)
            (supplement / "broker_summary").mkdir()
            (supplement / "benchmark_daily.csv").write_text(
                "symbol,date,open,high,low,close,volume\n"
                "ABC,2026-11-26,100,110,90,105,1000\n", encoding="utf-8")
            daily_bytes = (
                "symbol,date,open,high,low,close,volume\n"
                "ABC,2026-11-26,100,110,90,105,1000\n"
                " abc ,2026-11-26,100,110,90,105.00,1000\n"
            ).encode()
            broker_bytes = (
                "symbol,date,broker,buy_qty,sell_qty,buy_value,sell_value\n"
                "ABC,2026-11-26,01,10,5,1000,500\n"
                "ABC,2026-11-26,1,10,5,1000.00,500\n"
            ).encode()
            (original / "daily_prices.csv").write_bytes(daily_bytes)
            (original / "broker_summary.csv").write_bytes(broker_bytes)
            for name in ("sectors.csv", "sector_data.csv", "corporate_actions.csv"):
                (original / name).write_text("symbol\n", encoding="utf-8")
            output = root / "prepared"
            with patch.object(prep, "SUPPLEMENT", supplement):
                prep.prepare(original, output)
            raw_dir = output / "evidence" / "raw_inputs"
            self.assertEqual((raw_dir / "original_daily_prices.csv").read_bytes(), daily_bytes)
            self.assertEqual((raw_dir / "original_broker_summary.csv").read_bytes(), broker_bytes)
            manifest = json.loads((output / "evidence" / "duplicate_disposition_manifest.json").read_text())
            self.assertFalse(manifest["canonical_promotion_allowed"])
            self.assertEqual(len(manifest["raw_artifacts"]), 3)
            collapsed = [row for row in manifest["records"]
                         if row["disposition"] == "duplicate_identical_collapsed"]
            self.assertEqual(len(collapsed), 2)
            self.assertEqual({row["source_row_number"] for row in collapsed}, {3})
            overlaps = [row for row in manifest["records"]
                        if row["disposition"] == "duplicate_identical_overlap_skipped"]
            self.assertEqual(len(overlaps), 1)
            self.assertEqual(overlaps[0]["source_path"], "benchmark_daily.csv")

    def test_cross_partition_broker_dispositions(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            original = root / "original"
            original.mkdir()
            supplement = root / "supplement"
            (supplement / "price_gap_fills").mkdir(parents=True)
            (supplement / "broker_summary").mkdir()
            prep.write(original / "daily_prices.csv", KEY + PRICE, [price()])
            prep.write(supplement / "benchmark_daily.csv", KEY + PRICE, [price()])
            for name in ("sectors.csv", "sector_data.csv", "corporate_actions.csv"):
                (original / name).write_text("symbol\n", encoding="utf-8")
            fields = KEY + ("broker",) + BROKER
            a = dict(symbol="ABC", date="2026-11-26", broker="01", buy_qty="10",
                     sell_qty="5", buy_value="1000", sell_value="500")
            prep.write(supplement / "broker_summary" / "a.csv", fields, [a])
            prep.write(supplement / "broker_summary" / "b.csv", fields, [dict(a, broker="1")])
            with patch.object(prep, "SUPPLEMENT", supplement):
                prep.prepare(original, root / "out")
                self.assertEqual(len(list(prep.rows(root / "out" / "broker_summary.csv"))), 1)
                manifest = json.loads((root / "out" / "evidence" / "duplicate_disposition_manifest.json").read_text())
                broker_rows = [row for row in manifest["records"] if row["source_path"].startswith("broker_summary/")]
                self.assertEqual([row["disposition"] for row in broker_rows],
                                 ["retained", "duplicate_identical_collapsed"])
                prep.write(supplement / "broker_summary" / "b.csv", fields, [dict(a, sell_qty="6")])
                with self.assertRaisesRegex(ValueError, "Conflicting duplicate"):
                    prep.prepare(original, root / "conflict")
                self.assertFalse((root / "conflict").exists())

if __name__=="__main__":
    unittest.main()
