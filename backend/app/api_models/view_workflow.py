"""
Models for request and response of the view workflow endpoint.
"""

from pydantic import BaseModel, Field
from typing import Any, Dict


class ViewWorkflowRequest(BaseModel):
    workflowTitle: str = Field(..., description="Title of the workflow to view.")


class ViewWorkflowResponse(BaseModel):
    workflowTitle: str = Field(
        ..., description="Title of the workflow that was viewed."
    )
    diagram: Dict[str, Any] = Field(
        ..., description="The diagram of the workflow in JSON format."
    )
