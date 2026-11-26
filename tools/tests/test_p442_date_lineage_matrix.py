import csv
import datetime as dt
import hashlib
from collections import Counter
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "reference" / "p442_sharesansar_date_lineage_matrix_2026-11-26.csv"
EXPECTED_RAW_BLOBS = {
    "NMLBBL": "8dd19774b8409d0d67c94f9976fc079a5518d770",
    "SMPDA": "044d6f823b0d93c64c0906edfe00e284945fbc6f",
}
EXPECTED_OFFSETS_PER_SYMBOL = {1: 37, 2: 31, 3: 9, 4: 3, 5: 1}


def git_blob_sha(path):
    data = path.read_bytes()
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


class P442DateLineageMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with MATRIX.open(newline="", encoding="utf-8") as stream:
            cls.rows = list(csv.DictReader(stream))

    def test_all_162_symbol_date_rows_have_unique_identity(self):
        self.assertEqual(len(self.rows), 162)
        keys = [(r["symbol"], r["canonical_date"]) for r in self.rows]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(Counter(r["symbol"] for r in self.rows), {
            "NMLBBL": 81,
            "SMPDA": 81,
        })

    def test_every_row_matches_pinned_upstream_source_ohlcv(self):
        for row in self.rows:
            with self.subTest(symbol=row["symbol"], date=row["canonical_date"]):
                self.assertEqual(row["source_row_present"], "true")
                self.assertEqual(row["source_ohlcv_exact"], "true")
                self.assertEqual(row["source_hlc_volume_exact"], "true")
                self.assertEqual(row["source_date_column_present"], "false")
                self.assertTrue(row["source_blob_sha"])
                self.assertEqual(
                    row["source_path"],
                    "docs/Data/" + row["canonical_date"].replace("-", "_") + ".csv",
                )

    def test_each_scrape_date_tuple_maps_to_one_other_official_date(self):
        for row in self.rows:
            with self.subTest(symbol=row["symbol"], date=row["canonical_date"]):
                self.assertEqual(int(row["official_tuple_match_count"]), 1)
                self.assertEqual(row["official_match_dates"], row["nearest_official_date"])
                self.assertNotEqual(row["canonical_date"], row["nearest_official_date"])
                offset = (
                    dt.date.fromisoformat(row["canonical_date"])
                    - dt.date.fromisoformat(row["nearest_official_date"])
                ).days
                self.assertEqual(offset, int(row["offset_days"]))
                self.assertIn(offset, EXPECTED_OFFSETS_PER_SYMBOL)

    def test_offset_histogram_is_stable_per_symbol(self):
        for symbol in EXPECTED_RAW_BLOBS:
            with self.subTest(symbol=symbol):
                histogram = Counter(
                    int(r["offset_days"]) for r in self.rows if r["symbol"] == symbol
                )
                self.assertEqual(dict(histogram), EXPECTED_OFFSETS_PER_SYMBOL)

    def test_upstream_daily_file_manifest_is_complete_and_pinned(self):
        self.assertEqual(len({r["source_path"] for r in self.rows}), 81)
        self.assertEqual(len({r["source_blob_sha"] for r in self.rows}), 37)
        for date in {r["canonical_date"] for r in self.rows}:
            shas = {
                r["source_blob_sha"]
                for r in self.rows
                if r["canonical_date"] == date
            }
            self.assertEqual(len(shas), 1)

    def test_raw_ohlcv_files_remain_byte_identical(self):
        for symbol, expected in EXPECTED_RAW_BLOBS.items():
            path = ROOT / "03_stock_charts_ohlcv" / f"{symbol}_OHLCV.csv"
            with self.subTest(symbol=symbol):
                self.assertEqual(git_blob_sha(path), expected)


if __name__ == "__main__":
    unittest.main()
