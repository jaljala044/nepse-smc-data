import datetime

NPT = datetime.timezone(datetime.timedelta(hours=5, minutes=45))
NON_TRADING_WEEKDAYS = (5, 6)  # Saturday=5, Sunday=6; change to (4, 5) if Sun-Thu trading days


def effective_nepse_session_date(d: datetime.date | None = None) -> datetime.date:
    cur = d or datetime.datetime.now(NPT).date()
    while cur.weekday() in NON_TRADING_WEEKDAYS:
        cur -= datetime.timedelta(days=1)
    return cur


def effective_nepse_session_str(d: datetime.date | None = None) -> str:
    return effective_nepse_session_date(d).strftime("%Y-%m-%d")
