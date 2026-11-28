import tempfile, unittest
from pathlib import Path
from lifecycle_identity_holds import load_lifecycle_holds, EXPECTED_SYMBOLS

HEADER="symbol,event_type,effective_date,calendar_basis,security_id,successor_symbol,source_url,retrieved_at_utc,raw_payload_path,raw_sha256,git_blob_sha,source_tier,effective_date_confidence,source_statement,disposition\n"
def row(symbol, disposition="HOLD_UNKNOWN"):
    return f"{symbol},,,,,,,,,,,,unknown,none,,{disposition}\n"

class LifecycleHoldTests(unittest.TestCase):
    def test_full_26_symbol_scope_is_held_wildcard(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"ledger.csv"
            path.write_text(HEADER+"".join(row(s) for s in sorted(EXPECTED_SYMBOLS)))
            holds=load_lifecycle_holds(path)
            self.assertEqual(len(holds),26)
            self.assertEqual(holds[("JALPA","*")],"P444_LIFECYCLE_IDENTITY_HOLD")
    def test_missing_symbol_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"ledger.csv"
            path.write_text(HEADER+row("JALPA"))
            with self.assertRaises(ValueError): load_lifecycle_holds(path)
    def test_hold_release_requires_review_and_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"ledger.csv"
            path.write_text(HEADER+"".join(row(s,"VERIFIED") if s=="JALPA" else row(s) for s in sorted(EXPECTED_SYMBOLS)))
            with self.assertRaises(ValueError): load_lifecycle_holds(path)
    def test_duplicate_symbol_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"ledger.csv"
            path.write_text(HEADER+"".join(row(s) for s in sorted(EXPECTED_SYMBOLS))+row("JALPA"))
            with self.assertRaises(ValueError): load_lifecycle_holds(path)
if __name__=="__main__": unittest.main()
