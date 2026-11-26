import csv
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from audit_p428_official_eod_batch import build


def write_csv(path, header, rows):
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        writer.writerows(rows)


class P428OfficialEodBatchTests(unittest.TestCase):
    def make_fixture(self, root, official_row):
        queue = root / "queue.csv"
        write_csv(queue, [
            "symbol", "date", "status", "calendar_status", "open", "high",
            "low", "close", "volume", "turnover", "external_sha256", "derived_sha256"
        ], [[
            "TEST", "2026-03-01", "ALREADY_RECOVERED_DATE_SHIFT",
            "verified_open_observed", "100", "105", "98", "103", "1000",
            "102000", "extsha", "derivedsha"
        ]])

        mapping = root / "mapping.csv"
        write_csv(mapping, ["symbol", "security_id", "security_name", "active_status", "snapshot_date"], [
            ["TEST", "1234", "Test Limited", "A", "2026-11-25"]
        ])

        capture_dir = root / "captures"
        day_dir = capture_dir / "2026-03-01"
        day_dir.mkdir(parents=True)
        url = "https://www.nepalstock.com/api/nots/nepse-data/today-price?size=500&page=0&businessDate=2026-03-01"
        payload = {
            "totalElements": 1,
            "totalPages": 1,
            "number": 0,
            "size": 500,
            "content": [official_row],
        }
        raw = json.dumps(payload).encode("utf-8")
        page_path = day_dir / "page_0.json"
        page_path.write_bytes(raw)
        manifest = {
            "status": "COMPLETE_BOARD_CAPTURE",
            "business_date": "2026-03-01",
            "total_pages": 1,
            "total_elements": 1,
            "captured_pages": [{
                "page": 0,
                "file": str(page_path),
                "url": url,
                "retrieved_at": "2026-03-02T10:00:00+05:45",
                "http_status": 200,
                "content_type": "application/json",
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "rows": 1,
            }],
        }
        (day_dir / "capture_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        return queue, mapping, capture_dir

    def test_official_row_exact_match_is_confirmed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            official = {
                "businessDate": "2026-03-01T00:00:00",
                "securityId": 1234,
                "symbol": "TEST",
                "openPrice": 100,
                "highPrice": 105,
                "lowPrice": 98,
                "closePrice": 103,
                "totalTradedQuantity": 1000,
                "totalTradedValue": 102000,
                "totalTrades": 10,
            }
            queue, mapping, captures = self.make_fixture(root, official)
            rows = build(queue, mapping, captures, root / "out.csv", expected_count=1)
            self.assertEqual(rows[0]["official_capture_status"], "OFFICIAL_CAPTURE_ACCEPTED")
            self.assertEqual(rows[0]["official_ohlcv_match"], "TRUE")
            self.assertEqual(rows[0]["disposition"], "OFFICIAL_ROW_MATCHES_CANDIDATE")

    def test_official_row_different_but_valid_is_not_silently_equal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            official = {
                "businessDate": "2026-03-01T00:00:00",
                "securityId": 1234,
                "symbol": "TEST",
                "openPrice": 100,
                "highPrice": 106,
                "lowPrice": 98,
                "closePrice": 104,
                "totalTradedQuantity": 1200,
                "totalTradedValue": 124000,
                "totalTrades": 11,
            }
            queue, mapping, captures = self.make_fixture(root, official)
            rows = build(queue, mapping, captures, root / "out.csv", expected_count=1)
            self.assertEqual(rows[0]["official_capture_status"], "OFFICIAL_CAPTURE_ACCEPTED")
            self.assertEqual(rows[0]["official_ohlcv_match"], "FALSE")
            self.assertEqual(rows[0]["disposition"], "OFFICIAL_ROW_DIFFERS_CANDIDATE")

    def test_invalid_official_row_requires_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            official = {
                "businessDate": "2026-03-01T00:00:00",
                "securityId": 1234,
                "symbol": "TEST",
                "openPrice": 110,
                "highPrice": 105,
                "lowPrice": 98,
                "closePrice": 103,
                "totalTradedQuantity": 1000,
                "totalTradedValue": 102000,
                "totalTrades": 10,
            }
            queue, mapping, captures = self.make_fixture(root, official)
            rows = build(queue, mapping, captures, root / "out.csv", expected_count=1)
            self.assertEqual(rows[0]["official_capture_status"], "OFFICIAL_CAPTURE_REVIEW_REQUIRED")
            self.assertEqual(rows[0]["disposition"], "OFFICIAL_CAPTURE_REVIEW_REQUIRED")


if __name__ == "__main__":
    unittest.main()
