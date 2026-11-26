"""Contract tests against a separately checked-out pinned scanner backend."""
import csv
import io
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path
from scanner_inputs.prepare_scanner_inputs import aggregate_daily, validate_daily

sys.path.insert(0, str(Path("scanner-backend/backend").resolve()))
from app.scanner import quality_errors
from app.structure_timeframes import evaluate_timeframes
from app.scanner_eligibility import assess
from app.idpat_v3 import evaluate_idpat_v3

class CrossRepositoryTests(unittest.TestCase):
    def bars(self):
        return [dict(symbol="TEST", date=(date(2026,1,4)+timedelta(days=i)).isoformat(),
                     open="100", high="105", low="99", close="102", volume="10")
                for i in range(35) if i % 7 < 5]

    def typed(self, bars):
        return [dict(date=date.fromisoformat(r["date"]), **{k:float(r[k]) for k in ("open","high","low","close")}, volume=int(r["volume"])) for r in bars]

    def test_structural_contract(self):
        bars=self.bars()
        validate_daily(bars,set())
        for group in (bars,aggregate_daily(bars,"weekly",set()),aggregate_daily(bars,"monthly",set())):
            self.assertEqual(quality_errors(self.typed(group)),[])

    def test_unreviewed_rows_blocked(self):
        bars=self.typed(self.bars())
        self.assertTrue(assess("TEST",bars,"2026-02-10T15:00:00+05:45",{}))
        self.assertEqual(evaluate_timeframes(bars,eligible=False)["status"],"unavailable")
        self.assertIsNone(evaluate_idpat_v3(bars,eligible=False)["score"])

    def test_completed_week_contract(self):
        bars=self.typed(self.bars())
        result=evaluate_timeframes(bars,eligible=True,verified_sessions={r["date"] for r in bars})
        self.assertEqual(result["weekly_completed_bars"],4)
        self.assertIsNone(result["score"])
        self.assertEqual(result["swing"]["action"],"NO TRADE")

    def test_idpat_specification_gate(self):
        result=evaluate_idpat_v3(self.typed(self.bars()),eligible=True)
        self.assertEqual(result["status"],"specification_unverified")
        self.assertIsNone(result["score"])

if __name__ == "__main__":
    unittest.main()
