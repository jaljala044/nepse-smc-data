import datetime
import unittest

from nepse_session_date import (
    effective_nepse_session_date,
    effective_nepse_session_str,
    non_trading_weekdays,
)


class NepseSessionDateTests(unittest.TestCase):
    def test_old_schedule_kept_sunday_as_a_trading_weekday(self):
        self.assertEqual(non_trading_weekdays(datetime.date(2026, 4, 5)), (4, 5))
        self.assertEqual(
            effective_nepse_session_date(datetime.date(2026, 4, 5)),
            datetime.date(2026, 4, 5),
        )

    def test_old_schedule_skipped_friday_and_saturday(self):
        self.assertEqual(
            effective_nepse_session_date(datetime.date(2026, 4, 3)),
            datetime.date(2026, 4, 2),
        )
        self.assertEqual(
            effective_nepse_session_date(datetime.date(2026, 4, 4)),
            datetime.date(2026, 4, 2),
        )

    def test_new_schedule_starts_monday_2026_04_06(self):
        self.assertEqual(non_trading_weekdays(datetime.date(2026, 4, 6)), (5, 6))
        self.assertEqual(
            effective_nepse_session_date(datetime.date(2026, 4, 6)),
            datetime.date(2026, 4, 6),
        )
        self.assertEqual(
            effective_nepse_session_date(datetime.date(2026, 4, 10)),
            datetime.date(2026, 4, 10),
        )

    def test_new_schedule_skips_saturday_and_sunday(self):
        self.assertEqual(
            effective_nepse_session_date(datetime.date(2026, 4, 11)),
            datetime.date(2026, 4, 10),
        )
        self.assertEqual(
            effective_nepse_session_date(datetime.date(2026, 4, 12)),
            datetime.date(2026, 4, 10),
        )

    def test_string_helper_uses_historical_weekend_regime(self):
        self.assertEqual(
            effective_nepse_session_str(datetime.date(2026, 4, 12)),
            "2026-04-10",
        )

    def test_helper_does_not_claim_to_check_holidays(self):
        # Weekday-compatible dates are returned as-is; callers must consult
        # the dated exchange calendar to reject a public holiday or closure.
        self.assertEqual(
            effective_nepse_session_date(datetime.date(2026, 4, 13)),
            datetime.date(2026, 4, 13),
        )


if __name__ == "__main__":
    unittest.main()
