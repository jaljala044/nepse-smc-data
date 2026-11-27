"""Regression tests for exact repeat-pair lineage coverage auditing."""
import csv
import tempfile
import unittest
from pathlib import Path

from tools.p443_audit_repeat_lineage_coverage import audit


class RepeatLineageCoverageTests(unittest.TestCase):
    def make_csv(self, path, fields, rows):
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def test_exact_key_join_and_symbol_states(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pairs = root / "pairs.csv"
            lineage = root / "lineage.csv"
            pair_fields = [
                "path", "blob_sha", "symbol", "date", "row", "previous_date",
                "previous_row", "pair_classification",
            ]
            rows = [
                {"path":"ohlcv/AAA.csv","blob_sha":"abc","symbol":"AAA","date":"2025-01-02","row":"3","previous_date":"2025-01-01","previous_row":"2","pair_classification":"INSUFFICIENT_SESSION_EVIDENCE"},
                {"path":"ohlcv/AAA.csv","blob_sha":"abc","symbol":"AAA","date":"2025-01-03","row":"4","previous_date":"2025-01-02","previous_row":"3","pair_classification":"INSUFFICIENT_SESSION_EVIDENCE"},
                {"path":"ohlcv/BBB.csv","blob_sha":"def","symbol":"BBB","date":"2025-01-02","row":"3","previous_date":"2025-01-01","previous_row":"2","pair_classification":"BOTH_OPEN_TUPLE_UNVERIFIED"},
            ]
            self.make_csv(pairs, pair_fields, rows)
            self.make_csv(lineage, ["symbol","date","path","blob_sha","row"], [
                {"symbol":"AAA","date":"2025-01-02","path":"ohlcv/AAA.csv","blob_sha":"abc","row":"3"},
                {"symbol":"OUTSIDE","date":"2025-01-04","path":"ohlcv/OUTSIDE.csv","blob_sha":"xyz","row":"5"},
            ])
            result = audit(pairs, lineage)
            self.assertEqual(result["pair_rows"], 3)
            self.assertEqual(result["exact_intersection"], 1)
            self.assertEqual(result["uncovered_pair_keys"], 2)
            self.assertEqual(result["lineage_keys_outside_pair_set"], 1)
            self.assertEqual(result["symbol_coverage_states"], {
                "NO_LINEAGE": 1, "PARTIAL_LINEAGE": 1
            })
            self.assertEqual(
                [(r["symbol"], r["date"]) for r in result["missing_pair_rows"]],
                [("AAA","2025-01-03"),("BBB","2025-01-02")],
            )
            self.assertFalse(result["promotion_allowed"])
            self.assertFalse(result["canonical_data_modified"])

    def test_duplicate_pair_keys_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pairs = root / "pairs.csv"
            lineage = root / "lineage.csv"
            pair_fields = [
                "path", "blob_sha", "symbol", "date", "row", "previous_date",
                "previous_row", "pair_classification",
            ]
            row = {"path":"ohlcv/AAA.csv","blob_sha":"abc","symbol":"AAA","date":"2025-01-02","row":"3","previous_date":"2025-01-01","previous_row":"2","pair_classification":"INSUFFICIENT_SESSION_EVIDENCE"}
            self.make_csv(pairs, pair_fields, [row, row])
            self.make_csv(lineage, ["symbol","date","path","blob_sha","row"], [])
            with self.assertRaisesRegex(ValueError, "duplicate key"):
                audit(pairs, lineage)

    def test_invalid_dates_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pairs = root / "pairs.csv"
            lineage = root / "lineage.csv"
            pair_fields = [
                "path", "blob_sha", "symbol", "date", "row", "previous_date",
                "previous_row", "pair_classification",
            ]
            row = {"path":"ohlcv/AAA.csv","blob_sha":"abc","symbol":"AAA","date":"2025-02-30","row":"3","previous_date":"2025-01-01","previous_row":"2","pair_classification":"INSUFFICIENT_SESSION_EVIDENCE"}
            self.make_csv(pairs, pair_fields, [row])
            self.make_csv(lineage, ["symbol","date","path","blob_sha","row"], [])
            with self.assertRaises(ValueError):
                audit(pairs, lineage)


if __ (not real)
