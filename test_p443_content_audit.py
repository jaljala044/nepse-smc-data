import unittest
from p443_content_audit import scan, records

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
    def test_bad_row_width(self):
        with self.assertRaises(ValueError):
            list(records(b"a,b\n1,2,3\n","csv"))
    def test_json_scopes(self):
        entry=dict(path="calendar.json",git_blob_sha="fixture",format="json",category="session_calendar")
        _,_,findings=scan(b'{"a":[{"date":"2025-01-01"}],"b":[{"date":"2025-01-01"}]}',entry)
        self.assertEqual(findings,[])
