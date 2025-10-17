from datetime import datetime
import pytz
from langchain_core.tools import Tool


def create_get_datetime_tool():
    """
    Build and return the tool for getting the current CET datetime.
    """
    cet_tz = pytz.timezone("Europe/Berlin")  # CET/CEST time zone
    datetime_tool = Tool(
        name="get-current-date-time",
        func=lambda x: datetime.now(cet_tz).isoformat(),
        description="Use this tool to get the current date and time in CET (Central European Time).",
    )
    return datetime_tool
