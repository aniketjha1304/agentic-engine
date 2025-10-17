"""
WorkflowManagement class for workflows,
with internal workflow_state for proposal or review.

"""

import uuid
import json
from datetime import datetime

from app.utils.azure_repo_connector import AzureRepoConnector
from app.utils.run_code import run_code
from app.database.ai_persona_hub_queries import (
    get_workflow_by_title,
    save_workflow,
    update_workflow,
)
from app.utils.get_workflow_diagram import get_workflow_diagram
from app.config.env import (
    DEVOPS_ORGANIZATION_NAME,
    PROJECT_NAME,
    WORKFLOWS_REPO_NAME,
    AZURE_PAT_TOKEN,
)
from app.config.default import (
    DEFAULT_WORKFLOW_STATUS,
    DEFAULT_WORKFLOW_BRANCH_NAME,
    WORKFLOW_TYPE_HTTP_TRIGGER,
    DEFAULT_WORKFLOW_STATUS,
)


class WorkflowManagement:
    def __init__(self, user_id, organization_id):
        self.repo_connector = AzureRepoConnector(
            organization=DEVOPS_ORGANIZATION_NAME,
            project=PROJECT_NAME,
            repository=WORKFLOWS_REPO_NAME,
            pat_token=AZURE_PAT_TOKEN,
        )
        self.workflow_state = {}
        self.user_id = user_id
        self.organization_id = organization_id

    async def create_workflow(
        self,
        title: str,
        description: str,
        code: str,
        workflow_input_signature: dict = None,
    ) -> dict:
        """
        Create a new HTTP-triggered workflow.
        - Status is 'Inactive' at creation.
        - Code is validated.
        - Metadata in DB, code in repo.
        Updates self.workflow_state with new state on success.
        """
        if not (title and description and code):
            return {"error": "title, description, code are required"}

        try:
            code_check = await run_code(code)
        except Exception as e:
            return {"error": f"Workflow/skill code failed validation: {str(e)}"}

        file_name = title.strip().replace(" ", "_").lower()
        file_path = f"/workflows/{file_name}/{file_name}.py"
        workflow_id = str(uuid.uuid4())
        metadata = {
            "id": workflow_id,
            "title": title,
            "status": DEFAULT_WORKFLOW_STATUS,
            "type": WORKFLOW_TYPE_HTTP_TRIGGER,
            "description": description,
            "source_code_location": file_path,
            "organization_id": self.organization_id,
            "accountable_user_id": self.user_id,
            "workflow_input_state": json.dumps(workflow_input_signature or {}),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        db_result = await save_workflow(metadata)
        if not db_result.get("success"):
            return {"error": f"Could not save workflow: {db_result.get('message')}"}

        try:
            self.repo_connector.push_changes(
                changes={file_path: code},
                branch=DEFAULT_WORKFLOW_BRANCH_NAME,
                commit_message=f"Add HTTP workflow '{title}' (Inactive) via Ada agent",
            )
        except Exception as e:
            return {"error": f"Failed to commit code to repo: {e}"}

        self.workflow_state = {
            "id": workflow_id,
            "title": title,
            "description": description,
            "code": code,
            "metadata": workflow_input_signature or {},
            "status": DEFAULT_WORKFLOW_STATUS,
            "proposed": False,
            "diagram": get_workflow_diagram(code),
        }

        return {
            "workflow_id": workflow_id,
            "file_path": file_path,
            "status": DEFAULT_WORKFLOW_STATUS,
            "result": "Workflow metadata and code saved successfully (Inactive/validation passed).",
        }

    async def update_workflow(
        self,
        workflow_title: str,
        new_description: str = None,
        new_code: str = None,
        new_workflow_input_signature: dict = None,
    ) -> dict:
        """
        Update description, code, input signature of existing HTTP-triggered workflow.
        Sets status to Inactive and updates workflow_state.
        """
        existing = await get_workflow_by_title(workflow_title)
        if not existing:
            return {"error": f"Workflow with title '{workflow_title}' not found."}

        updated_fields = {}
        if new_description:
            updated_fields["description"] = new_description
        if new_workflow_input_signature is not None:
            updated_fields["workflow_input_state"] = json.dumps(
                new_workflow_input_signature
            )
        file_path = existing["source_code_location"]

        if new_code:
            try:
                code_check = await run_code(new_code)
            except Exception as e:
                return {"error": f"Workflow/skill code failed validation: {str(e)}"}
            try:
                self.repo_connector.push_changes(
                    changes={file_path: new_code},
                    branch=DEFAULT_WORKFLOW_BRANCH_NAME,
                    commit_message=f"Update HTTP workflow '{workflow_title}' (set Inactive) via Ada agent",
                )
            except Exception as e:
                return {"error": f"Failed to update code in repo: {e}"}

        updated_fields["status"] = DEFAULT_WORKFLOW_STATUS
        updated_fields["updated_at"] = datetime.utcnow()

        db_result = await update_workflow(
            existing["id"], {**existing, **updated_fields}
        )
        if not db_result.get("success"):
            return {
                "error": f"Failed to update workflow metadata: {db_result.get('message')}"
            }

        self.workflow_state = {
            "id": existing["id"],
            "title": workflow_title,
            "description": new_description or existing["description"],
            "code": new_code or "",  # If code wasn't updated, may fetch or leave blank
            "metadata": new_workflow_input_signature or {},
            "status": DEFAULT_WORKFLOW_STATUS,
            "proposed": False,
            "diagram": get_workflow_diagram(new_code),
        }

        return {
            "workflow_id": existing["id"],
            "status": DEFAULT_WORKFLOW_STATUS,
            "result": "Workflow updated and set to Inactive (validation passed).",
        }

    async def get_workflow(self, workflow_title: str) -> dict:
        wf = await get_workflow_by_title(workflow_title)
        if not wf:
            return {"error": f"No workflow found with title '{workflow_title}'"}
        return wf

    async def populate_state(
        self,
        title: str,
        description: str,
        code: str,
        workflow_input_signature: dict = None,
        status: str = DEFAULT_WORKFLOW_STATUS,
    ):
        """
        Updates self.workflow_state with provided data, does NOT persist to DB or repo.
        Use for proposals, drafts, or dry-run previews for UI/human review.
        """
        self.workflow_state = {
            "title": title,
            "description": description,
            "code": code,
            "metadata": workflow_input_signature or {},
            "status": status,
            "proposed": True,
            "diagram": get_workflow_diagram(code),
        }
        return "Populated the workflow state."
