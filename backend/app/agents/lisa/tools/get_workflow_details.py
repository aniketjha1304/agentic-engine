"""
Get workflow details with code for given workflow title.
"""

import os
from pydantic import BaseModel, Field
from agent_builder.builders.tool_builder import ToolBuilder
from app.utils.get_existing_workflow_code import get_existing_workflow_code
from app.database.ai_persona_hub_queries import get_workflow_by_title
from app.utils.get_workflow_trigger_data import get_workflow_trigger_data


class GetWorkflowDetails(BaseModel):

    skill_title: str = Field(
        description=("The title of the skill for which details are to be fetch."),
    )


async def get_workflow_details(
    skill_title: str,
) -> str:
    """
    Fetch workflows based on the given title or return all workflows.
    Optionally include the associated code in the details.

    Args:
        workflow_title str: The title of the workflow to fetch.

    Returns:
        str: A response message containing workflow details and optionally the code.
    """
    workflow_data = None
    response_message = ""

    try:
        workflow_data = await get_workflow_by_title(title=skill_title)
        # Check if any workflows were found
        if not workflow_data:
            response_message = (
                "No skills found matching the criteria."
                if skill_title is None
                else f"No skill found with title '{skill_title}'."
            )
            return response_message
        trigger_data = await get_workflow_trigger_data(
            workflow_id=workflow_data["id"], trigger_type=workflow_data["type"]
        )

        file_content = await get_existing_workflow_code(title=skill_title)

        # Create a response message with workflow details and code
        response_message = (
            f"Workflow Details:\n"
            f"Id: {workflow_data.get('id', 'N/A')}\n"
            f"Title: {workflow_data.get('title', 'N/A')}\n"
            f"Description: {workflow_data.get('description', 'N/A')}\n\n"
            f"Additional Trigger Data: {trigger_data}\n"
            f"Skill Code:\n"
            f"{file_content}"
        )

    except Exception as e:
        # Handle exceptions and return an error message
        response_message = f"Error fetching workflow details: {str(e)}"

    return response_message


def create_get_workflow_details_tool():
    """
    Build and return the tool for fetching workflow and their associated code.
    """
    tool_builder = ToolBuilder()
    tool_builder.set_name(name="get-skill-details")
    tool_builder.set_function(get_workflow_details)
    tool_builder.set_coroutine(get_workflow_details)
    tool_builder.set_description(
        description=(
            """
            Use this tool to retrieve comprehensive details of a skill
            based on the provided title.
            It fetches the skill logic, including its code, 
            required parameters ensuring a complete 
            overview of its structure and execution.
            """
        )
    )
    tool_builder.set_schema(schema=GetWorkflowDetails)
    return tool_builder.build()
