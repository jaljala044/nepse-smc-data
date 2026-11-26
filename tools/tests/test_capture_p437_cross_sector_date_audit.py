import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from capture_p437_cross_sector_date_audit import (
    SAMPLE, validate_sample, weekday_class, summarize_rows, build_quarantine_rows, capture
)

class P437CrossSectorDateAuditTests(unittest.TestCase):
    def test_sample_is_two_active_equities_per_twelve_sectors(self):
        result=validate_sample("../scanner_inputs/sectors.csv")
        self.assertEqual(result["errors"],[])
        self.assertEqual(len(SAMPLE),24)
        self.assertEqual(len(result["sector_counts"]),12)
        self.assertTrue(all(n==2 for n in result["sector_counts"].values()))

    def test_nepse_weekend_classification_respects_2026_regime_change(self):
        self.assertEqual(weekday_class("2026-04-03"),"friday")
        self.assertEqual(weekday_class("2026-04-04"),"saturday")
        self.assertEqual(weekday_class("2026-04-05"),"trading_weekday")
        self.assertEqual(weekday_class("2026-04-06"),"trading_weekday")
        self.assertEqual(weekday_class("2026-04-10"),"trading_weekday")
        self.assertEqual(weekday_class("2026-04-11"),"saturday")
        self.assertEqual(weekday_class("2026-04-12"),"sunday")
        self.assertEqual(weekday_class("2026-11-26"),"trading_weekday")
        self.assertEqual(weekday_class("2026-11-27"),"trading_weekday")
        self.assertEqual(weekday_class("2026-11-28"),"saturday")
        self.assertEqual(weekday_class("2026-11-29"),"sunday")

    def test_row_summary_flags_duplicate_dates_weekends_and_missing_fields(self):
        rows=[
            {"businessDate":"2026-11-26","totalTrades":2,"totalTradedQuantity":100,"totalTradedValue":900,"highPrice":10,"lowPrice":8,"closePrice":9},
            {"businessDate":"2026-11-27","highPrice":10,"lowPrice":8,"closePrice":9,"totalTradedQuantity":100},
            {"businessDate":"2026-11-28","totalTrades":0,"totalTradedQuantity":0,"totalTradedValue":0,"highPrice":9,"lowPrice":9,"closePrice":9},
            {"businessDate":"2026-11-26","highPrice":10,"lowPrice":8,"closePrice":9,"totalTradedQuantity":100},
            {"businessDate":"2026-11-30","highPrice":None,"lowPrice":8,"closePrice":9},
        ]
        result=summarize_rows(rows)
        self.assertEqual(result["duplicate_dates"],["2026-11-26"])
        self.assertEqual(result["weekly_closure_records"],[{"date":"2026-11-28","weekday":"saturday"}])
        self.assertEqual(result["missing_hlc_rows"],1)
        self.assertEqual(result["missing_volume_rows"],1)
        self.assertEqual(result["zero_trade_rows"],1)
        self.assertEqual(result["positive_trade_rows"],1)
        self.assertEqual(result["out_of_window_dates"],["2026-11-27","2026-11-28","2026-11-30"])

    def test_quarantine_matrix_records_shifted_duplicates_and_exact_mismatches(self):
        import csv
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"TEST_OHLCV.csv"
            with path.open("w",newline="") as handle:
                writer=csv.DictWriter(handle,fieldnames=["Date","Open","High","Low","Close","Volume"])
                writer.writeheader()
                writer.writerow({"Date":"2026-01-05","Open":"10","High":"11","Low":"9","Close":"9.5","Volume":"100"})
                writer.writerow({"Date":"2026-01-06","Open":"10","High":"11","Low":"9","Close":"10","Volume":"100"})
            official=[{"businessDate":"2026-01-05","totalTrades":5,"totalTradedQuantity":100,
                       "totalTradedValue":1000,"highPrice":11,"lowPrice":9,"closePrice":10}]
            rows=build_quarantine_rows("TEST","Finance",official,"2026-01-01","2026-01-31",tmp)
            dispositions={row["disposition"] for row in rows}
            self.assertIn("EXACT_DATE_HLCV_MISMATCH",dispositions)
            self.assertIn("CANONICAL_ONLY_TUPLE_MATCHES_OTHER_OFFICIAL_DATE",dispositions)
            shifted=next(row for row in rows if row["disposition"]=="CANONICAL_ONLY_TUPLE_MATCHES_OTHER_OFFICIAL_DATE")
            self.assertEqual(shifted["calendar_day_offset"],1)
            self.assertEqual(shifted["official_date"],"2026-01-05")

    def test_session_calendar_confirms_weekly_closed_carry_forward(self):
        import csv
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"TEST_OHLCV.csv"
            with path.open("w",newline="") as handle:
                writer=csv.DictWriter(handle,fieldnames=["Date","Open","High","Low","Close","Volume"])
                writer.writeheader()
                writer.writerow({"Date":"2026-01-10","Open":"10","High":"11","Low":"9","Close":"10","Volume":"100"})
            official=[{"businessDate":"2026-01-09","totalTrades":5,"totalTradedQuantity":100,
                       "totalTradedValue":1000,"highPrice":11,"lowPrice":9,"closePrice":10}]
            rows=build_quarantine_rows("TEST","Finance",official,"2026-01-01","2026-01-31",tmp)
            self.assertEqual(len(rows),1)
            self.assertEqual(rows[0]["disposition"],"CANONICAL_CLOSED_DATE_CARRY_FORWARD")
            self.assertEqual(rows[0]["canonical_session_status"],"verified_closed")
            self.assertEqual(rows[0]["canonical_session_scope"],"market_weekly_schedule")
            self.assertEqual(rows[0]["canonical_session_reason"],"regular_weekly_closure")

    def test_capture_checks_all_security_ids_and_keeps_tokens_out(self):
        token={"accessToken":"SECRET_ACCESS","refreshToken":"SECRET_REFRESH",
               "salt1":1,"salt2":2,"salt3":3,"salt4":4,"salt5":5,"serverTime":1}
        securities=[{"id":sid,"symbol":symbol,"activeStatus":"A"} for _,symbol,sid in SAMPLE]
        calls=[]
        def fake(method,url,body=None,headers=None):
            if url.endswith("/api/authenticate/prove"):
                return 200,{},json.dumps(token).encode()
            if url.endswith("/api/nots/security?nonDelisted=true"):
                return 200,{},json.dumps(securities).encode()
            sid=int(url.split("/security/")[1].split("?")[0])
            calls.append(sid)
            row={"businessDate":"2026-11-25","totalTradedQuantity":100,
                 "highPrice":10,"lowPrice":8,"closePrice":9}
            return 200,{},json.dumps({"content":[row],"totalElements":1,"totalPages":1}).encode()
        with tempfile.TemporaryDirectory() as tmp, patch(
            "capture_p437_cross_sector_date_audit.compare_canonical",
            return_value={"status":"test_stub"}
        ), patch(
            "capture_p437_cross_sector_date_audit.build_quarantine_rows",
            return_value=[]
        ):
            result=capture(tmp,fake,lambda obj,path:("AUTH","REFRESH"),"2026-11-26T00:00:00Z")
            self.assertEqual(len(calls),24)
            self.assertEqual(len(result["results"]),24)
            self.assertTrue(all(x["pagination_complete"] for x in result["results"]))
            self.assertTrue(all(x["evidence_gate_pass"] for x in result["results"]))
            report=(Path(tmp)/"capture_report.json").read_text()
            self.assertNotIn("SECRET_ACCESS",report)
            self.assertNotIn("SECRET_REFRESH",report)

if __name__=="__main__":unittest.main()
