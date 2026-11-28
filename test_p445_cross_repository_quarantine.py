import csv
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scanner_inputs import canonical_publication as publication
from scanner_inputs import prepare_scanner_inputs as staging

ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "reference" / "P443_CROSS_REPOSITORY_DATE_QUARANTINE_2026-11-28.json"


def git_blob_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + bytes([0]) + raw).hexdigest()


def one_trade_csv(trade, day=None):
    fields = ["Contract_No", "Symbol", "Buyer", "Seller", "Quantity", "Rate", "Amount"]
    if day is not None:
        fields.append("date")
    row = {
        "Contract_No": str(trade["contractId"]),
        "Symbol": trade["stockSymbol"],
        "Buyer": str(trade["buyerMemberId"]),
        "Seller": str(trade["sellerMemberId"]),
        "Quantity": str(trade["contractQuantity"]),
        "Rate": str(trade["contractRate"]),
        "Amount": str(trade["contractAmount"]),
    }
    if day is not None:
        row["date"] = day
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    writer.writerow(row)
    return stream.getvalue().encode("utf-8")


class CrossRepositoryWrongSessionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_manifest_pins_all_four_wrong_session_payloads(self):
        records = self.manifest["records"]
        self.assertEqual(len(records), 4)
        self.assertEqual(len({record["path"] for record in records}), 4)
        self.assertEqual({record["blob_sha"] for record in records}, {"732e3365b4304f7696a9d30dcd2e94451535caf8"})
        for record in records:
            with self.subTest(requested_date=record["requested_date"]):
                self.assertEqual(record["classification"], "wrong_session_response")
                self.assertFalse(record["canonical_ingestion_allowed"])
                self.assertTrue(record["retain_raw"])
                self.assertNotIn(record["requested_date"], record["actual_dates"])
                raw = (ROOT / record["path"]).read_bytes()
                self.assertEqual(git_blob_sha(raw), record["blob_sha"])
                payload = json.loads(raw)
                trades = payload["floorsheets"]["content"]
                self.assertEqual(len(trades), record["rows"])
                self.assertEqual({row["businessDate"] for row in trades}, set(record["actual_dates"]))
                self.assertEqual(len({str(row["contractId"]) for row in trades}), record["unique_contracts"])
                self.assertEqual(record["rows"], 500)
                self.assertEqual(record["unique_contracts"], 500)

    def test_wrong_requested_dates_rejected_by_staged_floorsheet_validator(self):
        for record in self.manifest["records"]:
            with self.subTest(requested_date=record["requested_date"]), tempfile.TemporaryDirectory() as tmp:
                payload = json.loads((ROOT / record["path"]).read_text(encoding="utf-8"))
                trade = payload["floorsheets"]["content"][0]
                path = Path(tmp) / f"floorsheet_{record['requested_date']}.csv"
                path.write_bytes(one_trade_csv(trade, record["requested_date"]))
                with self.assertRaisesRegex(ValueError, "Contract session prefix does not match row date"):
                    staging.validate_floorsheet(path, set())

    def test_wrong_requested_dates_rejected_by_canonical_publisher(self):
        for record in self.manifest["records"]:
            with self.subTest(requested_date=record["requested_date"]), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                payload = json.loads((ROOT / record["path"]).read_text(encoding="utf-8"))
                trade = payload["floorsheets"]["content"][0]
                raw = one_trade_csv(trade)
                destination = root / f"floorsheet_{record['requested_date']}.csv"
                with patch.object(publication, "load_holds", return_value={}):
                    with patch.object(publication, "load_equity_holds", return_value={}):
                        with patch.object(publication, "load_lifecycle_holds", return_value={}):
                            with patch.object(publication, "verified_closed_dates", return_value=set()):
                                with self.assertRaisesRegex(ValueError, "Contract session not established"):
                                    publication.publish_daily_floorsheet(
                                        raw, record["requested_date"], destination, root / "overlay.csv",
                                        control_path=root / "control.json", evidence_path=root / "evidence.json")
                self.assertFalse(destination.exists())

    def test_actual_session_prefix_is_accepted_by_staged_validator(self):
        record = self.manifest["records"][0]
        payload = json.loads((ROOT / record["path"]).read_text(encoding="utf-8"))
        trade = payload["floorsheets"]["content"][0]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "floorsheet_2026-11-26.csv"
            path.write_bytes(one_trade_csv(trade, "2026-11-26"))
            staging.validate_floorsheet(path, set())

    def test_non_date_coded_contract_is_not_reinterpreted(self):
        trade = {
            "contractId": "ABC-001", "stockSymbol": "ABC", "buyerMemberId": "1",
            "sellerMemberId": "2", "contractQuantity": 10,
            "contractRate": 100, "contractAmount": 1000,
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "floorsheet_2024-05-16.csv"
            path.write_bytes(one_trade_csv(trade, "2024-05-16"))
            staging.validate_floorsheet(path, set())


if __name__ == "__main__":
    unittest.main()
