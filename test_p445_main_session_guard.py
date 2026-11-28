import tempfile
import unittest
from pathlib import Path
from scanner_inputs.prepare_scanner_inputs import contract_session_date, validate_floorsheet_sessions


class MainSessionGuardTests(unittest.TestCase):
    def test_prefix(self):
        self.assertEqual(contract_session_date("20261126000001"), "2026-11-26")
        self.assertIsNone(contract_session_date("C1"))

    def validate(self, body, name="floorsheet.csv"):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / name).write_text(body, encoding="utf-8")
            validate_floorsheet_sessions(root)

    def test_matching_and_opaque_ids(self):
        self.validate("contractNo,businessDate\n20261126000001,2026-11-26\nC1,2026-11-26\n")

    def test_mismatch(self):
        with self.assertRaisesRegex(ValueError, "Contract session prefix"):
            self.validate("contractNo,businessDate\n20261126000001,2024-11-26\n")

    def test_ambiguous_dates(self):
        with self.assertRaisesRegex(ValueError, "ambiguous floorsheet field"):
            self.validate("contractNo,businessDate,date\nC1,2026-11-26,2026-11-26\n")

    def test_unsupported_format(self):
        with self.assertRaisesRegex(ValueError, "Unsupported floorsheet format"):
            self.validate("not a CSV", "floorsheet.xlsx")


if __name__ == "__main__":
    unittest.main()
