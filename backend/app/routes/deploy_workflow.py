import logging
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from app.utils.api_key_required import api_key_required
from app.utils.workflow_azure_function_builder import WorkflowAzureFunctionBuilder

from app.api_models.deploy_workfow import DeployWorkflowRequest, DeployWorkflowResponse
from app.database.ai_persona_hub_queries import (
    set_http_workflow_endpoint,
    update_workflow_status,
    get_workflow_by_title,
)
from app.config.default import WORKFLOW_ACTIVE_STATUS, WORKFLOW_TYPE_HTTP_TRIGGER
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/deploy-workflow",
    dependencies=[Depends(api_key_required)],
    response_model=DeployWorkflowResponse,
    summary="Deploy Workflow as Azure Function",
    description="""Endpoint to deploy a workflow as an Azure Function.
    This API render the workflow (langgraph based) and deploy it as azure function in
    workflows-azure-function reposiotory which triggeres a deployment CD pipeline and
    reflected as function. The process of actual deployment might take some time.
    """,
)
async def deploy_workflow(request: DeployWorkflowRequest):
    """
    Endpoint to deploy a workflow as an Azure Function.

    Expects a JSON payload with 'workflowId' or 'workflowTitle'.

    Returns
    -------
    DeployWorkflowResponse
        Response containing the deployment status.
    """
    try:
        # Extract the title or ID from the request
        workflow_title = request.workflowTitle
        workflow_data = await get_workflow_by_title(title=workflow_title)
        if not workflow_title:
            logger.error("Either 'workflowId' or 'workflowTitle' must be provided")
            raise HTTPException(
                status_code=400,
                detail="Either 'workflowId' or 'workflowTitle' must be provided",
            )

        logger.info(f"Received request to deploy workflow: {workflow_title}")

        # Initialize the WorkflowAzureFunctionBuilder
        builder = WorkflowAzureFunctionBuilder(title=workflow_title)

        # Build and deploy the workflow
        workflow_endpoint = await builder.build_and_deploy()

        # Prepare and return the response
        response = DeployWorkflowResponse(
            message=f"Workflow '{builder.title}' deployed successfully.",
            workflowTitle=builder.title,
            workflowEndpoint=workflow_endpoint,
        )
        update_status_response = await update_workflow_status(
            workflow_title=workflow_title, workflow_status=WORKFLOW_ACTIVE_STATUS
        )
        if not update_status_response["success"]:
            logger.error(
                f"Error while updating workflow status to Active: {str(update_status_response['message'])}"
            )
            raise Exception(
                f"Error while updating workflow status to Active: {str(update_status_response['message'])}"
            )
        if workflow_data["type"] == WORKFLOW_TYPE_HTTP_TRIGGER:
            set_endpoint_response = await set_http_workflow_endpoint(
                workflow_id=workflow_data["id"], workflow_endpoint=workflow_endpoint
            )
            if not set_endpoint_response["success"]:
                logger.error(
                    f"Error while setting workflow endpoint: {set_endpoint_response['message']}"
                )
                raise Exception(
                    f"Error while setting workflow endpoint: {set_endpoint_response['message']}"
                )
        logger.info(f"Workflow '{builder.title}' deployed successfully.")
        return response

    except Exception as e:
        logger.exception(f"Unexpected error occurred {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
