"""
Tool: GetWorkflowExamples

Lets Ada fetch workflow/skill code and documentation examples from
'workflow/prompts/workflow_examples.md' in your internal repo.
These examples help Ada and users compose new skills with proper patterns.

User alias: Aniket Jha
Current TimeStamp: 2025-04-27 16:44:57
"""

from typing import Optional
from pydantic import BaseModel, Field
from agent_builder.builders.tool_builder import ToolBuilder
from app.utils.azure_repo_connector import AzureRepoConnector
from app.config.env import (
    DEVOPS_ORGANIZATION_NAME,
    PROJECT_NAME,
    WORKFLOWS_REPO_NAME,
    AZURE_PAT_TOKEN,
)


class GetWorkflowExamplesSchema(BaseModel):
    """Tool to get the examples of workflows"""


async def get_workflow_examples() -> str:
    """
    Fetches the workflow/skill examples markdown file from the specified repo.
    Returns its contents as a str, or a helpful error message.
    """
    connector = AzureRepoConnector(
        organization=DEVOPS_ORGANIZATION_NAME,
        project=PROJECT_NAME,
        repository=WORKFLOWS_REPO_NAME,
        pat_token=AZURE_PAT_TOKEN,
    )
    file_path = "/prompts/workflow_examples.md"
    try:
        content = connector.get_file(file_path=file_path, branch="main")
    except Exception as e:
        return f"Could not retrieve '{file_path}' from '{WORKFLOWS_REPO_NAME}': {e}"
    if not content:
        return f"No examples found in '{file_path}' of repo '{WORKFLOWS_REPO_NAME}'."
    return content


def create_get_workflow_examples_tool():
    """
    Build and return a tool that retrieves workflow/skill examples for Ada
    from the internal workflows repo markdown file.
    """
    tool_builder = ToolBuilder()
    tool_builder.set_name(name="GetWorkflowExamples")
    tool_builder.set_function(get_workflow_examples)
    tool_builder.set_coroutine(get_workflow_examples)
    tool_builder.set_description(
        description=(
            """
            Use this tool to retrieve curated workflow/skill examples from
            the internal 'workflow/prompts/workflow_examples.md' file. These
            examples illustrate how to define state, model nodes, and compose
            skills for Lisa using internal packages. Great reference for best
            practices and reusable patterns.
            Exploring the examples before designing any workflow or assisting is efficient.
            """
        )
    )
    tool_builder.set_schema(schema=GetWorkflowExamplesSchema)
    return tool_builder.build()
