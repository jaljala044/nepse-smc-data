import unittest
from p437_official_eod_helpers import summarize_pages

class P437EodSummaryTests(unittest.TestCase):
    def test_unique_exact_target_row_is_found(self):
        pages=[{"content":[
            {"symbol":"NMLBBL","businessDate":"2024-05-19","openPrice":599.6},
            {"symbol":"SMPDA","businessDate":"2024-05-19","openPrice":1000},
        ]}]
        result=summarize_pages(pages,"NMLBBL","2024-05-19",2)
        self.assertEqual(result["status"],"TARGET_ROW_FOUND")
        self.assertEqual(result["target_row_count"],1)
        self.assertEqual(result["returned_business_dates"],["2024-05-19"])
        self.assertTrue(result["pagination_row_count_matches"])

    def test_missing_target_is_not_no_trade(self):
        pages=[{"content":[{"symbol":"OTHER","businessDate":"2024-05-19"}]}]
        result=summarize_pages(pages,"NMLBBL","2024-05-19",1)
        self.assertEqual(result["status"],"TARGET_ROW_MISSING")
        self.assertNotIn("NO_TRADE",result["status"])
        self.assertEqual(result["target_row_count"],0)

    def test_duplicate_target_rows_are_not_accepted(self):
        row={"symbol":"SMPDA","businessDate":"2024-08-18","closePrice":100}
        result=summarize_pages([{"content":[row,row]}],"SMPDA","2024-08-18",2)
        self.assertEqual(result["status"],"TARGET_ROW_NOT_UNIQUE")
        self.assertEqual(result["target_row_count"],2)

    def test_returned_date_is_recorded_when_business_date_is_ignored(self):
        pages=[{"content":[{"symbol":"NMLBBL","businessDate":"2026-11-26"}]}]
        result=summarize_pages(pages,"NMLBBL","2024-05-19",1)
        self.assertEqual(result["returned_business_dates"],["2026-11-26"])
        self.assertEqual(result["status"],"TARGET_ROW_MISSING")

    def test_incomplete_page_total_is_flagged(self):
        pages=[{"content":[{"symbol":"NMLBBL","businessDate":"2024-05-19"}]}]
        result=summarize_pages(pages,"NMLBBL","2024-05-19",2)
        self.assertFalse(result["pagination_row_count_matches"])

if __name__=="__main__":unittest.main()
