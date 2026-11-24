from github_floorsheet_pull import extract_trading_date, normalize_date_str


def test_normalize_valid_date():
    assert normalize_date_str("2026", "11", "24") == "2026-11-24"


def test_normalize_rejects_invalid_date():
    assert normalize_date_str("2026", "02", "30") is None


def test_extract_ymd_from_page_text():
    assert extract_trading_date("Trading Date: 2026-11-24", [], "fallback") == "2026-11-24"


def test_extract_dmy_from_page_text():
    assert extract_trading_date("Trading Date: 24/11/2026", [], "fallback") == "2026-11-24"


def test_extract_date_from_contract_number():
    rows = [["2026112400001", "NABIL", "1", "2", "10", "500", "5000"]]
    assert extract_trading_date("", rows, "fallback") == "2026-11-24"


def test_fallback_is_explicit_when_source_date_missing():
    assert extract_trading_date("No date shown", [], "2026-11-24") == "2026-11-24"
