import csv
import json
import tempfile
import unittest
from pathlib import Path

from tools.p444_audit_repeat_pair_capture_coverage import audit


class RepeatPairCaptureCoverageTests(unittest.TestCase):
    def make_inputs(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        base = Path(temp.name)
        matrix = base / "matrix.csv"
        with matrix.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=[
                "pair_id", "symbol", "previous_date", "current_date"
            ])
            writer.writeheader()
            writer.writerow({
                "pair_id": "p1", "symbol": "MATCH",
                "previous_date": "2026-11-25", "current_date": "2026-11-26"
            })
            writer.writerow({
                "pair_id": "p2", "symbol": "MATCH",
                "previous_date": "2026-11-26", "current_date": "2026-11-27"
            })
            writer.writerow({
                "pair_id": "p3", "symbol": "OLDTICKER",
                "previous_date": "2026-11-25", "current_date": "2026-11-26"
            })
        root = base / "symbols"
        payload_dir = root / "MATCH"
        payload_dir.mkdir(parents=True)
        rows = []
        for day, trades in (("2026-11-25", 12), ("2026-11-26", 0)):
            rows.append({
                "businessDate": day,
                "totalTrades": trades,
                "totalTradedQuantity": 100,
                "totalTradedValue": 1234.5,
            })
        (payload_dir / "response-01.bin").write_text(
            json.dumps({"content": rows}), encoding="utf-8"
        )
        successor_dir = root / "SUCCESSOR"
        successor_dir.mkdir()
        (successor_dir / "response-01.bin").write_text(
            json.dumps({"content": rows}), encoding="utf-8"
        )
        return matrix, root

    def test_exact_symbol_and_date_coverage_only(self):
        matrix, root = self.make_inputs()
        result = audit(matrix, root)
        self.assertEqual(result["matrix_pair_rows"], 3)
        self.assertEqual(result["matrix_symbols"], 2)
        self.assertEqual(result["capture_symbols"], 2)
        self.assertEqual(result["exact_symbol_intersection"], ["MATCH"])
        self.assertEqual(result["endpoint_occurrences_total"], 6)
        self.assertEqual(result["endpoint_occurrences_covered"], 3)
        self.assertEqual(result["pairs_with_both_endpoints_covered"], 1)
        self.assertFalse(result["promotion_allowed"])
        old = next(x for x in result["symbol_reports"] if x["symbol"] == "OLDTICKER")
        self.assertFalse(old["exact_symbol_capture_match"])
        self.assertEqual(old["covered_unique_endpoint_dates"], 0)

    def test_missing_matrix_fields_fail_closed(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        matrix = Path(temp.name) / "matrix.csv"
        matrix.write_text("pair_id,symbol\np1,MATCH\n", encoding="utf-8")
        root = Path(temp.name) / "symbols"
        root.mkdir()
        with self.assertRaisesRegex(ValueError, "missing required fields"):
            audit(matrix, root)


if __name__ == "__main__":
    unittest.main()
