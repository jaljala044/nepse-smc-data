import unittest

from nepse_reference_validation import (
    instrument_active_on,
    validate_calendar_rows,
    validate_instrument_rows,
)

HASH = "a" * 64


class CalendarValidationTests(unittest.TestCase):
    def test_accepts_explicit_closed_record_with_provenance(self):
        rows = [{
            "date": "2026-12-25",
            "status": "verified_closed",
            "source_id": "NEPSE_HOLIDAY_API",
            "evidence_uri": "https://nepalstock.com.np/api/nots/holiday/list?year=2026",
            "raw_evidence_sha256": HASH,
        }]
        self.assertEqual(validate_calendar_rows(rows), [])

    def test_rejects_duplicate_dates(self):
        row = {
            "date": "2026-12-25", "status": "verified_closed",
            "source_id": "x", "evidence_uri": "https://example.invalid",
            "raw_evidence_sha256": HASH,
        }
        errors = validate_calendar_rows([row, row])
        self.assertTrue(any("duplicate calendar date" in e for e in errors))

    def test_rejects_invalid_date_and_status(self):
        errors = validate_calendar_rows([{"date": "2026-02-30", "status": "open"}])
        self.assertTrue(any("valid ISO date" in e for e in errors))
        self.assertTrue(any("invalid calendar status" in e for e in errors))

    def test_verified_open_requires_source_and_checksum(self):
        errors = validate_calendar_rows([{
            "date": "2026-01-05", "status": "verified_open",
            "source_id": "", "evidence_uri": "", "raw_evidence_sha256": "not-a-hash",
        }])
        self.assertTrue(any("requires source_id" in e for e in errors))
        self.assertTrue(any("requires evidence_uri" in e for e in errors))
        self.assertTrue(any("SHA-256" in e for e in errors))

    def test_candidate_weekday_is_not_promoted_to_verified(self):
        self.assertEqual(validate_calendar_rows([{
            "date": "2026-01-05", "status": "candidate_open"
        }]), [])


class InstrumentValidationTests(unittest.TestCase):
    def test_unknown_dataset_symbol_is_reported(self):
        rows = [{"security_id": "1001", "symbol": "API", "valid_from": "2020-01-01"}]
        errors = validate_instrument_rows(rows, ["API", "UNKNOWN"])
        self.assertIn("unknown instrument symbol in dataset: UNKNOWN", errors)

    def test_overlapping_symbol_with_different_ids_is_rejected(self):
        rows = [
            {"security_id": "1001", "symbol": "ABC", "valid_from": "2020-01-01", "valid_to": "2022-12-31"},
            {"security_id": "2002", "symbol": "ABC", "valid_from": "2022-12-31", "valid_to": ""},
        ]
        errors = validate_instrument_rows(rows)
        self.assertTrue(any("overlapping symbol mapping" in e for e in errors))

    def test_inclusive_effective_date_boundaries(self):
        row = {"security_id": "1001", "symbol": "ABC", "valid_from": "2020-01-01", "valid_to": "2020-12-31"}
        self.assertTrue(instrument_active_on(row, "2020-01-01"))
        self.assertTrue(instrument_active_on(row, "2020-12-31"))
        self.assertFalse(instrument_active_on(row, "2021-01-01"))

    def test_rejects_reversed_effective_dates(self):
        rows = [{"security_id": "1001", "symbol": "ABC", "valid_from": "2022-01-01", "valid_to": "2021-12-31"}]
        errors = validate_instrument_rows(rows)
        self.assertTrue(any("valid_to precedes valid_from" in e for e in errors))

    def test_overlapping_stable_id_across_symbols_is_rejected(self):
        rows = [
            {"security_id": "1001", "symbol": "OLD", "valid_from": "2020-01-01", "valid_to": "2021-06-30"},
            {"security_id": "1001", "symbol": "NEW", "valid_from": "2021-06-30", "valid_to": ""},
        ]
        errors = validate_instrument_rows(rows)
        self.assertTrue(any("overlapping stable security_id" in e for e in errors))

    def test_non_overlapping_symbol_rename_can_reuse_stable_id(self):
        rows = [
            {"security_id": "1001", "symbol": "OLD", "valid_from": "2020-01-01", "valid_to": "2021-06-30"},
            {"security_id": "1001", "symbol": "NEW", "valid_from": "2021-07-01", "valid_to": ""},
        ]
        self.assertEqual(validate_instrument_rows(rows), [])

    def test_duplicate_overlapping_register_row_is_rejected(self):
        row = {"security_id": "1001", "symbol": "ABC", "valid_from": "2020-01-01", "valid_to": ""}
        errors = validate_instrument_rows([row, dict(row)])
        self.assertTrue(any("overlapping stable security_id" in e for e in errors))

    def test_missing_valid_from_is_rejected(self):
        rows = [{"security_id": "1001", "symbol": "ABC", "valid_from": "", "valid_to": ""}]
        self.assertTrue(any("missing valid_from" in e for e in validate_instrument_rows(rows)))


if __name__ == "__main__":
    unittest.main()
