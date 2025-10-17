"""
AzureRepoConnector class
"""

import base64
import requests
from typing import Optional, List, Dict


class AzureRepoConnector:
    """
    A utility class for interacting with Azure Repos, enabling operations like
    listing items, retrieving file contents, pushing changes, deleting files,
    creating branches, and merging branches.
    Refer: https://learn.microsoft.com/en-us/rest/api/azure/devops/git/?view=azure-devops-rest-7.0
    Parameters
    ----------
    organization : str
        Azure DevOps organization name.
    project : str
        Azure DevOps project name.
    repository : str
        Repository name.
    pat_token : str
        Personal Access Token (PAT) for authentication.
    """

    def __init__(
        self, organization: str, project: str, repository: str, pat_token: str
    ):
        self.organization = organization
        self.project = project
        self.repository = repository
        self.pat_token = pat_token
        self.base_url = f"https://dev.azure.com/{organization}/{project}/_apis/git/repositories/{repository}"
        self.api_version = "7.0"
        self.auth = ("", pat_token)

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Helper function to make HTTP requests with authentication.

        Parameters
        ----------
        method : str
            HTTP method (GET, POST, etc.).
        url : str
            Full API endpoint URL.
        **kwargs : dict
            Additional arguments to pass to the request.

        Returns
        -------
        requests.Response
            Response object.
        """
        response = requests.request(method, url, auth=self.auth, **kwargs)
        response.raise_for_status()
        return response

    def _get_latest_commit(self, branch: str) -> Optional[str]:
        """
        Gets the latest commit ID for a branch.

        Parameters
        ----------
        branch : str
            Branch name.

        Returns
        -------
        Optional[str]
            Latest commit ID or None if branch doesn't exist.
        """
        url = (
            f"{self.base_url}/refs?filter=heads/{branch}&api-version={self.api_version}"
        )
        response = self._make_request("GET", url)
        refs = response.json().get("value", [])
        return refs[0]["objectId"] if refs else None

    def _check_file_exists(self, file_path: str, branch: str) -> bool:
        """
        Checks if a file exists in the repository.

        Parameters
        ----------
        file_path : str
            Path to the file.
        branch : str
            Branch name.

        Returns
        -------
        bool
            True if the file exists, False otherwise.
        """
        url = f"{self.base_url}/items"
        params = {
            "path": file_path,
            "versionDescriptor.version": branch,
            "versionDescriptor.versionType": "branch",
            "api-version": self.api_version,
        }
        try:
            self._make_request("GET", url, params=params)
            return True
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return False
            raise

    def list_items(self, path: str = "/", branch: str = "main") -> List[Dict]:
        """
        Lists files and folders at a given path in the repository.

        Parameters
        ----------
        path : str, optional
            Path in the repository (default is root `/`).
        branch : str, optional
            Branch name (default is `main`).

        Returns
        -------
        List[Dict]
            List of items (files/folders) at the specified path.
        """
        url = f"{self.base_url}/items"
        params = {
            "scopePath": path,
            "recursionLevel": "oneLevel",
            "versionDescriptor.version": branch,
            "versionDescriptor.versionType": "branch",
            "api-version": self.api_version,
        }
        response = self._make_request("GET", url, params=params)
        return response.json().get("value", [])

    def get_file(self, file_path: str, branch: str = "main") -> Optional[str]:
        """
        Retrieves the content of a file from the repository.

        Parameters
        ----------
        file_path : str
            Path to the file in the repository.
        branch : str, optional
            Branch name (default is `main`).

        Returns
        -------
        Optional[str]
            Content of the file as a string or None if not found.
        """
        url = f"{self.base_url}/items"
        params = {
            "path": file_path,
            "versionDescriptor.version": branch,
            "versionDescriptor.versionType": "branch",
            "api-version": self.api_version,
            "download": True,
        }
        try:
            response = self._make_request("GET", url, params=params)
            return response.content.decode("utf-8")
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                print(f"File not found: {file_path}")
                return None
            raise

    def push_changes(self, changes: Dict[str, str], branch: str, commit_message: str):
        """
        Pushes multiple changes to a branch in a single commit.

        Parameters
        ----------
        changes : Dict[str, str]
            Dictionary where keys are file paths and values are file contents.
        branch : str
            Branch name to push the changes.
        commit_message : str
            Commit message.
        """
        latest_commit = (
            self._get_latest_commit(branch)
            or "0000000000000000000000000000000000000000"
        )
        formatted_changes = [
            {
                "changeType": (
                    "add" if not self._check_file_exists(path, branch) else "edit"
                ),
                "item": {"path": path},
                "newContent": {
                    "content": base64.b64encode(content.encode("utf-8")).decode(
                        "utf-8"
                    ),
                    "contentType": "base64encoded",
                },
            }
            for path, content in changes.items()
        ]
        data = {
            "refUpdates": [
                {"name": f"refs/heads/{branch}", "oldObjectId": latest_commit}
            ],
            "commits": [{"comment": commit_message, "changes": formatted_changes}],
        }
        url = f"{self.base_url}/pushes?api-version={self.api_version}"
        response = self._make_request("POST", url, json=data)
        print(
            "Changes pushed successfully."
            if response.status_code == 201
            else "Failed to push changes."
        )

    def delete_files(self, file_paths: List[str], branch: str, commit_message: str):
        """
        Deletes multiple files in the repository, one at a time.

        Parameters
        ----------
        file_paths : List[str]
            List of file paths to delete.
        branch : str
            Branch name to delete the files from.
        commit_message : str
            Commit message for each deletion.
        """
        latest_commit = self._get_latest_commit(branch)
        if not latest_commit:
            print(
                f"Branch '{branch}' does not exist or couldn't fetch the latest commit."
            )
            return

        for file_path in file_paths:
            # Check if the file exists before attempting to delete
            print("File path name ", file_path)
            exists = self._check_file_exists(file_path, branch)
            if not exists:
                print(
                    f"File '{file_path}' does not exist on branch '{branch}'. Skipping."
                )
                continue

            # Prepare the data for the delete request
            formatted_changes = [{"changeType": "delete", "item": {"path": file_path}}]

            data = {
                "refUpdates": [
                    {"name": f"refs/heads/{branch}", "oldObjectId": latest_commit}
                ],
                "commits": [
                    {
                        "comment": f"{commit_message}: {file_path}",
                        "changes": formatted_changes,
                    }
                ],
            }
            url = f"{self.base_url}/pushes?api-version={self.api_version}"

            # Make the request to delete the file
            response = self._make_request("POST", url, json=data)
            print("File response ", response)
            if response.status_code == 201:
                print(f"File '{file_path}' deleted successfully.")
                # Update latest_commit for the next deletion
                latest_commit = self._get_latest_commit(branch)
            else:
                print(
                    f"Failed to delete file '{file_path}'. "
                    f"Status code: {response.status_code}. Response: {response.content}"
                )

    def delete_folder(self, folder_path: str, branch: str, commit_message: str):
        """
        Deletes a folder and all its files from the repository.

        Parameters
        ----------
        folder_path : str
            Path to the folder to delete.
        branch : str
            Branch name to delete the folder from.
        commit_message : str
            Commit message for the deletion.
        """
        # Step 1: List all items in the folder
        items = self.list_items(folder_path, branch)

        # Step 2: Filter to get only file paths
        file_paths = [item["path"] for item in items if item["gitObjectType"] == "blob"]

        if not file_paths:
            print(f"No files found in folder '{folder_path}' to delete.")
            return

        # Step 3: Delete the files
        self.delete_files(file_paths, branch, commit_message)
        print(f"Folder '{folder_path}' and its files have been deleted successfully.")

    def create_branch(self, branch_name: str, source_branch: str = "main"):
        """
        Creates a new branch from an existing branch.

        Parameters
        ----------
        branch_name : str
            Name of the new branch.
        source_branch : str, optional
            Name of the source branch (default is `main`).
        """
        latest_commit = self._get_latest_commit(source_branch)
        if not latest_commit:
            raise ValueError(f"Source branch '{source_branch}' does not exist.")
        url = f"{self.base_url}/refs?api-version={self.api_version}"
        data = {
            "name": f"refs/heads/{branch_name}",
            "oldObjectId": "0000000000000000000000000000000000000000",
            "newObjectId": latest_commit,
        }
        response = self._make_request("POST", url, json=data)
        print(f"Branch '{branch_name}' created successfully.")

    def merge_branches(
        self, source_branch: str, target_branch: str, commit_message: str
    ):
        """
        Merges a source branch into a target branch.

        Parameters
        ----------
        source_branch : str
            The branch to merge from.
        target_branch : str
            The branch to merge into.
        commit_message : str
            Commit message for the merge.
        """
        source_commit = self._get_latest_commit(source_branch)
        target_commit = self._get_latest_commit(target_branch)
        if not source_commit or not target_commit:
            raise ValueError("Source or target branch does not exist.")
        data = {
            "refUpdates": [
                {"name": f"refs/heads/{target_branch}", "oldObjectId": target_commit}
            ],
            "commits": [{"comment": commit_message, "changes": []}],
        }
        url = f"{self.base_url}/pushes?api-version={self.api_version}"
        response = self._make_request("POST", url, json=data)
        print(f"Branches merged into '{target_branch}' successfully.")

    def get_full_tree(self, branch: str = "main") -> list:
        """
        Returns all items (files/folders) recursively for the repo at the given branch.
        """
        url = f"{self.base_url}/items"
        params = {
            "scopePath": "/",
            "recursionLevel": "full",
            "versionDescriptor.version": branch,
            "versionDescriptor.versionType": "branch",
            "api-version": self.api_version,
        }
        response = self._make_request("GET", url, params=params)
        return response.json().get("value", [])
