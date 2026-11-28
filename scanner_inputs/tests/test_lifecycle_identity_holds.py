import csv, tempfile, unittest
from pathlib import Path
from lifecycle_identity_holds import load_lifecycle_holds, EXPECTED_SYMBOLS

FIELDS=["symbol","event_type","effective_date","calendar_basis","security_id","successor_symbol","source_url","retrieved_at_utc","raw_payload_path","raw_sha256","git_blob_sha","source_tier","effective_date_confidence","source_statement","disposition"]
def write_ledger(path, symbols, disposition_for=None):
    with path.open("w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=FIELDS); writer.writeheader()
        for symbol in symbols:
            writer.writerow({"symbol":symbol,"source_tier":"unknown","effective_date_confidence":"none","disposition":(disposition_for(symbol) if disposition_for else "HOLD_UNKNOWN")})

class LifecycleHoldTests(unittest.TestCase):
    def test_full_26_symbol_scope_is_held_wildcard(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"ledger.csv"; write_ledger(path,sorted(EXPECTED_SYMBOLS))
            holds=load_lifecycle_holds(path)
            self.assertEqual(len(holds),26)
            self.assertEqual(holds[("JALPA","*")],"P444_LIFECYCLE_IDENTITY_HOLD")
    def test_missing_symbol_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"ledger.csv"; write_ledger(path,["JALPA"])
            with self.assertRaises(ValueError): load_lifecycle_holds(path)
    def test_hold_release_requires_review_and_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"ledger.csv"; write_ledger(path,sorted(EXPECTED_SYMBOLS),lambda s:"VERIFIED" if s=="JALPA" else "HOLD_UNKNOWN")
            with self.assertRaises(ValueError): load_lifecycle_holds(path)
    def test_duplicate_symbol_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"ledger.csv"; write_ledger(path,list(sorted(EXPECTED_SYMBOLS))+["JALPA"])
            with self.assertRaises(ValueError): load_lifecycle_holds(path)
if __name__=="__main__": unittest.main()
