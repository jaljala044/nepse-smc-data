import csv
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from audit_derived_ohlcv_v2 import audit


def git_blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def write_csv(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


class DerivedOhlcvV2AuditTests(unittest.TestCase):
    def fixture(self, root, corrupt_official=False):
        v2 = root / "v2"
        raw = root / "raw"
        out = root / "audit"
        v2.mkdir()
        raw.mkdir()
        raw_bytes = b"Date,Open,High,Low,Close,Volume\n2026-03-02,100,105,98,103,1000\n"
        derived_close = "102" if corrupt_official else "103"
        derived_bytes = (
            "Date,Open,High,Low,Close,Volume\n"
            f"2026-03-01,100,105,98,{derived_close},1000\n"
            "2026-03-02,100,105,98,103,1000\n"
        ).encode()
        (raw / "TEST_OHLCV.csv").write_bytes(raw_bytes)
        (v2 / "TEST_OHLCV.csv").write_bytes(derived_bytes)
        write_csv(v2 / "manifest.csv",
            ["symbol","raw_source_blob_sha","derived_blob_sha","rows"],
            [{"symbol":"TEST","raw_source_blob_sha":git_blob_sha(raw_bytes),"derived_blob_sha":git_blob_sha(derived_bytes),"rows":2}])
        write_csv(v2 / "provenance_ledger.csv",
            ["symbol","official_business_date","official_open","official_high","official_low","official_close","official_volume"],
            [{"symbol":"TEST","official_business_date":"2026-03-01","official_open":"100","official_high":"105","official_low":"98","official_close":"103","official_volume":"1000"}])
        write_csv(v2 / "corrections.csv",
            ["symbol","date","field","raw_value","derived_value","source","source_url","reason","status"],
            [{"symbol":"TEST","date":"2026-03-01","field":"Date","raw_value":"2026-03-02","derived_value":"2026-03-01","source":"NEPSE","source_url":"url","reason":"official","status":"applied"}])
        calendar = root / "calendar.csv"
        write_csv(calendar, ["date","status"], [
            {"date":"2026-03-01","status":"verified_open_observed"},
            {"date":"2026-03-02","status":"verified_closed"},
        ])
        actions = root / "corporate_actions.csv"
        write_csv(actions, ["symbol","event_type","announced_date","event_date","quantity_ratio","price_factor","notes"], [
            {"symbol":"TEST","event_type":"BONUS","announced_date":"2026-02-01","event_date":"2026-03-01","quantity_ratio":"0.1","price_factor":"0.909","notes":"fixture"}
        ])
        split = root / "split_review.csv"
        write_csv(split, ["symbol","proposal_date","old_par_npr","proposed_par_npr","proposed_new_shares_per_old_share","verified_effective_date","assessment","proposal_source","annual_report_source"], [
            {"symbol":"TEST","proposal_date":"2021-01-19","old_par_npr":"100","proposed_par_npr":"50","proposed_new_shares_per_old_share":"2","verified_effective_date":"","assessment":"proposal only; no effective date verified","proposal_source":"source","annual_report_source":"annual"}
        ])
        return v2, raw, calendar, actions, split, out, raw_bytes

    def test_audit_reports_repeats_and_closed_date_without_mutating_raw(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            v2, raw, calendar, actions, split, out, raw_before = self.fixture(root)
            totals = audit(v2, raw, calendar, actions, out,
                           expected_symbols=1, expected_official_rows=1,
                           expected_correction_counts={"Date": 1}, split_review_path=split)
            self.assertEqual(totals["raw_files_verified_byte_identical_to_manifest"], 1)
            self.assertEqual(totals["official_provenance_rows_verified"], 1)
            self.assertEqual(totals["adjacent_identical_ohlcv_rows"], 1)
            self.assertEqual(totals["calendar_alignment_flags"], 1)
            self.assertEqual(totals["corporate_action_event_records"], 1)
            self.assertEqual(totals["split_proposals_without_verified_effective_date"], 1)
            with (out / "split_review_flags.csv").open(newline="", encoding="utf-8") as fh:
                split_flags = list(csv.DictReader(fh))
            self.assertEqual(split_flags[0]["disposition"], "NO_SPLIT_FACTOR_APPLIED_EFFECTIVE_DATE_UNKNOWN")
            self.assertEqual((raw / "TEST_OHLCV.csv").read_bytes(), raw_before)
            with (out / "adjacent_repeat_flags.csv").open(newline="", encoding="utf-8") as fh:
                repeat_rows = list(csv.DictReader(fh))
            self.assertEqual(repeat_rows[0]["classification"], "CLOSED_SESSION_REPEAT_CANDIDATE")

    def test_audit_rejects_official_provenance_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            v2, raw, calendar, actions, split, out, _ = self.fixture(root, corrupt_official=True)
            with self.assertRaises(ValueError):
                audit(v2, raw, calendar, actions, out,
                      expected_symbols=1, expected_official_rows=1,
                      expected_correction_counts={"Date": 1}, split_review_path=split)


if __name__ == "__main__":
    unittest.main()
