import csv,hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from scanner_inputs import historical_quarantine as q
from scanner_inputs import prepare_scanner_inputs as p

class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.holds={("ABC","2026-04-09"):"PRICE_SEMANTICS_HOLD"}
    def fixture(self, rows):
        path=self.root/"overlay.csv"
        fields=["symbol","date","overlay_disposition","promotion_allowed","replacement_approved","scanner_admission","canonical_action","original_lineage"]
        with path.open("w",newline="") as f:
            w=csv.writer(f);w.writerow(fields);w.writerows(rows)
        raw=path.read_bytes();digest=hashlib.sha256(raw).hexdigest()
        manifest=self.root/"manifest.json"
        counts={"PRICE_SEMANTICS_HOLD":len(rows)}
        manifest.write_text(json.dumps(dict(overlay_sha256=digest,overlay_bytes=len(raw),rows=len(rows),unique_keys=len(rows),dispositions=counts,approved_replacements=0,promoted=0,dates=1)))
        for name,value in dict(MANIFEST=manifest,OVERLAY_SHA256=digest,EXPECTED_ROWS=len(rows),EXPECTED_DISPOSITIONS=counts).items():
            ctx=patch.object(q,name,value);ctx.start();self.addCleanup(ctx.stop)
        return path
    def row(self):
        return ["ABC","2026-04-09","PRICE_SEMANTICS_HOLD","false","false","BLOCKED","NO_CHANGE",'["lineage"]']
    def test_valid_overlay(self):
        self.assertEqual(q.load_holds(self.fixture([self.row()])),self.holds)
    def test_corrupted_overlay(self):
        path=self.fixture([self.row()]);path.write_bytes(path.read_bytes()+b"x")
        with self.assertRaises(ValueError):q.load_holds(path)
    def test_duplicate_key(self):
        with self.assertRaises(ValueError):q.load_holds(self.fixture([self.row(),self.row()]))
    def test_unauthorized_promotion(self):
        row=self.row();row[3]="true"
        with self.assertRaises(ValueError):q.load_holds(self.fixture([row]))
    def test_missing_overlay(self):
        path=self.fixture([self.row()]);path.unlink()
        with self.assertRaises(FileNotFoundError):q.load_holds(path)
    def test_normalized_hold(self):
        with self.assertRaises(ValueError):q.reject_held(" abc ","2026-04-09",self.holds)
    def test_session_wide_hold(self):
        with self.assertRaises(ValueError):q.reject_held("OTHER","2026-04-10",self.holds)
    def test_clean_key(self):
        q.reject_held("ABC","2026-04-08",self.holds)
    def test_broker_held(self):
        path=self.root/"broker_summary.csv";path.write_text("symbol,date,broker\nABC,2026-04-09,14\n")
        with self.assertRaises(ValueError):p.validate_broker_table(path,set(),self.holds)
    def test_broker_unknown_schema(self):
        path=self.root/"broker_summary.csv";path.write_text("symbol,broker\nABC,14\n")
        with self.assertRaises(ValueError):p.validate_broker_table(path,set(),self.holds)
    def test_floorsheet_held(self):
        path=self.root/"floorsheet.csv";path.write_text("contractno,date,symbol,buyer,seller,quantity,rate,amount\n123,2026-04-09,ABC,14,17,10,100,1000\n")
        with self.assertRaises(ValueError):p.validate_floorsheet(path,set(),self.holds)
    def test_prepare_requires_overlay(self):
        with self.assertRaises(ValueError):p.prepare(self.root,self.root/"out")
    def test_prepare_rejects_held_daily_without_publication(self):
        original=self.root/"raw";original.mkdir()
        daily=original/"daily_prices.csv"
        raw="symbol,date,open,high,low,close,volume\nABC,2026-04-09,100,110,90,105,10\n"
        daily.write_text(raw)
        output=self.root/"out"
        with patch.object(p,"load_holds",return_value=self.holds),patch.object(p,"verified_closed_dates",return_value=set()):
            with self.assertRaises(ValueError):p.prepare(original,output,self.root/"overlay.csv")
        self.assertFalse(output.exists());self.assertEqual(daily.read_text(),raw)
if __name__=="__main__":unittest.main()
