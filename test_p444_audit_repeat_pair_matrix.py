import csv
import tempfile
import unittest
from pathlib import Path

from tools.p444_audit_repeat_pair_matrix import audit

FIELDS = [
    "pair_id", "symbol", "previous_date", "current_date", "source_path",
    "source_blob_sha", "previous_source_row", "current_source_row",
    "source_pair_tuple_equal", "identity_scope", "historical_stable_id",
    "current_snapshot_security_id", "previous_session_status",
    "current_session_status", "disposition", "promotion_allowed",
]
for side in ("previous", "current"):
    FIELDS.extend(f"{side}_{field}" for field in (
        "execution_sources", "execution_security_ids", "execution_trade_counts",
        "execution_quantities", "execution_values", "execution_retrieved_at",
    ))


class MatrixArtifactAuditTests(unittest.TestCase):
    def row(self, **overrides):
        row = {field: "" for field in FIELDS}
        row.update({
            "pair_id": "file.csv#2->3", "symbol": "ABC",
            "previous_date": "2025-01-01", "current_date": "2025-01-02",
            "source_path": "file.csv", "source_blob_sha": "a" * 40,
            "previous_source_row": "2", "current_source_row": "3",
            "source_pair_tuple_equal": "true", "identity_scope": "current_snapshot_only",
            "current_snapshot_security_id": "10",
            "previous_session_status": "UNKNOWN", "current_session_status": "UNKNOWN",
            "disposition": "HOLD_UNKNOWN_NO_INFERENCE", "promotion_allowed": "false",
        })
        row.update(overrides)
        return row

    def run_rows(self, rows):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name) / "matrix.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        return audit(path, expected_pairs=len(rows),
                     expected_symbols=len({row["symbol"] for row in rows}))

    def codes(self, result):
        return [issue["code"] for issue in result["issues"]]

    def test_valid_hold_row_passes(self):
        self.assertTrue(self.run_rows([self.row()])["valid"])

    def test_promotion_is_rejected(self):
        self.assertIn("PROMOTION_NOT_FALSE",
                      self.codes(self.run_rows([self.row(promotion_allowed="true")])))

    def test_missing_historical_id_is_rejected(self):
        self.assertIn("HISTORICAL_ID_MISSING",
                      self.codes(self.run_rows([self.row(identity_scope="historical_effective_dated_id")])))

    def test_non_historical_scope_cannot_carry_historical_id(self):
        self.assertIn("UNVERIFIED_HISTORICAL_ID_PRESENT",
                      self.codes(self.run_rows([self.row(historical_stable_id="10")])))

    def test_duplicate_pair_id_is_rejected(self):
        result = self.run_rows([self.row(), self.row(symbol="DEF")])
        self.assertIn("DUPLICATE_PAIR_ID", self.codes(result))

    def test_non_increasing_dates_are_rejected(self):
        result = self.run_rows([self.row(previous_date="2025-01-02", current_date="2025-01-02")])
        self.assertIn("NON_INCREASING_PAIR_DATES", self.codes(result))

    def test_invalid_source_row_identity_is_rejected(self):
        result = self.run_rows([self.row(previous_source_row="0")])
        self.assertIn("INVALID_SOURCE_ROW_NUMBER", self.codes(result))

    def test_partial_execution_bundle_is_rejected(self):
        result = self.run_rows([self.row(current_execution_sources="capture.json")])
        self.assertIn("PARTIAL_EXECUTION_EVIDENCE_BUNDLE", self.codes(result))

    def test_complete_execution_bundle_is_counted(self):
        row = self.row()
        for field, value in {
            "current_execution_sources": "capture.json",
            "current_execution_security_ids": "123",
            "current_execution_trade_counts": "4",
            "current_execution_quantities": "100",
            "current_execution_values": "2500",
            "current_execution_retrieved_at": "2026-11-27T00:00:00Z",
        }.items():
            row[field] = value
        result = self.run_rows([row])
        self.assertTrue(result["valid"], result["issues"])
        self.assertEqual(result["counts"]["current_execution_evidence_present"], 1)

    def test_unresolved_identity_cannot_carry_current_id(self):
        result = self.run_rows([self.row(identity_scope="unresolved", current_snapshot_security_id="10")])
        self.assertIn("UNRESOLVED_SCOPE_HAS_CURRENT_ID", self.codes(result))


if __name__ == "__main__":
    unittest.main()
