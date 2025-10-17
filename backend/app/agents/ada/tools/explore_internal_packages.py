"""
Lets Ada explore internal package files inside Azure DevOps repos by reading their contents.
Intended for AI agents tasked with workflow/skill composition, so they can suggest correct code usage.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from agent_builder.builders.tool_builder import ToolBuilder
from app.utils.azure_repo_connector import AzureRepoConnector
from app.config.env import (
    DEVOPS_ORGANIZATION_NAME,
    PROJECT_NAME,
    AZURE_PAT_TOKEN,
)


class ExploreInternalPackageParams(BaseModel):
    repository: str = Field(
        description="The respository name for the package.",
    )
    file_paths: List[str] = Field(
        description="List of file paths to explore within the repository. Example: ['src/module_a.py', 'README.md']"
    )


async def explore_internal_package(repository: str, file_paths: List[str]) -> str:
    """
    Fetch and summarize contents of specified files inside an internal Azure repo.
    Args:
        repository (str): Name of the Azure repository.
        file_paths (List[str]): List of file paths to fetch.
        branch (str, optional): Branch name (default main).
    Returns:
        str: A summary or content extract from each file.
    """

    azure_repo_connector = AzureRepoConnector(
        organization=DEVOPS_ORGANIZATION_NAME,
        project=PROJECT_NAME,
        repository=repository,
        pat_token=AZURE_PAT_TOKEN,
    )

    file_summaries = []

    for file_path in file_paths:
        try:
            content = azure_repo_connector.get_file(file_path=file_path, branch="main")
        except Exception as e:
            file_summaries.append(f"Could not retrieve '{file_path}': {e}")
            continue

        if not content:
            file_summaries.append(f"File '{file_path}' is empty or not found.")
        elif file_path.endswith((".py", ".js", ".ts", ".json", ".yaml", ".yml")):
            # preview = content[:2000] + (
            #     "\n... (truncated)" if len(content) > 2000 else ""
            # )
            file_summaries.append(f"== File: {file_path} ==\n{content}\n")
        else:
            file_summaries.append(
                f"== File: {file_path} ==\nPreview not available for this filetype.\n"
            )

    response = "\n\n".join(file_summaries)
    if not response:
        response = "No file contents could be retrieved."

    return response


def create_explore_internal_package_tool():
    """
    Build and return the tool that lets Ada explore files/code from an internal Azure DevOps repo.
    """
    tool_builder = ToolBuilder()
    tool_builder.set_name(name="ExploreInternalPackage")
    tool_builder.set_function(explore_internal_package)
    tool_builder.set_coroutine(explore_internal_package)
    tool_builder.set_description(
        description=(
            """
            Use this tool to read and summarize or preview file contents from
            specified internal Azure DevOps repos, such as recall-space-utils or recall-space-agents.
            This helps discover available classes, functions, configuration, and API docs,
            so you can intelligently compose new workflows referencing real package code.
            """
        )
    )
    tool_builder.set_schema(schema=ExploreInternalPackageParams)
    return tool_builder.build()
