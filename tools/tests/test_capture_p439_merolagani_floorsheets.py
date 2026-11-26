import unittest
from decimal import Decimal
from bs4 import BeautifulSoup
from capture_p439_merolagani_floorsheets import (
    extract_form_state,get_total_pages,get_total_records,parse_rows,summarize_day
)

class P439MerolaganiParserTests(unittest.TestCase):
    def test_extract_form_state(self):
        soup=BeautifulSoup('<input name="__VIEWSTATE" value="v1"><input name="__EVENTVALIDATION" value="ev">',"html.parser")
        self.assertEqual(extract_form_state(soup),{"__VIEWSTATE":"v1","__EVENTVALIDATION":"ev"})

    def test_pagination_metadata(self):
        soup=BeautifulSoup("<div>Total pages: 5</div><div>Showing 1 - 500 of 2,345 records</div>","html.parser")
        self.assertEqual(get_total_pages(soup),5)
        self.assertEqual(get_total_records(soup),2345)

    def test_parse_transaction_row(self):
        html="""<table><tr><th>#</th><th>Transact. No.</th><th>Symbol</th><th>Buyer</th><th>Seller</th><th>Quantity</th><th>Rate</th><th>Amount</th></tr>
        <tr><td>1</td><td>2024051905010001</td><td><a title="Nepal Micro">NMLBBL</a></td><td><a title="Broker A">22</a></td><td><a title="Broker B">11</a></td><td>864</td><td>645.21</td><td>557,461.60</td></tr></table>"""
        rows=parse_rows(BeautifulSoup(html,"html.parser"),"2024-05-19")
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["symbol"],"NMLBBL")
        self.assertEqual(rows[0]["transaction_no"],"2024051905010001")
        self.assertEqual(rows[0]["quantity"],Decimal("864"))
        self.assertEqual(rows[0]["amount"],Decimal("557461.60"))
        self.assertEqual(rows[0]["buyer_broker_code"],"22")

    def test_candidate_secondary_evidence_gate(self):
        rows=[{"transaction_no":"2024051905010001","symbol":"NMLBBL","quantity":Decimal("1"),"rate":Decimal("100"),"amount":Decimal("100")}]
        page={"rows":rows,"total_pages":1,"total_records":1}
        rec={"date":"2024-05-19","symbol":"NMLBBL","role":"candidate","expected_rows":1,"expected_volume":"1","expected_turnover":"100"}
        result=summarize_day(rec,[page],1)
        self.assertTrue(result["pagination_complete"])
        self.assertTrue(result["content_valid"])
        self.assertTrue(result["secondary_evidence_gate"])
        self.assertEqual(result["target_transaction_count"],1)

    def test_prior_target_absence_requires_complete_market_pages(self):
        rows=[{"transaction_no":f"202405160501{i:04d}","symbol":"OTHER","quantity":Decimal("1"),"rate":Decimal("100"),"amount":Decimal("100")} for i in range(10)]
        page={"rows":rows,"total_pages":1,"total_records":10}
        rec={"date":"2024-05-16","symbol":"NMLBBL","role":"prior"}
        result=summarize_day(rec,[page],10)
        self.assertTrue(result["target_absent_in_complete_market_sheet"])
        self.assertTrue(result["secondary_evidence_gate"])

    def test_incomplete_page_or_bad_transaction_prefix_fails_gate(self):
        rows=[{"transaction_no":"2024051705010001","symbol":"NMLBBL","quantity":Decimal("1"),"rate":Decimal("100"),"amount":Decimal("100")}]
        page={"rows":rows,"total_pages":2,"total_records":2}
        rec={"date":"2024-05-19","symbol":"NMLBBL","role":"candidate","expected_rows":1,"expected_volume":"1","expected_turnover":"100"}
        result=summarize_day(rec,[page],2)
        self.assertFalse(result["pagination_complete"])
        self.assertEqual(result["transaction_date_prefix_mismatches"],1)
        self.assertFalse(result["secondary_evidence_gate"])

if __name__=="__main__":unittest.main()
