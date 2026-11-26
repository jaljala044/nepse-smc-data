import csv, tempfile, unittest
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
SCRIPT=Path(__file__).resolve().parents[1]/"audit_ohlcv_row_quality.py"
SPEC=spec_from_file_location("audit_ohlcv_row_quality",SCRIPT); M=module_from_spec(SPEC); SPEC.loader.exec_module(M)

class RowQualityTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
 def tearDown(self): self.tmp.cleanup()
 def write(self, rows):
  p=self.root/"ABC_OHLCV.csv"
  with p.open("w",newline="") as f:
   w=csv.DictWriter(f,fieldnames=["Date","Open","High","Low","Close","Volume"]); w.writeheader(); w.writerows(rows)
  return p
 def row(self,d="2026-11-19",o="10",h="11",l="9",c="10",v="100"):
  return dict(Date=d,Open=o,High=h,Low=l,Close=c,Volume=v)
 def test_valid_row_no_flags_and_hash(self):
  self.write([self.row()]); r=M.audit_file("ABC",self.root)
  self.assertEqual(r["classification"],"NO_BASIC_FLAGS_IN_THIS_CHECK"); self.assertEqual(len(r["sha256"]),64)
 def test_duplicate_and_invalid_ohlc_flagged(self):
  self.write([self.row(),self.row(h="8")]); r=M.audit_file("ABC",self.root)
  self.assertEqual(r["duplicate_dates"],1); self.assertEqual(r["ohlc_invariant_rows"],1)
  self.assertEqual(r["classification"],"REVIEW_FLAGS_PRESENT")
 def test_missing_file_is_not_no_trade(self):
  r=M.audit_file("XYZ",self.root); self.assertEqual(r["file_status"],"MISSING_FILE")
  self.assertNotIn("NO_TRADE",r["classification"])
 def test_zero_volume_is_reported_not_discarded(self):
  self.write([self.row(v="0")]); r=M.audit_file("ABC",self.root); self.assertEqual(r["zero_volume_rows"],1)
if __name__=="__main__": unittest.main()
