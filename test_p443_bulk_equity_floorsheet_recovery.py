"""Regression tests for bounded bulk floorsheet evidence recovery."""
import unittest
from decimal import Decimal

from tools.p443_bulk_equity_floorsheet_recovery import (
    build_expected_tuples,
    classify_request,
    select_dates,
)


class BulkFloorsheetRecoveryTests(unittest.TestCase):
    def test_loads_each_pinned_source_once_and_preserves_tuple_conflicts(self):
        keys = {("AAA", "2025-01-02"), ("BBB", "2025-01-02")}
        refs = {
            ("AAA", "2025-01-02"): {
                ("ohlcv/shared.csv", "blob-a", "2"),
                ("ohlcv/shared.csv", "blob-a", "3"),
            },
            ("BBB", "2025-01-02"): {
                ("ohlcv/shared.csv", "blob-a", "4"),
            },
        }
        calls = []

        def loader(path, blob):
            calls.append((path, blob))
            return {
                "2": ("2025-01-02", (Decimal("10"), Decimal("12"), Decimal("9"), Decimal("11"), Decimal("100"))),
                "3": ("2025-01-02", (Decimal("10"), Decimal("12"), Decimal("9"), Decimal("11"), Decimal("100"))),
                "4": ("2025-01-02", (Decimal("20"), Decimal("22"), Decimal("19"), Decimal("21"), Decimal("200"))),
            }

        expected = build_expected_tuples(keys, refs, loader)
        self.assertEqual(calls, [("ohlcv/shared.csv", "blob-a")])
        self.assertEqual(len(expected[("AAA", "2025-01-02")]), 1)
        self.assertEqual(len(expected[("BBB", "2025-01-02")]), 1)

    def test_conflicting_source_tuples_are_preserved_for_review(self):
        keys = {("AAA", "2025-01-02")}
        refs = {
            ("AAA", "2025-01-02"): {
                ("ohlcv/a.csv", "blob-a", "2"),
                ("ohlcv/b.csv", "blob-b", "2"),
            }
        }

        def loader(path, blob):
            close = "11" if path.endswith("a.csv") else "12"
            return {
                "2": ("2025-01-02", (
                    Decimal("10"), Decimal("12"), Decimal("9"),
                    Decimal(close), Decimal("100")
                ))
            }

        expected = build_expected_tuples(keys, refs, loader)
        self.assertEqual(len(expected[("AAA", "2025-01-02")]), 2)
        self.assertEqual(
            classify_request(expected[("AAA", "2025-01-02")], [], True, "PASS"),
            "SOURCE_TUPLE_CONFLICT",
        )

    def test_rejects_wrong_source_date_and_missing_lineage_row(self):
        keys = {("AAA", "2025-01-02")}
        refs = {("AAA", "2025-01-02"): {("ohlcv/a.csv", "blob-a", "2")}}
        with self.assertRaisesRegex(ValueError, "date mismatch"):
            build_expected_tuples(
                keys, refs,
                lambda *_: {"2": ("2025-01-03", (Decimal("1"),) * 5)},
            )
        with self.assertRaisesRegex(ValueError, "row missing"):
            build_expected_tuples(keys, refs, lambda *_: {})

    def test_date_selection_is_deterministic_and_bounded(self):
        bydate = {"2025-01-03": {"A"}, "2025-01-02": {"A", "B"}, "2025-01-01": {"A", "B"}}
        inventory = {day: {"date": day} for day in bydate}
        self.assertEqual(
            select_dates(bydate, inventory, 2),
            ["2025-01-01", "2025-01-02"],
        )
        with self.assertRaises(ValueError):
            select_dates(bydate, inventory, 0)

    def test_classification_never_calls_missing_rows_no_trade(self):
        expected = {
            (Decimal("10"), Decimal("12"), Decimal("9"), Decimal("11"), Decimal("100"))
        }
        self.assertEqual(
            classify_request(expected, [], True, "PASS"),
            "NO_OBSERVED_CONTRACT_UNKNOWN",
        )
        self.assertEqual(
            classify_request(expected, [], True, None),
            "AVAILABLE_NOT_FETCHED",
        )
        self.assertEqual(
            classify_request(expected, [], False, None),
            "NO_PINNED_PARTITION",
        )

    def test_high_low_volume_match_does_not_claim_open_close_match(self):
        expected = {
            (Decimal("10"), Decimal("12"), Decimal("9"), Decimal("11"), Decimal("100"))
        }
        observed = [(Decimal("12"), Decimal("60"), "C1"), (Decimal("9"), Decimal("40"), "C2")]
        self.assertEqual(
            classify_request(expected, observed, True, "PASS"),
            "HIGH_LOW_VOLUME_MATCH_OPEN_CLOSE_UNVERIFIED",
        )


if __name__ == "__main__":
    unittest.main()
