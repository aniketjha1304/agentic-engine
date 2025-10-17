from datetime import datetime, timezone
from langchain.tools import Tool


def create_get_datetime_tool():
    """
    Build and return the tool for executing workflows.
    """
    # Define a new tool that returns the current datetime
    datetime_tool = Tool(
        name="Datetime",
        func=lambda x: datetime.now(timezone.utc).isoformat(),
        description="Returns the current utc datetime in iso format",
    )
    return datetime_tool
