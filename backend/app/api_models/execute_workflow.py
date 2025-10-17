from pydantic import BaseModel, Field
from typing import Dict, Any


class ExecuteWorkflowRequest(BaseModel):
    workflowTitle: str = Field(..., description="The title of the workflow to execute.")
    workflowInputState: Dict[str, Any] = Field(
        ..., description="Input state parameters for the workflow execution."
    )


class ExecuteWorkflowResponse(BaseModel):
    message: Any = Field(
        ..., description="Message indicating the result of the workflow execution."
    )
    success: bool = Field(
        ..., description="Indicates whether the workflow execution was successful."
    )
