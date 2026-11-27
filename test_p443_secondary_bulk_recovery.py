"""Regression checks for secondary contract normalization and integrity."""
import unittest
from collections import Counter
from decimal import Decimal
from tools.p443_full_session_parity import signature

class SecondaryContractTests(unittest.TestCase):
    def row(self,contract="2024081401000001"):
        return {"contract_no":contract,"calculation_date":"2024-08-14","stock_symbol":"API","buyer":"14","seller":"17","quantity":"10","rate":"200.50","amount":"2005"}
    def test_normalized_duplicate(self):
        rows=[self.row(),self.row("'2024081401000001")]
        keys=[signature(r,True,"2024-08-14") for r in rows]
        self.assertEqual(keys[0],keys[1])
        self.assertEqual(sum(n-1 for n in Counter(k[1] for k in keys).values()),1)
    def test_fields(self):
        k=signature(self.row(),True,"2024-08-14")
        self.assertEqual(k[2],"API")
        self.assertEqual(k[5:8],(Decimal(10),Decimal("200.50"),Decimal(2005)))
    def test_invalid_fields(self):
        for field,value in [("quantity","1.5"),("rate","NaN"),("amount","999"),("buyer","x"),("contract_no","2e15"),("calculation_date","2024-08-15")]:
            with self.subTest(field=field):
                row=self.row();row[field]=value
                with self.assertRaises(ValueError):signature(row,True,"2024-08-14")
if __name__=="__main__":unittest.main()
