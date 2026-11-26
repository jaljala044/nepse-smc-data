import csv, unittest
from pathlib import Path
from build_nepse_security_ohlcv_reconciliation import build
ROOT=Path(__file__).resolve().parents[2]
class OfficialSecurityOhlcvTests(unittest.TestCase):
    def test_committed_matrix_counts_and_unknowns(self):
        with (ROOT/"reference/p429_official_security_ohlcv_reconciliation_2026-11-26.csv").open(encoding="utf-8",newline="") as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),610)
        counts={}
        for r in rows: counts[r["disposition"]]=counts.get(r["disposition"],0)+1
        self.assertEqual(counts,{"OFFICIAL_MATCH_WITH_OHLCV":488,"OFFICIAL_NO_OHLCV_FILE":85,"OHLCV_FILE_NO_OFFICIAL_MATCH":37})
        self.assertTrue(all(r["instrument_type"]=="UNKNOWN" for r in rows))
        self.assertTrue(all(r["valid_from"]=="UNKNOWN" and r["valid_to"]=="UNKNOWN" for r in rows))
    def test_builder_reproduces_summary(self):
        rows,report=build(ROOT/"reference/nepse_official_security_list_2026-11-25.raw.json",ROOT/"03_stock_charts_ohlcv","1c025b5a89c22a74b827e3550cee76cf4d3f7898")
        self.assertEqual(len(rows),610)
        self.assertEqual(report["official_missing_ohlcv_by_status"],{"A":61,"S":24})
        self.assertEqual(report["official_matched_ohlcv_by_status"],{"A":485,"S":3})
if __name__=="__main__":unittest.main()
