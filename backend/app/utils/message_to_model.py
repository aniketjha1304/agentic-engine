from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from app.api_models.invoke_lisa import LisaMessage


def message_to_model(message):
    """
    Convert a BaseMessage object to a LisaMessage object.
    Args:
        message (BaseMessage): A message object (AIMessage, HumanMessage, or SystemMessage).
    Returns:
        dict: Dictionary representation with 'role' and 'content'.
    """

    if isinstance(message, AIMessage):
        role = "assistant"
    elif isinstance(message, HumanMessage):
        role = "user"
    elif isinstance(message, SystemMessage):
        role = "system"

    # Add the content of the message
    content = message.content
    message_model = LisaMessage(
        role=role,
        content=content,
    )
    return message_model
