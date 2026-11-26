import csv
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from build_p428_official_eod_corrections import build


class P428OfficialCorrectionLedgerTests(unittest.TestCase):
    def write_matrix(self, path, rows):
        fields = [
            "symbol", "business_date", "candidate_status", "official_ohlcv_match",
            "official_capture_status", "official_quality_flags", "official_security_id",
            "mapping_security_id", "candidate_open", "candidate_high", "candidate_low",
            "candidate_close", "candidate_volume", "candidate_turnover",
            "official_open", "official_high", "official_low", "official_close",
            "official_volume", "official_turnover", "official_trades",
            "official_payload_sha256", "official_source_url", "official_retrieved_at",
        ]
        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def test_open_and_close_corrections_are_emitted_with_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            matrix = root / "matrix.csv"
            base = {
                "candidate_status": "QUARANTINE_INVALID_EXTERNAL_OHLCV",
                "official_ohlcv_match": "FALSE",
                "official_capture_status": "OFFICIAL_CAPTURE_ACCEPTED",
                "official_quality_flags": "",
                "official_security_id": "123",
                "mapping_security_id": "123",
                "candidate_high": "105", "candidate_low": "98",
                "candidate_close": "103", "candidate_volume": "1000",
                "candidate_turnover": "102000",
                "official_high": "105", "official_low": "98",
                "official_close": "103", "official_volume": "1000",
                "official_turnover": "102000", "official_trades": "10",
                "official_payload_sha256": "payloadsha",
                "official_source_url": "https://www.nepalstock.com/api/nots/nepse-data/today-price?businessDate=2026-03-01",
                "official_retrieved_at": "2026-03-02T10:00:00+05:45",
            }
            open_row = {**base, "symbol": "TEST", "business_date": "2026-03-01",
                        "candidate_open": "110", "official_open": "100"}
            close_row = {**base, "symbol": "TEST2", "business_date": "2026-03-01",
                         "candidate_status": "ALREADY_RECOVERED_DATE_SHIFT",
                         "candidate_open": "100", "official_open": "100",
                         "candidate_close": "103", "official_close": "104",
                         "official_high": "106", "candidate_high": "106"}
            self.write_matrix(matrix, [open_row, close_row])
            output = root / "corrections.csv"
            rows = build(matrix, output, expected_count=2)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["changed_fields"], "open")
            self.assertEqual(rows[1]["changed_fields"], "close")
            self.assertTrue(all(r["disposition"] == "PRIMARY_OFFICIAL_NEPSE_EOD_CORRECTION" for r in rows))

    def test_quality_flags_block_correction(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            matrix = root / "matrix.csv"
            row = {
                "symbol": "TEST", "business_date": "2026-03-01",
                "candidate_status": "QUARANTINE_INVALID_EXTERNAL_OHLCV",
                "official_ohlcv_match": "FALSE",
                "official_capture_status": "OFFICIAL_CAPTURE_REVIEW_REQUIRED",
                "official_quality_flags": "open_outside_range",
                "official_security_id": "123", "mapping_security_id": "123",
                "candidate_open": "110", "candidate_high": "105", "candidate_low": "98",
                "candidate_close": "103", "candidate_volume": "1000", "candidate_turnover": "102000",
                "official_open": "110", "official_high": "105", "official_low": "98",
                "official_close": "103", "official_volume": "1000", "official_turnover": "102000",
                "official_trades": "10", "official_payload_sha256": "payloadsha",
                "official_source_url": "https://www.nepalstock.com/api/nots/nepse-data/today-price?businessDate=2026-03-01",
                "official_retrieved_at": "2026-03-02T10:00:00+05:45",
            }
            self.write_matrix(matrix, [row])
            with self.assertRaises(ValueError):
                build(matrix, root / "corrections.csv", expected_count=1)


if __name__ == "__main__":
    unittest.main()
