from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import json


def model_to_message(message):
    """
    Convert a dictionary to an BaseMessage object.
    """
    message_with_schema = None
    if message["role"] == "assistant":
        message_with_schema = AIMessage(content=message["content"])

    if message["role"] == "user":
        message_with_schema = HumanMessage(content=message["content"])

    if message["role"] == "system":
        message_with_schema = SystemMessage(content=message["content"])
    return message_with_schema


def database_to_message(message):
    """
    Convert a database message entry into the corresponding message schema.
    Handles both JSON and string content.
    """
    text_content = ""
    workflow = None

    # Process content based on its type
    if isinstance(message["content"], str):
        try:
            # Attempt to parse as JSON
            content = json.loads(message["content"])
            if isinstance(content, dict):
                text_content = content.get("text", "")
                workflow = content.get("workflow", None)
            else:
                # If JSON isn't a dictionary, treat it as plain text
                text_content = message["content"]
        except json.JSONDecodeError:
            # If it's not JSON, treat it as plain text
            text_content = message["content"]
    elif isinstance(message["content"], dict):
        text_content = message["content"].get("text", "")
        workflow = message["content"].get("workflow", None)
    if workflow:
        text_content = f"""
        {text_content}
        Worflow: {workflow}
        """
    # Map to the appropriate schema
    message_with_schema = None
    if message["role"] == "assistant":
        message_with_schema = AIMessage(content=text_content)
    elif message["role"] == "user":
        message_with_schema = HumanMessage(content=text_content)
    elif message["role"] == "system":
        message_with_schema = SystemMessage(content=text_content)
    return message_with_schema
