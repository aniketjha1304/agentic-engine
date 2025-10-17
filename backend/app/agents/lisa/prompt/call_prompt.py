"""
Call prompt for lisa
"""

from app.agents.lisa.tools.get_workflows import get_workflows
from app.utils.azure_repo_connector import AzureRepoConnector
from app.config.env import (
    DEVOPS_ORGANIZATION_NAME,
    PROJECT_NAME,
    WORKFLOWS_REPO_NAME,
    AZURE_PAT_TOKEN,
)
from app.config.default import DEFAULT_WORKFLOW_BRANCH_NAME, default_llm_dict
from datetime import datetime
import pytz


async def get_call_lisa_prompt():

    # Initialize the language model interface

    workflows_information = await get_workflows()
    print(type(workflows_information))
    print(workflows_information)
    azure_repo_connector = AzureRepoConnector(
        organization=DEVOPS_ORGANIZATION_NAME,
        project=PROJECT_NAME,
        repository=WORKFLOWS_REPO_NAME,
        pat_token=AZURE_PAT_TOKEN,
    )
    # Step 3: Determine branch based on the workflow status
    file_content = azure_repo_connector.get_file(
        file_path=f"/prompts/lisa_call_prompt.md",
        branch=DEFAULT_WORKFLOW_BRANCH_NAME,
    )
    # Define the system prompt to guide the assistant's behavior
    cet_tz = pytz.timezone("Europe/Berlin")  # CET/CEST time zone
    current_date_time = datetime.now(cet_tz).isoformat()
    call_lisa_prompt = f""" 
    {file_content}
    ### Skills Configured with request processor.
    {workflows_information}
    ### Current date and time
    {current_date_time}
    """
    return call_lisa_prompt
