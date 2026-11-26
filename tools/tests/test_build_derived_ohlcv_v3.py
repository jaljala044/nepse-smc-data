import csv
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from build_derived_ohlcv_v3 import build


def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def write_csv(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


class DerivedOhlcvV3Tests(unittest.TestCase):
    def fixture(self, root):
        v2, raw = root / "v2", root / "raw"
        v2.mkdir()
        raw.mkdir()
        files = {
            "TEST": b"Date,Open,High,Low,Close,Volume\n2026-04-24,449.9,449.8,440.5,445.1,4553\n2026-04-25,446,450,440,448,1000\n",
            "OTHER": b"Date,Open,High,Low,Close,Volume\n2026-04-24,100,105,98,103,1000\n",
        }
        manifest = []
        for symbol, data in files.items():
            (raw / f"{symbol}_OHLCV.csv").write_bytes(data)
            (v2 / f"{symbol}_OHLCV.csv").write_bytes(data)
            manifest.append({
                "symbol": symbol, "raw_source_blob_sha": blob(data),
                "derived_blob_sha": blob(data), "rows": len(data.decode().splitlines()) - 1,
            })
        write_csv(v2 / "manifest.csv", list(manifest[0]), manifest)
        write_csv(v2 / "corrections.csv",
                  ["symbol","date","field","raw_value","derived_value","source","source_url","reason","status"], [])
        write_csv(v2 / "provenance_ledger.csv",
                  ["symbol","official_business_date","official_open"], [])
        matrix_row = {
            "symbol":"TEST", "business_date":"2026-04-24",
            "candidate_open":"449.9", "candidate_high":"449.8", "candidate_low":"440.5",
            "candidate_close":"445.1", "candidate_volume":"4553",
            "official_open":"445.0", "official_high":"449.8", "official_low":"440.5",
            "official_close":"445.1", "official_volume":"4553", "official_turnover":"2022210.3",
            "official_capture_status":"OFFICIAL_CAPTURE_ACCEPTED", "official_row_count":"1",
            "official_quality_flags":"", "official_security_id":"180", "mapping_security_id":"180",
            "official_payload_sha256":"payloadhash",
            "official_source_url":"https://www.nepalstock.com/api/nots/nepse-data/today-price?businessDate=2026-04-24",
            "official_retrieved_at":"2026-11-26T23:00:00+05:45",
        }
        matrix = root / "matrix.csv"
        write_csv(matrix, list(matrix_row), [matrix_row])
        correction_row = {
            "symbol":"TEST", "business_date":"2026-04-24", "field":"Open",
            "candidate_value":"449.9", "official_value":"445.0", "official_security_id":"180",
            "official_quality_flags":"", "official_payload_sha256":"payloadhash",
            "official_source_url":matrix_row["official_source_url"],
            "official_retrieved_at":matrix_row["official_retrieved_at"],
            "disposition":"PRIMARY_OFFICIAL_NEPSE_EOD_OPEN_CORRECTION",
        }
        correction = root / "corrections.csv"
        write_csv(correction, list(correction_row), [correction_row])
        return v2, raw, matrix, correction, files

    def test_applies_only_supported_open_and_preserves_v2_and_raw(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            v2, raw, matrix, correction, files = self.fixture(root)
            v2_before = {p.name:p.read_bytes() for p in v2.glob("*_OHLCV.csv")}
            raw_before = {p.name:p.read_bytes() for p in raw.glob("*_OHLCV.csv")}
            out = root / "ohlcv_v3"
            totals = build(v2, raw, matrix, correction, out, expected_symbols=2, expected_corrections=1)
            rows = list(csv.DictReader((out / "TEST_OHLCV.csv").open()))
            self.assertEqual(rows[0]["Open"], "445.0")
            self.assertEqual(rows[0]["High"], "449.8")
            self.assertEqual(rows[0]["Close"], "445.1")
            self.assertEqual((out / "OTHER_OHLCV.csv").read_bytes(), files["OTHER"])
            self.assertEqual({p.name:p.read_bytes() for p in v2.glob("*_OHLCV.csv")}, v2_before)
            self.assertEqual({p.name:p.read_bytes() for p in raw.glob("*_OHLCV.csv")}, raw_before)
            self.assertEqual(totals["official_open_corrections_applied"], 1)
            self.assertEqual(totals["v2_source_files_modified"], 0)

    def test_rejects_duplicate_correction_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            v2, raw, matrix, correction, _ = self.fixture(root)
            row = list(csv.DictReader(correction.open()))[0]
            write_csv(correction, list(row), [row, row])
            with self.assertRaises(ValueError):
                build(v2, raw, matrix, correction, root / "ohlcv_v3", expected_symbols=2, expected_corrections=2)

    def test_rejects_unaccepted_official_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            v2, raw, matrix, correction, _ = self.fixture(root)
            row = list(csv.DictReader(matrix.open()))[0]
            row["official_capture_status"] = "NO_OFFICIAL_ROW"
            write_csv(matrix, list(row), [row])
            with self.assertRaises(ValueError):
                build(v2, raw, matrix, correction, root / "ohlcv_v3", expected_symbols=2, expected_corrections=1)


if __name__ == "__main__":
    unittest.main()
