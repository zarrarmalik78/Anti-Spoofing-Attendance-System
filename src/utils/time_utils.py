import datetime
import pytz

# Pakistan Standard Time
PKT_TIMEZONE = pytz.timezone('Asia/Karachi')

def get_current_time() -> datetime.datetime:
    """Returns the current time in Pakistan Standard Time."""
    return datetime.datetime.now(PKT_TIMEZONE)

def get_current_time_str(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Returns the current time string in PKT."""
    return get_current_time().strftime(format_str)
