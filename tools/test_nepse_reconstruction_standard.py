"""Replay actual pinned April floorsheets through reusable standard."""
import csv,json,unittest,tempfile
from decimal import Decimal
from pathlib import Path
from nepse_reconstruction_standard import reconstruct
from validate_historical_floorsheets import download_one

class StandardTests(unittest.TestCase):
    def test_proxy(self):
        rows=[dict(contract="2",quantity=10,rate=101),dict(contract="1",quantity=10,rate=100),dict(contract="3",quantity=1,rate=90)]
        x=reconstruct(rows,lot_size=10)
        self.assertEqual((x["open"],x["high"],x["low"],x["close"],x["volume"]),(100,101,100,101,21))
        self.assertFalse(x["promotion_allowed"])
    def test_duplicate(self):
        r=dict(contract="1",quantity=10,rate=100)
        with self.assertRaises(ValueError):reconstruct([r,r],lot_size=10)
    def test_zero_price(self):
        with self.assertRaises(ValueError):reconstruct([dict(contract="1",quantity=10,rate=0)],lot_size=10)
    def test_no_regular(self):
        self.assertEqual(reconstruct([dict(contract="1",quantity=1,rate=100)],lot_size=10)["status"],"NO_ELIGIBLE_PRICE_TRADES")
    def test_timestamp(self):
        rows=[dict(contract="1",quantity=10,rate=101,time="2026-04-24T11:01:00+05:45"),dict(contract="2",quantity=10,rate=100,time="2026-04-24T11:00:00+05:45")]
        self.assertEqual(reconstruct(rows,lot_size=10,order_mode="timestamp")["open"],100)
        rows[0]["time"]=rows[1]["time"]
        with self.assertRaises(ValueError):reconstruct(rows,lot_size=10,order_mode="timestamp")
    def test_april_replay(self):
        evidence=json.loads(Path("reference/APRIL_2026_ODD_LOT_ADJUDICATION_2026-11-27.json").read_text())
        expected=evidence["rows"]
        dates={x["date"] for x in expected}
        self.assertEqual(len(expected),11)
        self.assertEqual(len({(x["date"],x["symbol"]) for x in expected}),11)
        with open("reference/p419_observed_date_floorsheet_archive_inventory_2026-11-26.csv",newline="") as f:
            items=[r for r in csv.DictReader(f) if r["date"] in dates and r["inventory_status"]=="FILE_PRESENT_IN_PINNED_GIT_TREE"]
        self.assertEqual(len(items),4)
        with tempfile.TemporaryDirectory() as tmp:
            for item in items:
                d=download_one(item,Path(tmp))
                self.assertEqual(d["download_status"],"PASS")
                with open(d["path"],newline="",encoding="utf-8-sig") as f: rows=list(csv.DictReader(f))
                for target in [x for x in expected if x["date"]==item["date"]]:
                    with self.subTest(date=target["date"],symbol=target["symbol"]):
                        self.assertEqual(d["actual_sha256"],target["source_sha256"])
                        trades=[dict(contract=r["transaction"],quantity=r["quantity"],rate=r["rate"]) for r in rows if r["symbol"].strip().upper()==target["symbol"]]
                        result=reconstruct(trades,lot_size=10)
                        self.assertEqual([result[k] for k in ("open","high","low","close","volume")],[Decimal(str(v)) for v in target["regular_price_all_volume_candidate"]])
                        self.assertFalse(result["promotion_allowed"])
                        print("REPLAY_PASS",target["date"],target["symbol"])
if __name__=="__main__":unittest.main(verbosity=2)
