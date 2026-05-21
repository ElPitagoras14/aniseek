from datetime import datetime, timezone

import pytz


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


def ensure_utc(time_obj: datetime) -> datetime:
    if time_obj.tzinfo is None:
        return time_obj.replace(tzinfo=timezone.utc)
    return time_obj.astimezone(timezone.utc)


def convert_to_user_timezone(utc_dt: datetime, user_timezone: str) -> datetime:
    if not user_timezone or user_timezone == "UTC":
        return utc_dt

    try:
        user_tz = pytz.timezone(user_timezone)
        return utc_dt.astimezone(user_tz)
    except pytz.UnknownTimeZoneError:
        return utc_dt
