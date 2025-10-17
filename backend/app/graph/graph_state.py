from typing_extensions import TypedDict
from langgraph.graph import add_messages
from typing import Annotated, Union, cast

from langchain_core.messages import AnyMessage


class Workflow(TypedDict):
    id: str
    title: str
    description: str
    content: str
    # diagram: bytes
    diagram: object
    status: str
    metadata: dict


class LisaState(TypedDict):
    # Each assistant has its own messages channel.
    messages: Annotated[list[AnyMessage], add_messages]
    workflow_configurer_messages: Annotated[list[AnyMessage], add_messages]
    task_executor_messages: Annotated[list[AnyMessage], add_messages]
    workflow: list[Workflow] = None
