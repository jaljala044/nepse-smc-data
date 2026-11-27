import csv,tempfile,unittest
from pathlib import Path
from tools.p444_validate_lifecycle_evidence import validate

FIELDS=["symbol","event_type","effective_date","calendar_basis","security_id","successor_symbol","source_url","retrieved_at_utc","raw_payload_path","raw_sha256","git_blob_sha","source_tier","effective_date_confidence","source_statement","disposition"]

class LifecycleValidatorTests(unittest.TestCase):
 def write(self,rows):
  t=tempfile.TemporaryDirectory(); self.addCleanup(t.cleanup); p=Path(t.name)/"ledger.csv"
  with p.open("w",newline="") as f:
   w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
  return p
 def test_blank_hold_rows_are_valid_but_not_provenance_complete(self):
  p=self.write([{"symbol":"ABC","source_tier":"unknown","effective_date_confidence":"none","disposition":"HOLD_UNKNOWN"}])
  x=validate(p);self.assertTrue(x["valid"]);self.assertEqual(x["provenance_complete_rows"],0)
 def test_incomplete_primary_claim_is_flagged(self):
  p=self.write([{"symbol":"ABC","event_type":"delisting","effective_date":"2026-01-01","source_url":"https://example.org","source_tier":"exchange_primary","effective_date_confidence":"verified","disposition":"HOLD_UNKNOWN"}])
  self.assertIn("INCOMPLETE_PROVENANCE",[x["code"] for x in validate(p)["issues"]])
 def test_invalid_date_and_event_are_flagged(self):
  p=self.write([{"symbol":"ABC","event_type":"trade_end","effective_date":"not-a-date","disposition":"HOLD_UNKNOWN"}])
  codes=[x["code"] for x in validate(p)["issues"]]
  self.assertIn("INVALID_EVENT_TYPE",codes);self.assertIn("INVALID_EFFECTIVE_DATE",codes)
 def test_duplicate_identity_scope_is_flagged(self):
  row={"symbol":"ABC","event_type":"listing","effective_date":"2020-01-01","source_url":"https://exchange.example/doc","retrieved_at_utc":"2026-11-27T00:00:00Z","raw_payload_path":"x.pdf","raw_sha256":"a"*64,"git_blob_sha":"b"*40,"source_tier":"exchange_primary","effective_date_confidence":"verified","disposition":"HOLD_UNKNOWN"}
  p=self.write([row,row]);self.assertIn("DUPLICATE_EVENT_RECORD",[x["code"] for x in validate(p)["issues"]])

if __name__=="__main__":unittest.main()
