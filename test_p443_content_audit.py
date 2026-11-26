import unittest
from p443_content_audit import scan, records, non_json_capture, floorsheet_date_from_filename

class StrictAuditTests(unittest.TestCase):
    def test_ohlcv(self):
        entry=dict(path="ABC_OHLCV.csv",git_blob_sha="fixture",format="csv",category="ohlcv_symbol_archive")
        raw=b"Date,Open,High,Low,Close,Volume\n2025-01-01,10,11,9,10,5\n2025-01-02,10,11,9,10,5\n2025-01-02,10,11,9,10,5\n2025-01-03,10,8,9,10,5\n"
        n,schemas,findings=scan(raw,entry)
        self.assertEqual(n,4)
        self.assertEqual(schemas,{"ohlcv":4})
        self.assertEqual({f["classification"] for f in findings},{"exact_record_repeat","duplicate_business_key","repeated_adjacent_tuple_unresolved","invalid_ohlcv"})
    def test_contract_session_scope(self):
        entry=dict(path="trades.csv",git_blob_sha="fixture",format="csv",category="floorsheet_or_reconciliation")
        raw=b"Date,ContractNo,Quantity\n2025-01-01,1,5\n2025-01-02,1,5\n2025-01-02,1,6\n"
        _,_,findings=scan(raw,entry)
        self.assertEqual([f["classification"] for f in findings],["conflicting_business_key"])
    def test_empty_json_capture(self):
        self.assertEqual(list(records(b"  ", "json")), [])
    def test_duplicate_display_headers_are_disambiguated(self):
        rows = list(records(b"Date,Diff,Diff %\n2024-01-01,1,2\n", "csv"))
        self.assertEqual(rows[0][1]["diff"], "1")
        self.assertEqual(rows[0][1]["diff__duplicate_2"], "2")
    def test_floorsheet_session_date_from_filename(self):
        self.assertEqual(floorsheet_date_from_filename("reference/floorsheet/floorsheet_2024-08-18.csv.gz"), "2024-08-18")
        self.assertEqual(floorsheet_date_from_filename("reference/audit_2024-08-18.json"), "")
    def test_floorsheet_contract_uses_filename_session_date(self):
        entry=dict(path="floorsheet/floorsheet_2024-08-18.csv",git_blob_sha="fixture",format="csv",category="floorsheet_or_reconciliation")
        raw=b"ContractNo,Quantity\\n123,5\\n123,6\\n"
        _,_,findings=scan(raw,entry)
        self.assertEqual([f["classification"] for f in findings],["conflicting_business_key"])
    def test_provider_error_body_is_not_parsed_as_json(self):
        self.assertTrue(non_json_capture(b"<html><body>WARNING: UNAUTHORIZED ACCESS</body></html>"))
        self.assertTrue(non_json_capture(b"Searched Date is not valid."))
        self.assertFalse(non_json_capture(b'{"ok": true}'))
    def test_bad_row_width(self):
        with self.assertRaises(ValueError):
            list(records(b"a,b\n1,2,3\n","csv"))
    def test_json_scopes(self):
        entry=dict(path="calendar.json",git_blob_sha="fixture",format="json",category="session_calendar")
        _,_,findings=scan(b'{"a":[{"date":"2025-01-01"}],"b":[{"date":"2025-01-01"}]}',entry)
        self.assertEqual(findings,[])
