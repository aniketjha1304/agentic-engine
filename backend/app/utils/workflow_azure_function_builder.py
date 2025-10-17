"""
WorkflowAzureFunctionBuilder Class
"""

import os
from typing import Optional, Dict, Any

from app.utils.azure_repo_connector import AzureRepoConnector
from app.utils.get_existing_workflow_code import get_existing_workflow_code
from app.database.ai_persona_hub_queries import get_workflow_by_title
from app.utils.generate_folder_name import generate_folder_name
from app.database.ai_persona_hub_queries import (
    get_http_trigger_workflow_data,
    get_scheduled_workflow_data,
)
from app.utils.get_workflow_trigger_data import get_workflow_trigger_data
from app.config.env import (
    DEVOPS_ORGANIZATION_NAME,
    PROJECT_NAME,
    WORKFLOW_FUNCTIONS_REPO_NAME,
    AZURE_PAT_TOKEN,
    WORKFLOW_FUNCTION_APP_URL,
)
from app.config.default import (
    DEFAULT_FUNCTION_BRANCH,
    WORKFLOW_TYPE_HTTP_TRIGGER,
    WORKFLOW_TYPE_SCHEDULED,
)


class WorkflowAzureFunctionBuilder:
    """
    A builder class for constructing and deploying Azure Functions for workflows.
    """

    def __init__(self, title: Optional[str] = None):
        """
        Initialize the WorkflowAzureFunctionBuilder with either workflow_id or title.

            title (Optional[str]): The title of the workflow.
        """
        if not title:
            raise ValueError("'title' must be provided.")

        self.title = title
        self.workflow_data: Dict[str, Any] = {}
        self.workflow_code: str = ""
        self.function_code: str = ""
        self.function_definition_filename = "function_app.py"
        self.workflow_code_filename: Optional[str] = None
        self.folder_name: Optional[str] = None
        self.workflow_type: str = WORKFLOW_TYPE_HTTP_TRIGGER
        self.route_url: str = ""

        # Initialize the functions repository connector
        self.functions_repo_connector = AzureRepoConnector(
            organization=DEVOPS_ORGANIZATION_NAME,
            project=PROJECT_NAME,
            repository=WORKFLOW_FUNCTIONS_REPO_NAME,
            pat_token=AZURE_PAT_TOKEN,
        )

    async def build_and_deploy(self) -> str:
        """
        Main method to build the Azure Function and deploy it.

        Returns:
            str: The route URL if HTTP trigger, else an empty string.
        """
        await self.fetch_workflow_data()
        await self.fetch_workflow_code()
        await self.generate_function_code()
        self.push_to_functions_repo()
        return self.route_url

    async def fetch_workflow_data(self) -> None:
        """
        Fetches the workflow data from the database.
        """

        self.workflow_data = await get_workflow_by_title(title=self.title)

        if not self.workflow_data:
            raise ValueError("Workflow not found in the database.")

        self.title = self.workflow_data["title"]
        self.folder_name = generate_folder_name(title=self.title)
        self.workflow_code_filename = f"{self.folder_name}.py"

    async def fetch_workflow_code(self) -> None:
        """
        Fetches the workflow code from the workflows repository.
        """
        self.workflow_code = await get_existing_workflow_code(self.title)
        if self.workflow_code is None:
            raise FileNotFoundError(f"Workflow code not found for '{self.title}'.")

    async def generate_function_code(self) -> None:
        """
        Generates the Azure Function code using the workflow code and metadata.
        """
        self.workflow_type = self.workflow_data.get("type", WORKFLOW_TYPE_HTTP_TRIGGER)
        # TODO: Modify this such that maybe the class function could become static
        # and used later.
        workflow_type_data = await get_workflow_trigger_data(
            workflow_id=self.workflow_data.get("id"), trigger_type=self.workflow_type
        )

        # Fetch the templates to convert the workflow into azure function.
        # TODO: Move the path name to defaults
        templates_dir = os.path.join(
            os.path.dirname(__file__), "azure_function_templates"
        )

        if self.workflow_type == WORKFLOW_TYPE_SCHEDULED:
            # Timer Trigger
            self.function_code = self.generate_timer_trigger_function(
                workflow_type_data, templates_dir
            )
        else:
            # HTTP Trigger
            self.function_code = self.generate_http_trigger_function(
                workflow_type_data, templates_dir
            )

    def push_to_functions_repo(self) -> None:
        """
        Pushes the generated function code and workflow code to the repository,
        along with necessary __init__.py files, in a single commit.
        """
        # Determine the base folder path based on trigger type
        base_folder = (
            "workflows/scheduled"
            if self.workflow_type == WORKFLOW_TYPE_SCHEDULED
            else "workflows/http_trigger"
        )

        # Prepare file paths
        folder_path = f"/{base_folder}/{self.folder_name}"
        function_definition_path = f"{folder_path}/{self.function_definition_filename}"
        workflow_code_path = f"{folder_path}/{self.workflow_code_filename}"

        # Get all changes to be committed
        changes = self._collect_changes(
            folder_path=folder_path,
            function_definition_path=function_definition_path,
            workflow_code_path=workflow_code_path,
        )

        # Push all changes together
        self.functions_repo_connector.push_changes(
            changes=changes,
            branch=DEFAULT_FUNCTION_BRANCH,
            commit_message=f"Add/update function and workflow code for '{self.title}'",
        )

        print(
            f"Successfully deployed function '{self.title}' to the functions repository."
        )

    def generate_http_trigger_function(
        self, workflow_type_data: Dict[str, Any], templates_dir: str
    ) -> str:
        """
        Generates the Azure Function code for an HTTP trigger.

        Args:
            metadata (Dict[str, Any]): The workflow metadata.
            templates_dir (str): The directory where templates are stored.

        Returns:
            str: The generated function code.
        """
        template = self._load_template(templates_dir, "http_trigger_template.txt")

        # Take the route argument from dictionary (http_trigger_workflow)
        # If exists else make it the folder name.
        route = (
            workflow_type_data.get("route") or self.folder_name
        )  # Default route is function name
        function_name = self.folder_name

        # Fill in the template
        function_code = template.format(
            workflow_function_name=function_name,
            route=route,
            folder_name=self.folder_name,
        )

        # Construct route URL
        # NOTE: Here we create the workflow endpoint.
        base_url = WORKFLOW_FUNCTION_APP_URL.rstrip("/")
        if not base_url:
            raise ValueError(
                "WORKFLOW_FUNCTION_APP_URL is not set in environment variables."
            )

        route = route.lstrip("/")
        self.route_url = f"{base_url}/{route}"
        return function_code

    def generate_timer_trigger_function(
        self, workflow_type_data: Dict[str, Any], templates_dir: str
    ) -> str:
        """
        Generates the Azure Function code for a Timer trigger.

        Args:
            metadata (Dict[str, Any]): The workflow metadata.
            templates_dir (str): The directory where templates are stored.

        Returns:
            str: The generated function code.
        """
        template = self._load_template(templates_dir, "timer_trigger_template.txt")

        cron_expression = workflow_type_data.get("cron_expression")
        if not cron_expression:
            raise ValueError("Schedule is required for TimerTrigger functions.")

        function_name = self.folder_name

        # Fill in the template
        function_code = template.format(
            workflow_function_name=function_name,
            cron_expression=cron_expression,
            folder_name=self.folder_name,
        )

        # Since it's not an HTTP trigger, set route_url to empty
        self.route_url = ""
        return function_code

    def _load_template(self, templates_dir: str, template_name: str) -> str:
        """
        Loads a template file from the templates directory.

        Args:
            templates_dir (str): The directory where templates are stored.
            template_name (str): The name of the template file.

        Returns:
            str: The content of the template file.
        """
        template_path = os.path.join(templates_dir, template_name)
        with open(template_path, "r") as template_file:
            return template_file.read()

    def _collect_changes(
        self,
        folder_path: str,
        function_definition_path: str,
        workflow_code_path: str,
    ) -> Dict[str, str]:
        """
        Collects all changes to be pushed to the repository.

        Args:
            folder_path (str): The base folder path for the function.
            function_definition_path (str): The path to the function definition file.
            workflow_code_path (str): The path to the workflow code file.

        Returns:
            Dict[str, str]: A dictionary mapping file paths to their content.
        """
        # Collect __init__.py file changes
        init_files_changes = self._get_init_files_changes(folder_path)

        # Prepare changes for function code and workflow code
        code_changes = {
            function_definition_path: self.function_code,
            workflow_code_path: self.workflow_code,
        }

        # Combine all changes
        changes = {**init_files_changes, **code_changes}
        return changes

    def _get_init_files_changes(self, folder_path: str) -> Dict[str, str]:
        """
        Generates a dictionary of __init__.py files for the given folder path.

        Args:
            folder_path (str): The folder path where __init__.py files need to be added.

        Returns:
            Dict[str, str]: A dictionary mapping file paths to empty content.
        """
        directories = folder_path.strip("/").split("/")
        cumulative_paths = []
        curr_path = ""
        for dir_name in directories:
            curr_path += f"/{dir_name}"
            cumulative_paths.append(curr_path)

        return {f"{dir_path}/__init__.py": "" for dir_path in cumulative_paths}
