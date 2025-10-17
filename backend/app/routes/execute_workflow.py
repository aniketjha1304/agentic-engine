import json
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from app.utils.api_key_required import api_key_required
from app.utils.execute_http_trigger_workflow import execute_http_trigger_workflow

from app.api_models.execute_workflow import (
    ExecuteWorkflowRequest,
    ExecuteWorkflowResponse,
)

import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter()


@router.post(
    "/execute-workflow",
    dependencies=[Depends(api_key_required)],
    response_model=ExecuteWorkflowResponse,
    summary="Execute a Htttp Triggered workflow with given input state parameters",
    description="Endpoint to execute a workflow with specified input parameters. The api invokes the function app of worklfow with given params.",
)
async def execute_workflow(request: ExecuteWorkflowRequest):
    try:
        workflow_title = request.workflowTitle
        input_parameters = request.workflowInputState

        logger.info(f"Received request to execute workflow: {workflow_title}")

        # Execute the workflow
        data = await execute_http_trigger_workflow(
            workflow_title=workflow_title, input_parameters=input_parameters
        )

        logger.info("Data from execution of workflow")
        logger.info(data)

        response_message = data["message"]
        if data["success"]:
            return ExecuteWorkflowResponse(message=response_message, success=True)
        else:
            raise HTTPException(status_code=500, detail=response_message)

    except Exception as e:
        logger.exception("Unexpected error occurred")
        raise HTTPException(status_code=500, detail="Internal server error")
