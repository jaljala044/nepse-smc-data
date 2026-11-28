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

if __name__=="__main__":
    unittest.main()
