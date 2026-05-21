"""Tools the agent can call. Phase 1.1: just current_time as a proof of the
tool-calling path. More tools land in phase 1.5."""
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from anthropic import beta_tool


@beta_tool
def get_current_time(timezone: str = "UTC") -> str:
    """Get the current date and time in a given timezone.

    Args:
        timezone: IANA timezone name (e.g., 'Europe/Lisbon', 'America/New_York', 'UTC').
    """
    try:
        tz = ZoneInfo(timezone)
    except ZoneInfoNotFoundError:
        return f"Unknown timezone: {timezone!r}. Use an IANA name like 'Europe/Lisbon'."
    return datetime.now(tz).strftime("%A, %d %B %Y, %H:%M:%S %Z")
