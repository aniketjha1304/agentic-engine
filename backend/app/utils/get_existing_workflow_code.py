"""
Utility script to get the code of worklow.
"""

from app.utils.azure_repo_connector import AzureRepoConnector
from app.config.env import (
    DEVOPS_ORGANIZATION_NAME,
    PROJECT_NAME,
    WORKFLOWS_REPO_NAME,
    AZURE_PAT_TOKEN,
)
from app.config.default import DEFAULT_WORKFLOW_BRANCH_NAME
from app.database.ai_persona_hub_queries import get_workflow_by_title


async def get_existing_workflow_code(
    title: str, branch_name: str = DEFAULT_WORKFLOW_BRANCH_NAME
):
    workflow_data = await get_workflow_by_title(title=title)
    workflow_source_code_location = workflow_data["source_code_location"]
    azure_repo_connector = AzureRepoConnector(
        organization=DEVOPS_ORGANIZATION_NAME,
        project=PROJECT_NAME,
        repository=WORKFLOWS_REPO_NAME,
        pat_token=AZURE_PAT_TOKEN,
    )
    # Step 3: Determine branch based on the workflow status
    file_content = azure_repo_connector.get_file(
        file_path=workflow_source_code_location,
        branch=branch_name,
    )

    return file_content
