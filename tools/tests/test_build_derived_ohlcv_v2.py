import csv
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from build_derived_ohlcv_v2 import build


def git_blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def write_csv(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


class DerivedOhlcvV2Tests(unittest.TestCase):
    def test_shift_and_insert_use_official_rows_without_touching_raw(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            v1 = root / "v1"
            raw = root / "raw"
            v1.mkdir()
            raw.mkdir()
            shift_bytes = (
                "Date,Open,High,Low,Close,Volume\n"
                "2026-03-02,100,105,98,103,1000\n"
            ).encode()
            insert_bytes = (
                "Date,Open,High,Low,Close,Volume\n"
                "2026-04-23,100,105,98,103,1000\n"
            ).encode()
            for symbol, data in [("TEST", shift_bytes), ("TEST2", insert_bytes)]:
                (raw / f"{symbol}_OHLCV.csv").write_bytes(data)
                (v1 / f"{symbol}_OHLCV.csv").write_bytes(data)

            manifest_fields = [
                "symbol", "raw_source_path", "raw_source_blob_sha", "derived_path",
                "derived_blob_sha", "rows", "derivation_status", "correction_count"
            ]
            manifest = []
            for symbol, data, count in [("TEST", shift_bytes, 1), ("TEST2", insert_bytes, 1)]:
                manifest.append({
                    "symbol": symbol,
                    "raw_source_path": f"03_stock_charts_ohlcv/{symbol}_OHLCV.csv",
                    "raw_source_blob_sha": git_blob_sha(data),
                    "derived_path": f"derived/ohlcv_v1/{symbol}_OHLCV.csv",
                    "derived_blob_sha": git_blob_sha(data),
                    "rows": count,
                    "derivation_status": "identical_to_raw",
                    "correction_count": 0,
                })
            write_csv(v1 / "manifest.csv", manifest_fields, manifest)
            write_csv(v1 / "corrections.csv",
                      ["symbol", "date", "field", "raw_value", "derived_value", "source", "source_url", "reason", "status"], [])

            matrix_fields = [
                "symbol", "business_date", "candidate_status", "candidate_open",
                "candidate_high", "candidate_low", "candidate_close", "candidate_volume",
                "candidate_turnover", "mapping_security_id", "official_security_id",
                "official_open", "official_high", "official_low", "official_close",
                "official_volume", "official_turnover", "official_trades",
                "official_capture_status", "official_quality_flags", "official_row_count",
                "official_payload_sha256", "official_source_url", "official_retrieved_at"
            ]
            common = {
                "candidate_high": "105", "candidate_low": "98", "candidate_close": "103",
                "candidate_volume": "1000", "candidate_turnover": "102000",
                "mapping_security_id": "123", "official_security_id": "123",
                "official_high": "105", "official_low": "98", "official_close": "103",
                "official_volume": "1000", "official_turnover": "102000", "official_trades": "10",
                "official_capture_status": "OFFICIAL_CAPTURE_ACCEPTED", "official_quality_flags": "",
                "official_row_count": "1", "official_payload_sha256": "payload-sha",
                "official_source_url": "https://www.nepalstock.com/api/nots/nepse-data/today-price?businessDate=2026-03-01",
                "official_retrieved_at": "2026-03-02T10:00:00+05:45",
            }
            rows = [
                {**common, "symbol": "TEST", "business_date": "2026-03-01",
                 "candidate_status": "ALREADY_RECOVERED_DATE_SHIFT",
                 "candidate_open": "100", "official_open": "100"},
                {**common, "symbol": "TEST2", "business_date": "2026-04-24",
                 "candidate_status": "QUARANTINE_INVALID_EXTERNAL_OHLCV",
                 "candidate_open": "110", "official_open": "100",
                 "official_source_url": "https://www.nepalstock.com/api/nots/nepse-data/today-price?businessDate=2026-04-24"},
            ]
            matrix = root / "official.csv"
            write_csv(matrix, matrix_fields, rows)
            calendar = root / "calendar.csv"
            write_csv(calendar, ["date", "status"], [
                {"date": "2026-03-01", "status": "verified_open_observed"},
                {"date": "2026-03-02", "status": "verified_closed"},
            ])

            raw_before = {p.name: p.read_bytes() for p in raw.glob("*_OHLCV.csv")}
            output = root / "ohlcv_v2"
            totals = build(v1, raw, matrix, calendar, output,
                           expected_official_rows=2, expected_symbols=2,
                           expected_shift_rows=1, expected_insert_rows=1)

            test_rows = list(csv.DictReader((output / "TEST_OHLCV.csv").open()))
            self.assertEqual([r["Date"] for r in test_rows], ["2026-03-01"])
            self.assertEqual(test_rows[0]["Close"], "103")
            test2_rows = list(csv.DictReader((output / "TEST2_OHLCV.csv").open()))
            self.assertEqual([r["Date"] for r in test2_rows], ["2026-04-23", "2026-04-24"])
            self.assertEqual(test2_rows[1]["Open"], "100")
            self.assertEqual({p.name: p.read_bytes() for p in raw.glob("*_OHLCV.csv")}, raw_before)
            self.assertEqual(len(list(csv.DictReader((output / "provenance_ledger.csv").open()))), 2)
            corrections = list(csv.DictReader((output / "corrections.csv").open()))
            self.assertEqual({r["field"] for r in corrections}, {"Date", "Row", "Open"})
            self.assertEqual(totals["raw_source_files_modified"], 0)
            self.assertEqual(totals["derived_rows"], 3)

    def test_rejects_shift_when_raw_row_does_not_match_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            v1 = root / "v1"
            raw = root / "raw"
            v1.mkdir()
            raw.mkdir()
            data = b"Date,Open,High,Low,Close,Volume\n2026-03-02,100,105,98,102,1000\n"
            (raw / "TEST_OHLCV.csv").write_bytes(data)
            (v1 / "TEST_OHLCV.csv").write_bytes(data)
            write_csv(v1 / "manifest.csv",
                ["symbol", "raw_source_path", "raw_source_blob_sha", "derived_path", "derived_blob_sha", "rows", "derivation_status", "correction_count"],
                [{"symbol":"TEST","raw_source_path":"raw","raw_source_blob_sha":git_blob_sha(data),"derived_path":"v1","derived_blob_sha":git_blob_sha(data),"rows":1,"derivation_status":"identical_to_raw","correction_count":0}])
            write_csv(v1 / "corrections.csv",
                ["symbol", "date", "field", "raw_value", "derived_value", "source", "source_url", "reason", "status"], [])
            fields=["symbol","business_date","candidate_status","candidate_open","candidate_high","candidate_low","candidate_close","candidate_volume","candidate_turnover","mapping_security_id","official_security_id","official_open","official_high","official_low","official_close","official_volume","official_turnover","official_trades","official_capture_status","official_quality_flags","official_row_count","official_payload_sha256","official_source_url","official_retrieved_at"]
            row={"symbol":"TEST","business_date":"2026-03-01","candidate_status":"ALREADY_RECOVERED_DATE_SHIFT","candidate_open":"100","candidate_high":"105","candidate_low":"98","candidate_close":"103","candidate_volume":"1000","candidate_turnover":"102000","mapping_security_id":"123","official_security_id":"123","official_open":"100","official_high":"105","official_low":"98","official_close":"103","official_volume":"1000","official_turnover":"102000","official_trades":"10","official_capture_status":"OFFICIAL_CAPTURE_ACCEPTED","official_quality_flags":"","official_row_count":"1","official_payload_sha256":"sha","official_source_url":"https://www.nepalstock.com/api/nots/nepse-data/today-price?businessDate=2026-03-01","official_retrieved_at":"2026-03-02T10:00:00+05:45"}
            matrix=root/"official.csv"
            write_csv(matrix,fields,[row])
            calendar=root/"calendar.csv"
            write_csv(calendar,["date","status"],[{"date":"2026-03-01","status":"verified_open_observed"},{"date":"2026-03-02","status":"verified_closed"}])
            with self.assertRaises(ValueError):
                build(v1,raw,matrix,calendar,root/"ohlcv_v2",expected_official_rows=1,expected_symbols=1,expected_shift_rows=1,expected_insert_rows=0)


if __name__ == "__main__":
    unittest.main()
