import csv,tempfile,unittest
from pathlib import Path
from tools.p444_audit_repeat_pair_matrix import audit

FIELDS=["pair_id","symbol","previous_date","current_date","source_path","source_blob_sha","previous_source_row","current_source_row","source_pair_tuple_equal","identity_scope","historical_stable_id","current_snapshot_security_id","previous_session_status","current_session_status","disposition","promotion_allowed"]

class MatrixArtifactAuditTests(unittest.TestCase):
 def row(self,**kw):
  r={k:"" for k in FIELDS};r.update({"pair_id":"file.csv#2->3","symbol":"ABC","previous_date":"2025-01-01","current_date":"2025-01-02","source_path":"file.csv","source_blob_sha":"a"*40,"previous_source_row":"2","current_source_row":"3","source_pair_tuple_equal":"true","identity_scope":"current_snapshot_only","current_snapshot_security_id":"10","previous_session_status":"UNKNOWN","current_session_status":"UNKNOWN","disposition":"HOLD_UNKNOWN_NO_INFERENCE","promotion_allowed":"false"});r.update(kw);return r
 def run_rows(self,rows):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);p=Path(t.name)/"m.csv"
  with p.open("w",newline="") as f:
   w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
  return audit(p,expected_pairs=len(rows),expected_symbols=len(set(x["symbol"] for x in rows)))
 def test_valid_hold_row_passes(self):
  self.assertTrue(self.run_rows([self.row()])["valid"])
 def test_promotion_is_rejected(self):
  x=self.run_rows([self.row(promotion_allowed="true")]);self.assertIn("PROMOTION_NOT_FALSE",[i["code"] for i in x["issues"]])
 def test_missing_historical_id_is_rejected(self):
  x=self.run_rows([self.row(identity_scope="historical_effective_dated_id")]);self.assertIn("HISTORICAL_ID_MISSING",[i["code"] for i in x["issues"]])
 def test_non_historical_scope_cannot_carry_historical_id(self):
  x=self.run_rows([self.row(historical_stable_id="10")]);self.assertIn("UNVERIFIED_HISTORICAL_ID_PRESENT",[i["code"] for i in x["issues"]])
 def test_duplicate_pair_id_is_rejected(self):
  x=self.run_rows([self.row(),self.row(symbol="DEF")]);self.assertIn("DUPLICATE_PAIR_ID",[i["code"] for i in x["issues"]])

if __name__=="__main__":unittest.main()
