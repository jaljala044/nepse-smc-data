import datetime

NPT = datetime.timezone(datetime.timedelta(hours=5, minutes=45))

# NEPSE changed from Sunday–Thursday trading to Monday–Friday trading
# effective 2026-04-06. This models the weekly weekend only; public holidays,
# special sessions, and exchange-specific closures require a dated session calendar.
MONDAY_FRIDAY_START = datetime.date(2026, 4, 6)
SUNDAY_THURSDAY_NON_TRADING = (4, 5)  # Friday=4, Saturday=5
MONDAY_FRIDAY_NON_TRADING = (5, 6)  # Saturday=5, Sunday=6


def non_trading_weekdays(d: datetime.date) -> tuple[int, int]:
    """Return the weekly closed weekdays for the NEPSE schedule in force on d."""
    if d >= MONDAY_FRIDAY_START:
        return MONDAY_FRIDAY_NON_TRADING
    return SUNDAY_THURSDAY_NON_TRADING


def effective_nepse_session_date(d: datetime.date | None = None) -> datetime.date:
    """Return the most recent weekday-compatible date, not a holiday-verified session.

    For an exact historical trading session, use the date-specific NEPSE session
    calendar. This helper only handles the weekly weekend regime change.
    """
    cur = d or datetime.datetime.now(NPT).date()
    closed = non_trading_weekdays(cur)
    while cur.weekday() in closed:
        cur -= datetime.timedelta(days=1)
        closed = non_trading_weekdays(cur)
    return cur


def effective_nepse_session_str(d: datetime.date | None = None) -> str:
    return effective_nepse_session_date(d).strftime("%Y-%m-%d")
