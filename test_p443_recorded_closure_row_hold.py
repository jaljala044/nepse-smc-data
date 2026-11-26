import unittest
from tools.p443_recorded_closure_row_hold import adjudicate

def pair(**kw):
    r=dict(pair_classification="PAIR_CONTAINS_RECORDED_CLOSURE",path="ABC.csv",blob_sha="fixture",symbol="ABC",date="2026-01-02",row="3",calendar_evidence="closed",previous_date="2026-01-01",previous_row="2",previous_calendar_evidence="open")
    r.update(kw)
    return r

class ClosureRowHoldTests(unittest.TestCase):
    def test_only_closed_side(self):
        n,rows=adjudicate([pair()])
        self.assertEqual(n,1)
        self.assertEqual(list(rows),[("ABC.csv","fixture","3")])
    def test_previous_closed_side(self):
        _,rows=adjudicate([pair(calendar_evidence="open",previous_calendar_evidence="closed")])
        self.assertEqual(list(rows),[("ABC.csv","fixture","2")])
    def test_shared_row_deduplicated(self):
        n,rows=adjudicate([pair(),pair(date="2026-01-03",row="4",calendar_evidence="open",previous_date="2026-01-02",previous_row="3",previous_calendar_evidence="closed")])
        self.assertEqual(n,2)
        self.assertEqual(len(rows),1)
    def test_conflict_pair_not_adjudicated(self):
        self.assertEqual(adjudicate([pair(pair_classification="CONFLICTING_EVIDENCE")]),(0,{}))
