"""
Utility script to get the code of worklow.
"""

from app.utils.azure_repo_connector import AzureRepoConnector
from app.config.env import (
    DEVOPS_ORGANIZATION_NAME,
    PROJECT_NAME,
    WORKFLOWS_REPO_NAME,
    WORKFLOW_FUNCTIONS_REPO_NAME,
    AZURE_PAT_TOKEN,
)
from app.config.default import (
    DEFAULT_WORKFLOW_BRANCH_NAME,
    WORKFLOW_TYPE_HTTP_TRIGGER,
    DEFAULT_WORKFLOW_STATUS,
    DEFAULT_FUNCTION_BRANCH,
)
from app.database.ai_persona_hub_queries import get_workflow_by_title
from app.utils.generate_folder_name import generate_folder_name
from app.utils.logger import get_logger

logger = get_logger(__name__)
# TODO: Fix the worklfow code deletion.


def delete_workflow_source_code(
    workflow_data: dict, branch_name: str = DEFAULT_WORKFLOW_BRANCH_NAME
):
    response = True
    file_name = generate_folder_name(workflow_data["title"])
    workflow_file = workflow_data["source_code_location"]

    delete_file_name = [
        workflow_file,  # The source file
        f"workflows/{file_name}/__init__.py",
        # f"workflows/{file_name}/",  # Folder
    ]
    azure_repo_connector = AzureRepoConnector(
        organization=DEVOPS_ORGANIZATION_NAME,
        project=PROJECT_NAME,
        repository=WORKFLOWS_REPO_NAME,
        pat_token=AZURE_PAT_TOKEN,
    )

    # Step 3: Delete the folder and its files
    try:
        delete_file_response = azure_repo_connector.delete_files(
            file_paths=delete_file_name,
            branch=branch_name,
            commit_message=f"Delete workflow {file_name}",
        )
    except Exception as e:
        logger.error(f"Error while deleting workflow source code: {str(e)}")
        response = False
    return response


def delete_workflow_azure_function_code(
    workflow_data: dict, branch_name: str = DEFAULT_FUNCTION_BRANCH
) -> bool:
    """
    Deletes Azure Function code associated with the given workflow.

    Parameters
    ----------
    workflow_data : dict
        Workflow details including title and type.
    branch_name : str, optional
        The branch name to delete files from (default is DEFAULT_WORKFLOW_BRANCH_NAME).

    Returns
    -------
    bool
        True if deletion was successful, False otherwise.
    """
    response = True
    file_name = generate_folder_name(workflow_data["title"])

    # Determine the base path based on workflow type
    base_path = (
        "/workflows/http_trigger"
        if workflow_data["type"] == WORKFLOW_TYPE_HTTP_TRIGGER
        else "/workflows/scheduled"
    )

    # Files and folder paths to delete
    delete_file_names = [
        f"{base_path}/{file_name}/function_app.py",
        f"{base_path}/{file_name}/{file_name}.py",
        f"{base_path}/{file_name}/__init__.py",
        # f"{base_path}/{file_name}/",  # Folder
    ]

    # Initialize Azure Repo Connector
    azure_repo_connector = AzureRepoConnector(
        organization=DEVOPS_ORGANIZATION_NAME,
        project=PROJECT_NAME,
        repository=WORKFLOW_FUNCTIONS_REPO_NAME,
        pat_token=AZURE_PAT_TOKEN,
    )

    # Attempt to delete files
    try:
        azure_repo_connector.delete_files(
            file_paths=delete_file_names,
            branch=branch_name,
            commit_message=f"Delete workflow {file_name}",
        )
    except Exception as e:
        logger.error(f"Error while deleting workflow Azure Function code: {str(e)}")
        response = False

    return response
