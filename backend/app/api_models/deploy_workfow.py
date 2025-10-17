from pydantic import BaseModel, Field
from typing import Optional


class DeployWorkflowRequest(BaseModel):
    # workflowId: Optional[str] = Field(None, description="ID of the workflow to deploy.")
    workflowTitle: Optional[str] = Field(
        None, description="Title of the workflow to deploy."
    )


from pydantic import BaseModel, Field


class DeployWorkflowResponse(BaseModel):
    message: str = Field(..., description="Message indicating the deployment status.")
    workflowTitle: str = Field(..., description="Title of the deployed workflow.")
    workflowEndpoint: str = Field(
        ..., description="The endpoint of the deployed workflow."
    )
