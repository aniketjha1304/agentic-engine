from typing_extensions import Literal
from langgraph.graph import END
from app.graph.graph_state import LisaState
from app.config.default import default_llm_dict
from langchain_core.messages import SystemMessage
from langgraph.types import Command

from app.utils.determine_next_action import (
    determine_next_action,
    NextActionType,
)
from app.graph.default import tool_name_to_assistant_name

from app.graph.nodes.get_workflows import create_get_workflows_tool
from app.graph.nodes.execute_workflow import create_execute_workflow_tool
from app.graph.nodes.monitor_workflow_execution import (
    create_workflow_run_tool,
)
from app.graph.nodes.get_workflow_details import create_get_workflow_details_tool
from app.graph.nodes.get_datetime import create_get_datetime_tool
from app.graph.nodes.workflow_configurer_assistant import (
    DelegateToWorkflowConfigurer,
)
from app.utils.ai_brain import recaller_tool, encoder_tool, brain_with_embeddings
from app.graph.nodes.task_executor_assistant import DelegateToTaskExecutor
from app.utils.route_conversation import transfer_to_assistant


async def gating_assistant(
    state: LisaState,
) -> Command[
    Literal[
        "gating_assistant_tools",
        "task_executor_assistant",
        "workflow_configurer_assistant",
        "__end__",
    ]
]:
    llm = default_llm_dict["azure_openai_gpt4o"]
    llm_instruction = """
    You are Lisa, an intelligent and resourceful material planning assistant.

    ### Your Role:
    As a coordinator and planner, your primary goal is to assist users with
    material planning tasks. You achieve this by efficiently orchestrating workflows,
    executing tasks, and leveraging tools to fulfill user requests. You act as a coworker
    or collaborator, offering clear and helpful assistance tailored to user needs.

    ### Responsibilities:
    1. **Workflow Management**:
    - Execute or monitor existing workflows.
    - Learn and configure new workflows taught by users.

    2. **Request Coordination**:
    - Understand the context of conversations and user requirements.
    - Delegate tasks to specialized tools and assistants via tool calls.
    - Ensure all actions are aligned to fulfill user requests effectively.

    3. **Ad-Hoc Tasks**:
    - Handle non-standard user requests promptly.
    - Apply creative problem-solving to deliver outcomes beyond predefined workflows.

    ### Key Points:
    - **Workflows**: These represent your skills and capabilities,
    broken into sequences of conditional tasks designed to achieve objectives.
    - **Tool Use**: Specialized assistants and tools are accessible
    via tool calls, and you must coordinate their use efficiently.
    - **Outcome Focused**: Your ultimate goal is to meet user demands with clarity, accuracy, and speed.

    Stay attentive to user needs, communicate clearly, and execute your role with precision.
    """

    sys_msg = SystemMessage(content=llm_instruction)

    # The tools could be realized here for LLM binding too.
    llm_with_tools = llm.bind_tools(
        [
            DelegateToWorkflowConfigurer,
            DelegateToTaskExecutor,
            create_get_workflows_tool(),
            create_execute_workflow_tool(),
            create_workflow_run_tool(),
            create_get_workflow_details_tool(),
            create_get_datetime_tool(),
            recaller_tool,
            encoder_tool,
        ],
        parallel_tool_calls=False,
    )
    response = llm_with_tools.invoke([sys_msg] + state["messages"])

    action_type, next_action = determine_next_action(
        response, tool_name_to_assistant_name
    )

    if action_type == NextActionType.AGENT:
        # Transfer control to the specified agent
        update = transfer_to_assistant(
            state=state, response=response, next_agent=next_action
        )
    elif action_type == NextActionType.TOOL:
        next_action = "gating_assistant_tools"
        update = {"messages": [response]}
    else:
        next_action = "__end__"
        update = {"messages": [response]}

    return Command(
        update=update,
        goto=next_action,
    )
