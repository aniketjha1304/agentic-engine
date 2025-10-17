"""
Pydantic models for MongoDB collections
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4


class Message(BaseModel):
    """Message model for chat messages"""

    role: str = Field(..., description="Role of the message sender (user/assistant)")
    content: str = Field(..., description="Content of the message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Chat(BaseModel):
    """Chat model for storing conversations"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., description="Name/title of the chat")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    messages: List[Message] = Field(
        default_factory=list, description="List of messages in the chat"
    )
    agent_name: Optional[str] = Field(
        None, description="Name of the agent associated with this chat"
    )


class Workflow(BaseModel):
    """Workflow model for storing agent workflows"""

    name: str = Field(..., description="Unique name/identifier of the workflow")
    code: str = Field(..., description="Code/implementation of the workflow")
    status: str = Field(
        default="inactive", description="Status of the workflow (active/inactive)"
    )
    endpoint: Optional[str] = Field(None, description="API endpoint for the workflow")
    attributes: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional workflow attributes"
    )
    description: Optional[str] = Field(
        None, description="Description of what the workflow does"
    )
    input_parameters: Optional[Dict[str, Any]] = Field(
        None, description="JSON schema for workflow input parameters"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Agent(BaseModel):
    """Agent model for storing AI agents configuration"""

    name: str = Field(..., description="Unique name of the agent")
    system_prompt: str = Field(
        ..., description="System prompt/instructions for the agent"
    )
    workflow_names: List[str] = Field(
        default_factory=list, description="List of workflow names this agent can use"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    llm_config: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="LLM configuration for the agent"
    )


# API Request/Response Models


class CreateAgentRequest(BaseModel):
    name: str
    system_prompt: str
    workflow_names: List[str] = []
    llm_config: Optional[Dict[str, Any]] = {}


class UpdateAgentRequest(BaseModel):
    system_prompt: Optional[str] = None
    workflow_names: Optional[List[str]] = None
    llm_config: Optional[Dict[str, Any]] = None


class CreateWorkflowRequest(BaseModel):
    name: str
    code: str
    status: str = "inactive"
    endpoint: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = {}
    description: Optional[str] = None
    input_parameters: Optional[Dict[str, Any]] = None


class UpdateWorkflowRequest(BaseModel):
    code: Optional[str] = None
    status: Optional[str] = None
    endpoint: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    input_parameters: Optional[Dict[str, Any]] = None


class CreateChatRequest(BaseModel):
    name: str
    agent_name: Optional[str] = None


class ChatMessageRequest(BaseModel):
    chat_id: str
    agent_name: str
    message: str


class ChatMessageResponse(BaseModel):
    message: str
    chat_id: str


class ExecuteWorkflowRequest(BaseModel):
    workflow_name: str
    input_data: Dict[str, Any]
