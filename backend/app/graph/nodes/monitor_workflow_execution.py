import os
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field
from typing_extensions import Annotated, Literal

from langchain_core.runnables.config import RunnableConfig
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from langsmith import Client
from agent_builder.builders.tool_builder import ToolBuilder


def get_latest_run_details(project_name: str) -> Optional[Dict[str, Any]]:
    """
    Fetch the latest run details for a given project.

    Args:
        project_name (str): The name of the project in LangSmith.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing run details if found, else None.
    """
    client = Client()

    # Fetch the latest run for the project
    runs = list(client.list_runs(project_name=project_name, limit=1, is_root=True))

    if not runs:
        return None

    latest_run = runs[0]
    run_details = client.read_run(latest_run.id, load_child_runs=False)
    run_url = client.get_run_url(run=run_details, project_name=project_name)
    print("Run details: ", run_details)
    run_info = {
        "Run Name": run_details.name,
        "Project Name": project_name,
        "Start Time": (
            run_details.start_time.strftime("%Y-%m-%d %H:%M:%S")
            if run_details.start_time
            else "N/A"
        ),
        "Status": run_details.status,
        "Run URL": run_url,
    }

    return run_info


async def fetch_latest_workflow_run(
    workflow_title: str,
) -> str:
    """
    Fetch the latest run details for a workflow and return run details along with the run URL.

    Args:
        config (RunnableConfig): The configuration for the current execution.
        state (dict): The current application state.
        workflow_title (str): The title of the workflow.

    Returns:
        Command: Contains the response message and direction for the workflow.
    """
    try:

        # Get the latest run details
        run_info = get_latest_run_details(workflow_title)
        if not run_info:
            response_message = f"No runs found for the workflow '{workflow_title}'."
            return response_message

        # Prepare the response message
        response_message = (
            f"Latest run details for workflow '{workflow_title}':\n"
            f"Run Name: {run_info['Run Name']}\n"
            f"Project Name: {run_info['Project Name']}\n"
            f"Start Time: {run_info['Start Time']}\n"
            f"Status: {run_info['Status']}\n"
            f"Run URL: {run_info['Run URL']}\n"
        )

        return response_message
    except Exception as e:
        # Handle exceptions and return an error message
        response_message = f"Error fetching latest run: {str(e)}"
        return response_message


class FetchLatestWorkflowRunInput(BaseModel):
    """Tool to fetch the latest run details for a workflow."""

    workflow_title: str = Field(
        ...,
        description="The title of the workflow.",
    )


def create_workflow_run_tool():
    """
    Build and return the tool for fetching the latest workflow run details.
    """
    tool_builder = ToolBuilder()
    tool_builder.set_name(name="FetchLatestWorkflowRun")
    tool_builder.set_function(fetch_latest_workflow_run)
    tool_builder.set_coroutine(fetch_latest_workflow_run)
    tool_builder.set_description(
        description="Fetch the latest run details for a workflow."
    )
    tool_builder.set_schema(schema=FetchLatestWorkflowRunInput)
    return tool_builder.build()
