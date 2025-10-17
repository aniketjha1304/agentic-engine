import logging
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import ValidationError
from app.api_models.view_workflow import ViewWorkflowRequest, ViewWorkflowResponse
from app.utils.api_key_required import api_key_required
from app.utils.get_existing_workflow_code import get_existing_workflow_code
from app.utils.get_workflow_diagram import get_workflow_diagram
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/view-workflow",
    dependencies=[Depends(api_key_required)],
    response_model=ViewWorkflowResponse,
    summary="Get Workflow Diagram",
    description="Endpoint to get the workflow diagram (langgraph code) for a given workflow title.",
)
async def view_workflow(
    workflowTitle: str = Query(..., description="Title of the workflow to view")
) -> ViewWorkflowResponse:
    """
    Endpoint to get the workflow diagram for a given workflow title.

    Parameters
    ----------
    workflowTitle : str
        Title of the workflow to view.

    Returns
    -------
    ViewWorkflowResponse
        Response containing the workflow diagram.
    """
    try:
        logger.info(f"Received request to view workflow: {workflowTitle}")

        # Validate the request using the schema
        request_model = ViewWorkflowRequest(workflowTitle=workflowTitle)

        # Retrieve the script content
        script_content = await get_existing_workflow_code(
            title=request_model.workflowTitle
        )

        if not script_content:
            logger.error("Script not found.")
            raise HTTPException(status_code=404, detail="Script not found.")

        # Generate the workflow diagram
        diagram_json = get_workflow_diagram(script_content)

        # Prepare and return the response
        response = ViewWorkflowResponse(
            workflowTitle=request_model.workflowTitle,
            diagram=diagram_json,
        )
        logger.info(f"Workflow diagram generated for: {workflowTitle}")
        return response

    except Exception as e:
        logger.exception(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error; {str(e)}")
