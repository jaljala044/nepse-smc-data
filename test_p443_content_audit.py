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
        raw=b"Date,ID,ContractNo,Symbol,Buyer,Seller,Quantity\n2025-01-01,10,1,ABC,1,2,5\n2025-01-02,11,1,ABC,1,2,5\n2025-01-02,11,1,ABC,1,2,6\n"
        _,_,findings=scan(raw,entry)
        self.assertEqual([f["classification"] for f in findings],["conflicting_business_key"])
        self.assertIn("previous=", findings[0]["evidence"])
        self.assertIn("current=", findings[0]["evidence"])
    def test_contract_number_reuse_is_not_duplicate_record_identity(self):
        entry=dict(path="trades.csv",git_blob_sha="fixture",format="csv",category="floorsheet_or_reconciliation")
        raw=b"Date,ID,ContractNo,Symbol,Buyer,Seller,Quantity\n2025-01-01,10,999,ABC,1,2,5\n2025-01-01,11,999,XYZ,1,2,6\n"
        _,schemas,findings=scan(raw,entry)
        self.assertEqual(findings,[])
        self.assertEqual(schemas["contract_no_reused_values"],1)
        self.assertEqual(schemas["contract_no_reused_rows"],1)
        self.assertEqual(schemas["contract_no_reused_across_symbols"],1)
    def test_ohlcv_flat_candle_at_valid_bounds(self):
        entry=dict(path="ABC_OHLCV.csv",git_blob_sha="fixture",format="csv",category="ohlcv_symbol_archive")
        raw=b"Date,Open,High,Low,Close,Volume\n2025-01-01,790,790,790,790,10\n"
        _,_,findings=scan(raw,entry)
        self.assertEqual(findings,[])
    def test_non_transaction_floorsheet_metadata_is_not_missing_trade_session(self):
        entry=dict(path="audit.json",git_blob_sha="fixture",format="json",category="floorsheet_or_reconciliation")
        raw=b'{"date":"2026-11-23","page_sha256":"abc","contracts":42,"turnover_npr":1000}'
        _,schemas,findings=scan(raw,entry)
        self.assertEqual(findings,[])
        self.assertEqual(schemas["non_transaction_record"],1)
    def test_trade_record_without_session_is_flagged(self):
        entry=dict(path="trades.csv",git_blob_sha="fixture",format="csv",category="floorsheet_or_reconciliation")
        raw=b"ContractNo,Symbol,Buyer,Seller,Quantity,Rate\n123,ABC,1,2,5,10\n"
        _,_,findings=scan(raw,entry)
        self.assertEqual([f["classification"] for f in findings],["contract_session_missing"])
    def test_metadata_contract_sample_is_not_trade(self):
        entry=dict(path="capture_report.json",git_blob_sha="fixture",format="json",category="floorsheet_or_reconciliation")
        _,schemas,findings=scan(b'{"sample":{"contract_no":"123","id":"456","quantity":"5","rate":"10"}}',entry)
        self.assertEqual(findings,[])
        self.assertEqual(schemas["non_transaction_record"],1)
    def test_official_contract_aliases_and_calculation_date(self):
        entry=dict(path="trades.csv",git_blob_sha="fixture",format="csv",category="floorsheet_or_reconciliation")
        raw=b"calculation_date,contractId,stockSymbol,buyerMemberId,sellerMemberId,contractQuantity,contractRate\n2025-01-01,123,ABC,1,2,5,10\n"
        _,schemas,findings=scan(raw,entry)
        self.assertEqual(findings,[])
        self.assertEqual(schemas["contract"],1)
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
        raw=b"ID,ContractNo,Symbol,Buyer,Seller,Quantity\n10,123,ABC,1,2,5\n11,123,ABC,1,2,6\n11,123,ABC,1,2,7\n"
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
