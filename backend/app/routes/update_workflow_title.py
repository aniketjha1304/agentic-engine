import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.utils.api_key_required import api_key_required
from app.utils.get_existing_workflow_code import get_existing_workflow_code
from app.utils.generate_folder_name import generate_folder_name
from app.database.ai_persona_hub_queries import (
    get_workflow_by_title,
    update_workflow_title_and_source_code_location,
)

# from app.utils.update_workflow_code import update_workflow_code
from app.utils.delete_workflow_code import (
    delete_workflow_source_code,
    delete_workflow_azure_function_code,
)
from app.utils.azure_repo_connector import AzureRepoConnector
from app.utils.generate_folder_name import generate_folder_name
from app.config.env import (
    DEVOPS_ORGANIZATION_NAME,
    PROJECT_NAME,
    WORKFLOWS_REPO_NAME,
    AZURE_PAT_TOKEN,
)
from app.config.default import DEFAULT_WORKFLOW_BRANCH_NAME, DEFAULT_WORKFLOW_STATUS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


class UpdateWorkflowTitleRequest(BaseModel):
    currentTitle: str
    newTitle: str


class UpdateWorkflowTitleResponse(BaseModel):
    message: str
    updatedTitle: str


@router.post(
    "/update-workflow-title",
    dependencies=[Depends(api_key_required)],
    response_model=UpdateWorkflowTitleResponse,
    summary="Update Workflow Title",
    description="Endpoint to update the title of an existing workflow and apply necessary changes.",
)
async def update_workflow_title(
    request: UpdateWorkflowTitleRequest,
) -> UpdateWorkflowTitleResponse:
    """
    Endpoint to update the title of an existing workflow.

    Parameters
    ----------
    request : UpdateWorkflowTitleRequest
        Contains the current and new workflow titles.

    Returns
    -------
    UpdateWorkflowTitleResponse
        Response indicating success or failure of the update.
    """
    try:
        current_workflow_title = request.currentTitle
        new_workflow_title = request.newTitle

        logger.info(
            f"Received request to update workflow title from '{current_workflow_title}' to '{new_workflow_title}'"
        )
        workflow_data = await get_workflow_by_title(current_workflow_title)
        # Check if the existing workflow exists
        existing_script = await get_existing_workflow_code(title=current_workflow_title)
        if (not existing_script) or (not workflow_data):
            logger.error("Workflow not found.")
            raise HTTPException(status_code=404, detail="Workflow not found.")

        # Let's delete the workflow source code and dpeloyment code
        code_deleted_source = delete_workflow_source_code(workflow_data)

        code_deleted_deployment = delete_workflow_azure_function_code(workflow_data)

        # Let's create a new workflow code and deployment
        new_file_name = generate_folder_name(title=new_workflow_title)
        new_file_path = f"/workflows/{new_file_name}/{new_file_name}.py"
        # Commit the workflow code to Azure DevOps
        azure_repo_connector = AzureRepoConnector(
            organization=DEVOPS_ORGANIZATION_NAME,
            project=PROJECT_NAME,
            repository=WORKFLOWS_REPO_NAME,
            pat_token=AZURE_PAT_TOKEN,
        )
        changes = {new_file_path: existing_script}
        commit_message = f"Commit by Lisa for saving workflow '{new_workflow_title}'"

        azure_repo_connector.push_changes(
            changes=changes,
            branch=DEFAULT_WORKFLOW_BRANCH_NAME,
            commit_message=commit_message,
        )
        new_workflow_data = {
            "title": new_workflow_title,
            "status": DEFAULT_WORKFLOW_STATUS,
            "source_code_location": new_file_path,
        }
        update_workflow_data = await update_workflow_title_and_source_code_location(
            workflow_id=workflow_data["id"], workflow_data=new_workflow_data
        )
        logger.info(
            f"Response from database operation to delete title: {update_workflow_data}"
        )
        logger.info(f"Successfully updated workflow title to: {new_workflow_title}")
        return UpdateWorkflowTitleResponse(
            message="Workflow title updated successfully.",
            updatedTitle=new_workflow_title,
        )

    except Exception as e:
        logger.exception(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error; {str(e)}")
