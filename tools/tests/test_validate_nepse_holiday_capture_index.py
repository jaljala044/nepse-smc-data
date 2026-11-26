import json, unittest
from pathlib import Path
from validate_nepse_holiday_capture_index import validate

class HolidayCaptureIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(Path("../reference/nepse_official_holiday_api_capture_mirror_2015_2025.json").read_text())

    def test_committed_index_passes(self):
        self.assertEqual(validate(self.data), [])

    def test_missing_annual_capture_fails(self):
        data = json.loads(json.dumps(self.data))
        data["years"].pop(3)
        self.assertTrue(any("2015-2026" in e for e in validate(data)))

    def test_unpinned_blob_fails(self):
        data = json.loads(json.dumps(self.data))
        data["years"][0]["files"][0]["git_blob_sha"] = "bad"
        self.assertTrue(any("invalid Git blob SHA" in e for e in validate(data)))

    def test_616_must_remain_unknown(self):
        data = json.loads(json.dumps(self.data))
        data["calendar_616_recovery"]["exact_date_list_recovered"] = True
        self.assertTrue(any("unrecovered 616-date" in e for e in validate(data)))

if __name__ == "__main__":
    unittest.main()
