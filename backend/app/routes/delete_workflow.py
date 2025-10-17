import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from app.utils.api_key_required import api_key_required
from app.utils.logger import get_logger
from app.database.ai_persona_hub_queries import (
    delete_workflow_by_title,
    get_workflow_by_title,
    delete_http_trigger_workflow,
    delete_scheduled_workflow,
)
from app.utils.delete_workflow_code import (
    delete_workflow_source_code,
    delete_workflow_azure_function_code,
)

# Assumed utility functions
from app.api_models.delete_workflow import DeleteWorkflowResponse
from app.config.default import WORKFLOW_TYPE_HTTP_TRIGGER, WORKFLOW_TYPE_SCHEDULED
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.delete(
    "/delete-workflow/{workflowTitle}",
    dependencies=[Depends(api_key_required)],
    response_model=DeleteWorkflowResponse,
    summary="Delete Workflow",
    description="Endpoint to delete a workflow by its title, including metadata and source code/deployment code.",
)
async def delete_workflow(workflowTitle: str):
    try:
        logger.info(f"Received request to delete workflow: {workflowTitle}")

        worfklow_data = await get_workflow_by_title(title=workflowTitle)
        logger.info(f"Workflow data for deleting: {worfklow_data}")
        # Delete the workflow's source code
        code_deleted_source = delete_workflow_source_code(worfklow_data)
        if not code_deleted_source:
            logger.error(f"Failed to delete source code for workflow: {workflowTitle}")
            # raise HTTPException(
            #     status_code=500, detail="Failed to delete workflow source code"
            # )

        code_deleted_deployment = delete_workflow_azure_function_code(worfklow_data)

        if not code_deleted_deployment:
            logger.error(
                f"Failed to delete azure function code for workflow: {workflowTitle}"
            )
            # raise HTTPException(
            #     status_code=500, detail="Failed to delete workflow azure function code"
            # )
        # Delete workflow metadata from the database

        if worfklow_data["type"] == WORKFLOW_TYPE_HTTP_TRIGGER:
            workflow_type_delete = await delete_http_trigger_workflow(
                workflow_id=worfklow_data["id"]
            )
        else:
            workflow_type_delete = await delete_scheduled_workflow(
                workflow_id=worfklow_data["id"]
            )
        logger.info(f"Delete workflow type result: {workflow_type_delete}")
        workflow_delete = await delete_workflow_by_title(workflowTitle)
        logger.info(f"Deletw workflow result: {workflow_delete}")
        if not workflow_delete["success"]:
            logger.error(f"Workflow not found in database: {workflowTitle}")

        logger.info(f"Successfully deleted workflow: {workflowTitle}")
        return DeleteWorkflowResponse(
            message=f"Workflow '{workflowTitle}' deleted successfully", success=True
        )
    except Exception as e:
        logger.error(f"Unexpected error occurred during workflow deletion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
