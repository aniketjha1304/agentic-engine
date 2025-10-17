"""
Tool to generate workflow code based on detailed steps and algorithm provided
by the workflow_configurer_assistant.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage

from app.config.default import default_llm_dict
from agent_builder.builders.tool_builder import ToolBuilder
from app.utils.azure_repo_connector import AzureRepoConnector
from app.config.env import (
    DEVOPS_ORGANIZATION_NAME,
    PROJECT_NAME,
    WORKFLOWS_REPO_NAME,
    AZURE_PAT_TOKEN,
)
from app.config.default import (
    DEFAULT_WORKFLOW_BRANCH_NAME,
)


async def generate_workflow_code(
    workflow_description: str,
    workflow_title: str,
    additional_notes: Optional[str] = None,
    requires_human_input: bool = False,
) -> str:
    """
    Generate workflow code based on the provided detailed steps and algorithm.
    Include any additional notes in the generation process.

    Args:
        workflow_description (str): Detailed steps and algorithm for the workflow.
        additional_notes (str, optional): Any additional notes or comments.
        requires_human_input (boolean, optional): Whether human input is required during execution.

    Returns:
        str: Generated workflow code or an error message if the process fails.
    """
    try:
        # Initialize the LLM
        llm = default_llm_dict["azure_openai_gpt4o"]

        # Include the workflow description and additional notes (if any) in the user message
        user_message_content = f"""Generate workflow code based on
        the following workflow description:\n\n{workflow_description}
        workflow title: {workflow_title}
        trace_project (To be added in workflow code for tracing): {workflow_title}
        """

        if additional_notes:
            user_message_content += f"\n\nAdditional Notes:\n{additional_notes}"

        azure_repo_connector = AzureRepoConnector(
            organization=DEVOPS_ORGANIZATION_NAME,
            project=PROJECT_NAME,
            repository=WORKFLOWS_REPO_NAME,
            pat_token=AZURE_PAT_TOKEN,
        )
        # Step 3: Determine branch based on the workflow status
        # Fetch the prompt from the workflow repository.
        file_content = azure_repo_connector.get_file(
            file_path=f"/prompts/workflow_code_generator.md",
            branch=DEFAULT_WORKFLOW_BRANCH_NAME,
        )
        if requires_human_input is True:
            workflow_template = azure_repo_connector.get_file(
                            file_path=f"/templates/require_human_input_workflow_template.txt",
                            branch=DEFAULT_WORKFLOW_BRANCH_NAME,
                        )
        else:
            workflow_template = azure_repo_connector.get_file(
                file_path=f"/templates/workflow_template.txt",
                branch=DEFAULT_WORKFLOW_BRANCH_NAME,
            )

        # Define the system prompt to guide the assistant's behavior
        llm_instruction = f""" 
            {file_content}
            Pre-defined Workflow Template: {workflow_template}
        """
        # Create the system and user messages
        sys_msg = SystemMessage(content=llm_instruction)
        user_msg = HumanMessage(content=user_message_content)

        # Invoke the LLM to generate the workflow code
        response = await llm.ainvoke([sys_msg, user_msg])

        # Extract the generated code from the response
        generated_code = response.content

        # Prepare the response message
        response_message = (
            f"Here is the generated workflow code based on your description:\n\n"
            f"{generated_code}\n"
        )

        # Return the response
        return response_message

    except Exception as e:
        # Handle exceptions and return an error message
        response_message = f"Error generating workflow code: {str(e)}"
        return response_message


class GenerateWorkflowCode(BaseModel):
    """
    Tool to generate workflow code based on provided workflow description
    and additional notes.
    """

    workflow_description: str = Field(
        ..., description="Detailed steps and algorithm for the workflow."
    )
    workflow_title: str = Field(..., description="Title of the workflow.")
    requires_human_input: bool = Field(..., description="Whether human input is required during workflow execution.")
    additional_notes: Optional[str] = Field(
        default=None,
        description="""Any additional notes or comments. Existing workflow 
        code could be provided here when adjusting or updating existing workflow""",
    )


def create_generate_workflow_code_tool():
    """
    Build and return the tool for generating workflow code.
    """
    tool_builder = ToolBuilder()
    tool_builder.set_name(name="GenerateWorkflowCode")
    tool_builder.set_function(generate_workflow_code)
    tool_builder.set_coroutine(generate_workflow_code)
    tool_builder.set_description(
        description=(
            """Use this tool to generate workflow code based on the provided 
            blueprint, which includes detailed steps and algorithms. 
            The code is assembled using predefined, modular components that 
            are pre-configured with access to the user's organizational data, 
            such as email systems, task management tools, and site permissions.
            The workflow code is generated using the template."""
        )
    )
    tool_builder.set_schema(schema=GenerateWorkflowCode)
    return tool_builder.build()
