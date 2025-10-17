from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from app.graph.graph_state import LisaState
from app.graph.default import assistant_name_to_message_key


def transfer_to_assistant(state: LisaState, response: AIMessage, next_agent: str):
    """
    Validates the last response and transfers a message to another assistant.

    Args:
        state (LisaState): The current state containing messages.
        response: The response message from the assistant.
        next_agent (str): The name of the next assistant to transfer to.

    Returns:
        dict or None: An update dictionary containing the transformed messages or None if validation fails.
    """

    # Retrieve the tool call from the last AIMessage
    tool_call = response.tool_calls[0]

    # Get the sender message from the tool call
    sender_message = tool_call.get("args", {}).get("message")
    if not sender_message:
        return None

    # Find the corresponding key for the next agent
    message_key = assistant_name_to_message_key.get(next_agent)

    # Convert the sender message to a HumanMessage
    transformed_message = HumanMessage(content=sender_message)
    return {message_key: [transformed_message], "messages": [response]}


def transfer_to_supervisor(state: LisaState, response: AIMessage, agent_name: str):
    """
    Transfers the last AI message to a supervisor by converting it into a ToolMessage.

    Args:
        state (LisaState): The current state containing messages.
        agent_name (str): The name of the agent to find the message key.

    Returns:
        dict or None: An update dictionary containing the modified messages or None if validation fails.
    """
    # Fetch the key for the agent name
    message_key = assistant_name_to_message_key.get(agent_name)

    # NOTE: Assuming the last message has only one tool call for this current agent.
    tool_call = state["messages"][-1].tool_calls[0]
    tool_message = ToolMessage(content=response.content, tool_call_id=tool_call["id"])

    return {"messages": [tool_message], message_key: [response]}
