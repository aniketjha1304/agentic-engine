import os
from dotenv import load_dotenv
from typing_extensions import Literal
from pydantic import BaseModel, Field

from langgraph.types import Command
from langchain_core.messages import SystemMessage

from app.graph.graph_state import LisaState
from app.config.default import default_llm_dict
from app.graph.default import tool_name_to_assistant_name

# Import the required tools
from app.graph.nodes.generate_workflow_code import create_generate_workflow_code_tool
from app.graph.nodes.save_workflow import create_save_workflow_tool
from app.utils.determine_next_action import (
    determine_next_action,
    NextActionType,
)
from app.utils.route_conversation import transfer_to_supervisor
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


load_dotenv()


class DelegateToWorkflowConfigurer(BaseModel):
    """
    Use this tool to delegate to the workflow configurer assistant when users
    ask you to set up or configure new workflows, or modify existing ones.
    This assistant understands the requirements,
    plans the workflow, generates the workflow code, asks for questions
    and saves the workflow.
    """

    message: str = Field(..., description="Message for workflow configurer.")


async def workflow_configurer_assistant(
    state: LisaState,
) -> Command[
    Literal[
        "workflow_configurer_tools",
        "gating_assistant",
    ]
]:
    """
    The workflow configurer assistant interacts with the user to create and
    configure workflows. It acts as an algorithmic thinker to understand
    requirements, generate a workflow blueprint, provide detailed instructions
    to the code generation tool, check the generated code, and save the
    workflow. If any issues arise, it asks the user for clarification.
    """
    # Initialize the language model interface
    llm = default_llm_dict["azure_openai_gpt4o"]
    azure_repo_connector = AzureRepoConnector(
        organization=DEVOPS_ORGANIZATION_NAME,
        project=PROJECT_NAME,
        repository=WORKFLOWS_REPO_NAME,
        pat_token=AZURE_PAT_TOKEN,
    )
    # Step 3: Determine branch based on the workflow status
    file_content = azure_repo_connector.get_file(
        file_path=f"/prompts/workflow_configurer.md",
        branch=DEFAULT_WORKFLOW_BRANCH_NAME,
    )
    workflow_template = azure_repo_connector.get_file(
        file_path=f"/templates/workflow_template.txt",
        branch=DEFAULT_WORKFLOW_BRANCH_NAME,
    )

    # Define the system prompt to guide the assistant's behavior
    llm_instruction = f""" 
    {file_content}
    Workflow Template: {workflow_template}
    """

    sys_msg = SystemMessage(content=llm_instruction)

    # Bind the necessary tools to the language model
    llm_with_tools = llm.bind_tools(
        [
            create_generate_workflow_code_tool(),
            create_save_workflow_tool(),
        ],
        parallel_tool_calls=False,
    )

    # Invoke the language model with the system message and conversation history
    response = await llm_with_tools.ainvoke(
        [sys_msg] + state["workflow_configurer_messages"]
    )

    # Determine the next action based on the language model's response
    action_type, next_action = determine_next_action(
        response, tool_name_to_assistant_name
    )

    if action_type == NextActionType.END:
        # End the conversation and return to the gating assistant
        next_action = "gating_assistant"
        update = transfer_to_supervisor(
            state=state, response=response, agent_name="workflow_configurer_assistant"
        )
    elif action_type == NextActionType.TOOL:
        # Proceed to use the tools bound to the assistant
        next_action = "workflow_configurer_tools"
        update = {"workflow_configurer_messages": [response]}
    else:
        # Continue the conversation
        update = {"workflow_configurer_messages": [response]}

    return Command(
        update=update,
        goto=next_action,
    )
