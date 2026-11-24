import datetime
import unittest

from nepse_session_date import candidate_weekdays, effective_nepse_session_date


class NepseSessionDateTests(unittest.TestCase):
    def test_pre_may_2022_regular_session_is_sunday_through_thursday(self):
        self.assertEqual(candidate_weekdays(datetime.date(2022, 5, 14)), (6, 0, 1, 2, 3))
        self.assertEqual(
            effective_nepse_session_date(datetime.date(2022, 5, 14)),
            datetime.date(2022, 5, 12),
        )

    def test_temporary_monday_friday_regime(self):
        self.assertEqual(candidate_weekdays(datetime.date(2022, 5, 15)), (0, 1, 2, 3, 4))
        self.assertEqual(
            effective_nepse_session_date(datetime.date(2022, 6, 11)),
            datetime.date(2022, 6, 10),
        )

    def test_temporary_sunday_friday_regime(self):
        self.assertEqual(candidate_weekdays(datetime.date(2022, 6, 15)), (6, 0, 1, 2, 3, 4))
        self.assertEqual(
            effective_nepse_session_date(datetime.date(2022, 6, 18)),
            datetime.date(2022, 6, 17),
        )

    def test_sunday_thursday_regime_restored(self):
        self.assertEqual(candidate_weekdays(datetime.date(2022, 9, 17)), (6, 0, 1, 2, 3))
        self.assertEqual(
            effective_nepse_session_date(datetime.date(2022, 9, 17)),
            datetime.date(2022, 9, 15),
        )

    def test_monday_friday_regime_from_april_2026(self):
        self.assertEqual(candidate_weekdays(datetime.date(2026, 4, 6)), (0, 1, 2, 3, 4))
        self.assertEqual(
            effective_nepse_session_date(datetime.date(2026, 11, 25)),
            datetime.date(2026, 11, 25),
        )

    def test_current_regime_skips_saturday_and_sunday(self):
        self.assertEqual(
            effective_nepse_session_date(datetime.date(2026, 11, 29)),
            datetime.date(2026, 11, 27),
        )


if __name__ == "__main__":
    unittest.main()
