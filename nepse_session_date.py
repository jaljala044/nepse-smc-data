"""NEPSE weekday-session candidates by published trading-week regime.

This helper is a weekday filter only. It cannot determine exchange holidays,
exceptional suspensions, or special sessions. Use the evidence-backed session
calendar before treating a date as an actual open session.
"""
import datetime

NPT = datetime.timezone(datetime.timedelta(hours=5, minutes=45))


def candidate_weekdays(day: datetime.date) -> tuple[int, ...]:
    """Return candidate weekdays for the published NEPSE schedule regime.

    Python weekday numbers: Monday=0 ... Sunday=6.
    Regime boundaries follow the project's session-calendar research.
    """
    if day <= datetime.date(2022,  5, 14):
        # Sunday-Thursday regular session; Friday odd-lot is not a regular session.
        return (6, 0, 1, 2, 3)
    if day <= datetime.date(2022, 6, 14):
        # Temporary Monday-Friday schedule from 15 May 2022.
        return (0, 1, 2, 3, 4)
    if day <= datetime.date(2022, 9, 16):
        # Temporary Sunday-Friday schedule from 15 June 2022.
        return (6, 0, 1, 2, 3, 4)
    if day <= datetime.date(2026, 4, 5):
        # Sunday-Thursday schedule restored from 17 September 2022.
        return (6, 0, 1, 2, 3)
    # Monday-Friday schedule reported effective 6 April 2026.
    return (0, 1, 2, 3, 4)


def effective_nepse_session_date(d: datetime.date | None = None) -> datetime.date:
    """Return the latest weekday candidate, not a verified exchange session.

    Exchange holidays, suspensions and exceptional openings are not inferred.
    """
    cur = d or datetime.datetime.now(NPT).date()
    while cur.weekday() not in candidate_weekdays(cur):
        cur -= datetime.timedelta(days=1)
    return cur


def effective_nepse_session_str(d: datetime.date | None = None) -> str:
    return effective_nepse_session_date(d).strftime("%Y-%m-%d")
