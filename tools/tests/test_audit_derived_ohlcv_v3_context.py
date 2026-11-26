import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from audit_derived_ohlcv_v3_context import build_context


def write_csv(path, rows, fields=None):
    fields = fields or (list(rows[0]) if rows else [])
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


class DerivedOhlcvV3ContextTests(unittest.TestCase):
    def test_recomputes_repeats_calendar_and_action_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            v3 = root / "v3"
            v3.mkdir()
            (v3 / "TEST_OHLCV.csv").write_text(
                "Date,Open,High,Low,Close,Volume\n"
                "2026-01-01,100,105,98,103,1000\n"
                "2026-01-02,100,105,98,103,1000\n",
                encoding="utf-8",
            )
            write_csv(v3 / "manifest.csv", [{
                "symbol":"TEST","rows":"2",
            }])
            calendar = root / "calendar.csv"
            write_csv(calendar, [
                {"date":"2026-01-01","status":"verified_open_observed"},
                {"date":"2026-01-02","status":"verified_closed"},
            ])
            actions = root / "actions.csv"
            write_csv(actions, [{
                "symbol":"TEST","event_type":"BONUS","announced_date":"2025-12-01",
                "event_date":"2026-01-02","quantity_ratio":"0.1","price_factor":"0.909",
                "notes":"test event",
            }])
            split = root / "split.csv"
            write_csv(split, [{
                "symbol":"TEST","proposal_date":"2025-01-01","old_par_npr":"100",
                "proposed_par_npr":"50","verified_effective_date":"",
                "assessment":"proposal only",
            }])
            out = root / "out"
            totals = build_context(v3, calendar, actions, split, out, expected_symbols=1)
            self.assertEqual(totals["adjacent_identical_ohlcv_rows"], 1)
            self.assertEqual(totals["adjacent_repeat_classifications"]["CLOSED_SESSION_REPEAT_CANDIDATE"], 1)
            self.assertEqual(totals["calendar_alignment_flags"], 1)
            self.assertEqual(totals["corporate_action_event_records"], 1)
            self.assertEqual(totals["split_proposals_without_verified_effective_date"], 1)
            with (out / "calendar_alignment_flags.csv").open(newline="") as fh:
                flags = list(csv.DictReader(fh))
            self.assertEqual(flags[0]["flag"], "ROW_ON_VERIFIED_CLOSED_DATE")
            with (out / "corporate_action_coverage.csv").open(newline="") as fh:
                coverage = list(csv.DictReader(fh))
            self.assertEqual(coverage[0]["adjustment_status"], "RAW_PRICE_BASIS_REVIEW_REQUIRED")

    def test_absent_action_records_are_not_called_no_action(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            v3 = root / "v3"
            v3.mkdir()
            (v3 / "TEST_OHLCV.csv").write_text(
                "Date,Open,High,Low,Close,Volume\n2026-01-01,100,105,98,103,1000\n",
                encoding="utf-8",
            )
            write_csv(v3 / "manifest.csv", [{"symbol":"TEST","rows":"1"}])
            calendar, actions, split = root/"calendar.csv", root/"actions.csv", root/"split.csv"
            write_csv(calendar, [{"date":"2026-01-01","status":"verified_open_observed"}])
            write_csv(actions, [], ["symbol","event_type","announced_date","event_date","quantity_ratio","price_factor","notes"])
            write_csv(split, [], ["symbol","proposal_date","old_par_npr","proposed_par_npr","verified_effective_date","assessment"])
            out = root / "out"
            totals = build_context(v3, calendar, actions, split, out, expected_symbols=1)
            self.assertEqual(totals["symbols_without_action_records_not_verified"], 1)
            with (out / "corporate_action_coverage.csv").open(newline="") as fh:
                rows = list(csv.DictReader(fh))
            self.assertEqual(rows[0]["adjustment_status"], "NO_ACTION_RECORD_NOT_VERIFIED")


if __name__ == "__main__":
    unittest.main()
