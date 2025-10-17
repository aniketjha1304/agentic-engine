"""
Tool to save or update a workflow by verifying, saving metadata, 
and committing code to Azure DevOps.
"""

import re
import os
import uuid
import json
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from typing_extensions import Annotated
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from langchain_core.runnables.config import RunnableConfig
from langchain_core.messages import ToolMessage

from app.utils.azure_repo_connector import AzureRepoConnector
from app.utils.run_code import run_code
from app.utils.postgres_connector import PostgresConnector
from app.graph.graph_state import Workflow
from app.utils.generate_folder_name import generate_folder_name
from app.utils.get_workflow_diagram import get_workflow_diagram
from app.config.env import (
    DEVOPS_ORGANIZATION_NAME,
    PROJECT_NAME,
    WORKFLOWS_REPO_NAME,
    AZURE_PAT_TOKEN,
)
from app.config.default import (
    DEFAULT_WORKFLOW_STATUS,
    DEFAULT_WORKFLOW_BRANCH_NAME,
    WORKFLOW_TYPE_HTTP_TRIGGER,
    WORKFLOW_TYPE_SCHEDULED,
)
from agent_builder.builders.tool_builder import ToolBuilder
from app.database.ai_persona_hub_queries import (
    get_workflow_by_title,
    save_workflow,
    update_workflow,
)

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# TODO: Refactor his code such that now the workflow type is defined nicely.
async def save_or_update_workflow(
    config: RunnableConfig,
    state: Annotated[dict, InjectedState],
    title: str,
    description: str,
    code: str,
    is_scheduled: bool = False,
    workflow_input_signature: Optional[Dict[str, Any]] = {},
    cron_expression: str = None,
) -> Command[Literal["workflow_configurer_assistant"]]:
    """
    Save or update a workflow by verifying, saving metadata,
    and committing code to Azure DevOps.

    Args:
        config (RunnableConfig): Configuration for the current execution.
        state (dict): Injected state dictionary.
        title (str): The title of the workflow.
        description (str): A brief description of the workflow.
        code (str): The workflow code in Python.
        env_json (Dict[str, Any]): Environment variables for the workflow.
        is_scheduled (bool, optional): Indicates if the workflow is scheduled.
        trace_project (Optional[str], optional): Trace project name for monitoring.
        trace_api_key (Optional[str], optional): Trace API key for monitoring.
        metadata (Optional[Dict[str, Any]], optional): Additional metadata.

    Returns:
        Command: A command to update the state and determine the next step.
    """
    workflow_state_data = None
    response_message = ""
    workflow_input_signature = json.dumps(workflow_input_signature)
    try:
        file_name = generate_folder_name(title=title)
        file_path = f"/workflows/{file_name}/{file_name}.py"
        # Extract user and organization IDs from the config
        user_id = int(config.get("configurable", {}).get("user_id"))
        organization_id = int(config.get("configurable", {}).get("organization_id"))

        # Initialize variables
        status = DEFAULT_WORKFLOW_STATUS
        workflow_id = None

        # Validate metadata based on scheduling
        if is_scheduled and cron_expression is None:
            raise ValueError("Scheduled workflows require 'cron_expression'.")

        existing_workflow = await get_workflow_by_title(title)

        # Prepare workflow data for insertion or update
        # TODO: Use the utility function and refactor with database change
        logger.info(f"Existing workflow: {existing_workflow}")
        workflow_data = {
            # "id": workflow_id,
            "title": title,
            "status": status,
            "description": description,
            "organization_id": organization_id,
            "accountable_user_id": user_id,
            "type": (
                WORKFLOW_TYPE_SCHEDULED if is_scheduled else WORKFLOW_TYPE_HTTP_TRIGGER
            ),
            "source_code_location": file_path,
        }
        if is_scheduled:
            workflow_data.update({"cron_expression": cron_expression})
        else:
            workflow_data.update({"workflow_input_state": workflow_input_signature})

        logger.info("workflow_data before database operation: ", workflow_data)
        if existing_workflow:
            workflow_id = existing_workflow["id"]
            workflow_data.update({"id": workflow_id})
            data = await update_workflow(
                workflow_id=workflow_id, workflow_data=workflow_data
            )
        else:
            workflow_id = str(uuid.uuid4())
            workflow_data.update({"id": workflow_id})
            data = await save_workflow(workflow_data=workflow_data)
        if data["success"]:
            response_message += " Workflow metadata saved "

        logger.info(f"Database operation result: {data}")
        # Commit the workflow code to Azure DevOps
        azure_repo_connector = AzureRepoConnector(
            organization=DEVOPS_ORGANIZATION_NAME,
            project=PROJECT_NAME,
            repository=WORKFLOWS_REPO_NAME,
            pat_token=AZURE_PAT_TOKEN,
        )
        changes = {file_path: code}
        commit_message = f"Commit by Lisa for saving workflow '{title}'"

        azure_repo_connector.push_changes(
            changes=changes,
            branch=DEFAULT_WORKFLOW_BRANCH_NAME,
            commit_message=commit_message,
        )

        response_message += " Workflow code committed to Azure DevOps."

        workflow_state_data = Workflow(
            id=workflow_data["id"],
            title=workflow_data["title"],
            description=workflow_data["description"],
            content=code,
            diagram=get_workflow_diagram(workflow_code=code),
            status=workflow_data["status"],
            is_scheduled=is_scheduled,
        )

    except Exception as e:
        # Handle errors and prepare error message
        response_message = f"Error saving workflow: {str(e)}"

    # Update state and return command
    tool_call = state["workflow_configurer_messages"][-1].tool_calls[0]
    tool_message = ToolMessage(content=response_message, tool_call_id=tool_call["id"])
    update = {
        "workflow_configurer_messages": [tool_message],
        "workflow": [workflow_state_data] if workflow_state_data is not None else [],
    }

    return Command(
        update=update,
        goto="workflow_configurer_assistant",
    )


class SaveWorkflowInput(BaseModel):
    """
    Input schema for saving or updating a workflow.

    This schema defines the necessary and optional fields required to create
    or update a workflow in the system, including its metadata, configuration,
    and scheduling details.
    """

    title: str = Field(
        ...,
        description="The title of the workflow. This serves as a unique identifier or display name for the workflow.",
    )
    description: str = Field(
        ...,
        description="A brief description of the workflow. This should provide a concise overview of its purpose or functionality.",
    )
    code: str = Field(
        ...,
        description="The Python code that defines the workflow logic. This should include all necessary functions and operations for execution.",
    )
    is_scheduled: bool = Field(
        default=False,
        description="Indicates whether the workflow is scheduled to run automatically. Set to 'True' for scheduled workflows, otherwise 'False'.",
    )
    workflow_input_signature: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description=(
            "Provide a JSON Schema defining the expected input parameters for HTTP-triggered workflows or manually run workflows with defined input parameters. "
            "The schema should describe the structure, data types, and any constraints for the input. For example:\n\n"
            "{\n"
            '  "type": "object",\n'
            '  "properties": {\n'
            '    "user_name": {"type": "string"},\n'
            '    "age": {"type": "integer", "minimum": 18}\n'
            "  },\n"
            '  "required": ["user_name"]\n'
            "}\n\n"
            "This schema will be stored in the database for future reference,such as when triggering workflows programmatically or for documentation purposes."
            " Note: This has to be provided only when workflow input parameters are defined in workflow code."
        ),
    )
    cron_expression: Optional[str] = Field(
        description=(
            "Specifies the scheduling details for the workflow in cron expression format. "
            "Cron expressions are used to define recurring schedules and follow the format: 'minute hour day month day-of-week'. "
            "Example: '0 9 * * 1-5' means every weekday at 9:00 AM."
        )
    )
    state: Annotated[dict, InjectedState] = Field(
        description="The state of the workflow's graph."
    )


def create_save_workflow_tool():
    """
    Build and return the tool for saving or updating a workflow.
    """
    tool_builder = ToolBuilder()
    tool_builder.set_name(name="SaveWorkflow")
    tool_builder.set_function(save_or_update_workflow)
    tool_builder.set_coroutine(save_or_update_workflow)
    tool_builder.set_description(
        description=(
            "Save or update a workflow by verifying, saving metadata, "
            "and committing code to Azure DevOps. To be used after generating the workflow code so that it is persisted"
        )
    )
    tool_builder.set_schema(schema=SaveWorkflowInput)
    tool_builder.set_max_iterations(max_iterations=4)
    return tool_builder.build()
