import unittest
from validate_p444_identity_interval import validate

BASE={"record_type":"lifecycle_interval","security_id":"8041","symbol":"NESDO","instrument_type":"EQUITY","status":"ACTIVE","effective_from":"2026-01-01","effective_to":None,"source_url":"https://example.org/record.pdf","retrieved_at_utc":"2026-01-02T00:00:00Z","raw_sha256":"a"*64,"source_git_blob_sha":None,"authorization_status":"authorized","evidence_tier":"primary","effective_date_confidence":"verified","canonical_promotion_allowed":False}
class IdentityIntervalTests(unittest.TestCase):
 def test_verified_interval_contract_passes(self): self.assertEqual(validate(BASE),[])
 def test_snapshot_only_record_cannot_claim_effective_date(self):
  r={**BASE,"record_type":"snapshot_identity","effective_from":None,"source_url":"","retrieved_at_utc":None,"raw_sha256":None,"authorization_status":"not_assessed","evidence_tier":"current_snapshot_only","effective_date_confidence":"unknown"}
  self.assertEqual(validate(r),[])
 def test_lifecycle_without_hash_or_authorization_fails(self):
  r={**BASE,"raw_sha256":None,"authorization_status":"not_assessed"}
  self.assertIn("lifecycle_requires_raw_sha256",validate(r)); self.assertIn("lifecycle_requires_rights_clearance",validate(r))
 def test_reversed_interval_fails(self):
  r={**BASE,"effective_from":"2026-02-01","effective_to":"2026-01-01"}
  self.assertIn("reversed_interval",validate(r))
 def test_promotion_cannot_be_enabled(self):
  self.assertIn("promotion_must_remain_false",validate({**BASE,"canonical_promotion_allowed":True}))
if __name__=="__main__": unittest.main()
