"""
Tool: CreateWorkflow

Lets Ada create a new HTTP-triggered workflow by submitting code and metadata.
Validates code before save. Result is always 'inactive' status. Useful for skill/workflow automation.

"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from agent_builder.builders.tool_builder import ToolBuilder


class CreateWorkflowInput(BaseModel):
    title: str = Field(description="The unique name for the new workflow.")
    description: str = Field(
        description="Brief explanation of what the workflow does and its context. This description would help lisa understand when to run this skill."
    )
    code: str = Field(description="The workflow Python code to validate/save.")
    workflow_input_signature: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="JSON schema for workflow's expected input parameters, if any, as per JSONSchema style.",
    )


# async def create_workflow_tool(
#     workflow_manager,
#     title: str,
#     description: str,
#     code: str,
#     workflow_input_signature: Optional[Dict[str, Any]],
#     user_id: int,
#     organization_id: int,
# ) -> dict:
#     """
#     Create a new HTTP workflow with Ada, always 'inactive' status.
#     """
#     result = await workflow_manager.create_workflow(
#         title=title,
#         description=description,
#         code=code,
#         workflow_input_signature=workflow_input_signature,
#         user_id=user_id,
#         organization_id=organization_id,
#     )
#     return result


def build_create_workflow_tool(workflow_manager) -> dict:
    """
    Construct and return the create workflow tool.
    """
    tool_builder = ToolBuilder()
    tool_builder.set_name(name="CreateWorkflow")
    tool_builder.set_function(workflow_manager.create_workflow)
    tool_builder.set_coroutine(workflow_manager.create_workflow)
    tool_builder.set_description(
        description=(
            """Create a new skill/workflow for the system.
            The workflow will always be created as 'Inactive' for human review.
            Validates the code, saves input signature and description.
            """
        )
    )
    tool_builder.set_schema(schema=CreateWorkflowInput)
    return tool_builder.build()
