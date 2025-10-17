from pydantic import BaseModel, Field


class DeleteWorkflowResponse(BaseModel):
    message: str = Field(
        ..., description="Message indicating the result of the deletion."
    )
    success: bool = Field(
        ..., description="Indicates whether the deletion was successful."
    )
