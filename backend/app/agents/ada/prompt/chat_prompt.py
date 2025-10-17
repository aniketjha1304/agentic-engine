"""
Chat prompt for Ada
"""

from app.utils.azure_repo_connector import AzureRepoConnector
from app.config.env import (
    DEVOPS_ORGANIZATION_NAME,
    PROJECT_NAME,
    WORKFLOWS_REPO_NAME,
    AZURE_PAT_TOKEN,
)
from app.config.default import DEFAULT_WORKFLOW_BRANCH_NAME

# from app.agents.lisa.tools.get_search import get_core_summary_memory

INTERNAL_REPOS = [
    {
        "repo_name": "recall-space-utils",
        "description": "Shared utilities and helper functions for workflow development.",
    },
    {
        "repo_name": "recall-space-agents",
        "description": "Reusable AI agent modules and template logic.",
    },
]


async def get_repo_structure(repo_name: str, branch: str = "main") -> str:
    """
    Efficiently gets all .py/.md files and directory structure by fetching
    the entire tree at once.
    """
    connector = AzureRepoConnector(
        organization=DEVOPS_ORGANIZATION_NAME,
        project=PROJECT_NAME,
        repository=repo_name,
        pat_token=AZURE_PAT_TOKEN,
    )
    try:
        all_items = connector.get_full_tree(branch=branch)
        lines = []
        for item in all_items:
            path = item["path"]
            obj_type = item.get("gitObjectType")
            # Indent based on depth (count slashes minus root)
            level = path.count("/") - 1 if path.startswith("/") else path.count("/")
            indent = "  " * level
            if obj_type == "tree":
                lines.append(f"{indent}[DIR] {path}")
            elif obj_type == "blob" and (path.endswith(".py") or path.endswith(".md")):
                lines.append(f"{indent}[FILE] {path}")
        return "\n".join(lines) if lines else "No .py/.md files or folders found."
    except Exception as e:
        return f"Could not fetch structure for repo {repo_name}: {e}"


async def get_chat_ada_prompt():
    """
    Build Ada's full system prompt, including:
    - Prompt instructions from repo (prompts/ada_chat_prompt.md)
    - The names and folder structure (dirs and .py/.md files) of core internal packages
    - Summary of Ada's core memory
    """

    # core_summary_memory = await get_core_summary_memory()

    workflows_connector = AzureRepoConnector(
        organization=DEVOPS_ORGANIZATION_NAME,
        project=PROJECT_NAME,
        repository=WORKFLOWS_REPO_NAME,
        pat_token=AZURE_PAT_TOKEN,
    )

    ada_prompt_content = workflows_connector.get_file(
        file_path="/prompts/ada_chat_prompt.md",
        branch=DEFAULT_WORKFLOW_BRANCH_NAME,
    )
    # ada_prompt_content = "You are ada."
    repo_structures: str = ""
    for repo in INTERNAL_REPOS:
        repo_name = repo["repo_name"]
        # description = repo.get("description", "")
        structure_str = await get_repo_structure(
            repo_name=repo_name,
            branch=DEFAULT_WORKFLOW_BRANCH_NAME,
        )
        repo_structures += (
            f"\n\n## Repository Name: {repo_name}\n"
            f"## Package Name: {repo_name}\n"
            f"### Code structure (.py/.md only):\n{structure_str}"
        )

    chat_ada_prompt = f"""{ada_prompt_content}

        # Internal Core Package Overview
        Below are the code packages you can use when building or proposing workflows/skills.
        Only .py and .md files and all folders are included.

        {repo_structures}
        """
    return chat_ada_prompt
