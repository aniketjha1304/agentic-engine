# import os
# from pydantic import BaseModel, Field
# from app.utils.postgres_connector import PostgresConnector
# from app.utils.azure_repo_connector import AzureRepoConnector
# from app.utils.generate_folder_name import generate_folder_name
# from langchain_core.messages import ToolMessage
# from langchain_core.runnables.config import RunnableConfig
# from app.utils.extract_tool_call import extract_tool_call
# from app.config.default import (
#     DEVOPS_ORGANIZATION_NAME,
#     PROJECT_NAME,
#     WORKFLOWS_REPO_NAME,
#     DEFAULT_WORKFLOW_BRANCH_NAME,
# )


# class DeleteWorkflow(BaseModel):
#     """Tool to delete a workflow based on the given title."""

#     title: str = Field(..., description="The title of the workflow to be deleted.")


# def delete_workflow(state, config: RunnableConfig):
#     """
#     Delete a workflow from the database and Azure DevOps repository.

#     Args:
#         state (dict): The current state of the application.
#         config (RunnableConfig): Configuration for the current execution.

#     Returns:
#         dict: Response containing success or error message.
#     """
#     # Extract arguments and tool_call_id from the last AI message
#     tool_call_data = extract_tool_call(state["messages"], tool_name="DeleteWorkflow")
#     tool_call_id = tool_call_data["tool_call_id"]
#     args = tool_call_data["tool_call_args"]

#     title = args.get("title")
#     response_message = ""

#     try:
#         # Create a Postgres connector to interact with the database
#         postgres_connector = PostgresConnector(database_url=os.getenv("DATABASE_URL"))

#         # Step 1: Check if the workflow exists
#         query = "SELECT id FROM workflows WHERE title = %s"
#         result = postgres_connector.execute_query(query, (title,))

#         if not result:
#             response_message = f"No workflow found with the title '{title}'."
#         else:
#             workflow_id = result[0]["id"]

#             # Step 2: Delete the workflow from the database
#             delete_query = "DELETE FROM workflows WHERE id = %s"
#             postgres_connector.execute_query(delete_query, (workflow_id,))

#             # Step 3: Delete the corresponding folder and file from Azure DevOps
#             file_name = generate_folder_name(title=title)

#             azure_repo_connector = AzureRepoConnector(
#                 organization=DEVOPS_ORGANIZATION_NAME,
#                 project=PROJECT_NAME,
#                 repository=WORKFLOWS_REPO_NAME,
#                 pat_token=os.getenv("AZURE_PAT_TOKEN"),
#             )
#             # TODO: Add logic to delete from all branches
#             azure_repo_connector.delete_files(
#                 file_paths=[f"/workflows/{file_name}/{file_name}.py"],
#                 branch=DEFAULT_WORKFLOW_BRANCH_NAME,
#                 commit_message=f"Delete workflow {title}",
#             )

#             response_message = f"Workflow '{title}' and its associated files have been deleted successfully."

#         # Return the response as a ToolMessage
#         return {
#             "messages": [
#                 ToolMessage(content=response_message, tool_call_id=tool_call_id)
#             ],
#         }

#     except Exception as e:
#         response_message = f"Error deleting workflow: {str(e)}"
#         return {
#             "messages": [
#                 ToolMessage(content=response_message, tool_call_id=tool_call_id)
#             ],
#         }
