import json, unittest
from pathlib import Path
from validate_nepse_holiday_capture_index import validate
class HolidayCaptureIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(Path("../reference/nepse_official_holiday_api_capture_mirror_2015_2026.json").read_text())
    def test_index_passes(self): self.assertEqual(validate(self.data),[])
    def test_missing_year_fails(self):
        d=json.loads(json.dumps(self.data)); d["annual_captures"].pop(3)
        self.assertTrue(any("2015-2026" in e for e in validate(d)))
    def test_bad_blob_sha_fails(self):
        d=json.loads(json.dumps(self.data)); d["annual_captures"][0]["files"][0]["git_blob_sha"]="bad"
        self.assertTrue(any("invalid blob SHA" in e for e in validate(d)))
    def test_616_must_remain_unknown(self):
        d=json.loads(json.dumps(self.data)); d["calendar_616_recovery"]["exact_date_list_recovered"]=True
        self.assertTrue(any("unrecovered 616-session" in e for e in validate(d)))
if __name__=="__main__": unittest.main()
