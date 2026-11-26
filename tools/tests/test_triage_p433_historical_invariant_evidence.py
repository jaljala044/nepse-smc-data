import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from triage_p433_historical_invariant_evidence import build


def write_csv(path, rows, fields=None):
    fields = fields or (list(rows[0]) if rows else [])
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


class P433HistoricalEvidenceTriageTests(unittest.TestCase):
    def test_keeps_historical_flags_unknown_when_primary_sources_do_not_cover_dates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            flags = root / "flags.csv"
            write_csv(flags, [{"symbol":"AHPC","date":"2010-01-01","flag":"OPEN_OUTSIDE_RANGE"}])
            inventory = root / "floorsheets.csv"
            write_csv(inventory, [{
                "date":"2026-11-20","source_commit":"pinned123",
            }])
            actions = root / "actions.csv"
            write_csv(actions, [], ["symbol","event_type"])
            out, summary_path = root/"out.csv", root/"summary.json"
            summary = build(flags, inventory, actions, out, summary_path,
                            as_of_date="2026-11-26", official_history_days=365,
                            expected_flags=1)
            with out.open(newline="") as fh:
                row = next(csv.DictReader(fh))
            self.assertEqual(row["official_eod_status"], "OUTSIDE_CURRENT_ROLLING_HISTORY_WINDOW")
            self.assertEqual(row["floorsheet_archive_status"], "NO_PINNED_DAILY_FILE_FOR_DATE")
            self.assertEqual(row["corporate_action_status"], "NO_ACTION_RECORD_NOT_PROOF_OF_NONE")
            self.assertEqual(row["disposition"], "UNKNOWN_HISTORICAL_PRIMARY_SOURCE_NOT_AVAILABLE")
            self.assertEqual(summary["promoted_or_repaired_rows"], 0)

    def test_marks_action_record_as_review_required_and_archive_hit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            flags = root / "flags.csv"
            write_csv(flags, [{"symbol":"TEST","date":"2026-11-20","flag":"OPEN_OUTSIDE_RANGE"}])
            inventory = root / "floorsheets.csv"
            write_csv(inventory, [{"date":"2026-11-20","source_commit":"pinned123"}])
            actions = root / "actions.csv"
            write_csv(actions, [{"symbol":"TEST","event_type":"BONUS"}])
            summary = build(flags, inventory, actions, root/"out.csv", root/"summary.json",
                            as_of_date="2026-11-26", official_history_days=365,
                            expected_flags=1)
            with (root/"out.csv").open(newline="") as fh:
                row = next(csv.DictReader(fh))
            self.assertEqual(row["floorsheet_archive_status"], "PINNED_DAILY_FILE_PRESENT")
            self.assertEqual(row["corporate_action_status"], "ACTION_RECORD_PRESENT_REVIEW_REQUIRED")
            self.assertEqual(row["official_eod_status"], "WITHIN_WINDOW_BUT_ROW_NOT_YET_RETRIEVED")


if __name__ == "__main__":
    unittest.main()
