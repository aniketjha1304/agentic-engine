from typing import Dict, Any, Tuple, Optional
from enum import Enum


class NextActionType(Enum):
    AGENT = "agent"
    TOOL = "tool"
    END = "__end__"


def determine_next_action(
    response: Any, tool_to_agent_mapping: Dict[str, str]
) -> Tuple[NextActionType, Optional[str]]:
    """
    Determines the next action based on tool calls in the response.

    Args:
        response (Any): The response object containing potential tool calls.
        tool_to_agent_mapping (Dict[str, str]): Mapping of tool names to agent names.

    Returns:
        Tuple[NextActionType, Optional[str]]:
            A tuple containing the signal type and the name of the next action.
    """
    # Check if the response has tool calls
    if hasattr(response, "tool_calls") and response.tool_calls:
        for tool_call in response.tool_calls:
            tool_name = tool_call.get("name")
            if tool_name:
                if tool_name in tool_to_agent_mapping:
                    # The tool is mapped to an agent
                    next_agent = tool_to_agent_mapping[tool_name]
                    return NextActionType.AGENT, next_agent
                return NextActionType.TOOL, tool_name
        # If no valid tool calls found, default to tool with no name
        return NextActionType.TOOL, None
    else:
        # No tool calls; the conversation can end
        return NextActionType.END, None
