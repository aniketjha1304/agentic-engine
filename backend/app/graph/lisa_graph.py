import os
from azure.identity import UsernamePasswordCredential
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage

from app.graph.nodes.gating_assistant import gating_assistant
from app.graph.nodes.get_workflows import (
    create_get_workflows_tool,
)
from app.graph.nodes.execute_workflow import create_execute_workflow_tool
from app.graph.nodes.monitor_workflow_execution import create_workflow_run_tool
from app.graph.nodes.task_executor_assistant import task_executor_assistant
from app.graph.nodes.workflow_configurer_assistant import (
    workflow_configurer_assistant,
)
from app.graph.nodes.save_workflow import create_save_workflow_tool
from app.graph.nodes.generate_workflow_code import (
    create_generate_workflow_code_tool,
)
from app.graph.nodes.get_workflow_details import create_get_workflow_details_tool
from app.graph.nodes.get_datetime import create_get_datetime_tool
from app.utils.ai_brain import recaller_tool, encoder_tool, brain_with_embeddings
from app.graph.graph_state import LisaState

from recall_space_agents.toolkits.ms_email.ms_email import MSEmailToolKit
from recall_space_agents.toolkits.ms_site.ms_site import MSSiteToolKit
from recall_space_agents.toolkits.ms_site_workbook.ms_site_workbook import (
    MSSiteWorkbookToolKit,
)
from recall_space_agents.toolkits.ms_todo.ms_todo import MSTodoToolKit
from app.config.env import CLIENT_ID, LISA_PASSWORD, LISA_USER_NAME, TENANT_ID

# Initialize Azure credentials
credentials = UsernamePasswordCredential(
    client_id=CLIENT_ID,
    username=LISA_USER_NAME,
    password=LISA_PASSWORD,
    tenant_id=TENANT_ID,
    authority="https://login.microsoftonline.com/",
)

# Initialize toolkits and tools
ms_todo_toolkit = MSTodoToolKit(credentials=credentials)
tools_todo = ms_todo_toolkit.get_tools()

ms_email_toolkit = MSEmailToolKit(credentials=credentials)
tools_email = ms_email_toolkit.get_tools()
tools_email.pop(1)
ms_sites_toolkit = MSSiteToolKit(credentials=credentials)
tools_sites = ms_sites_toolkit.get_tools()

ms_sites_workbook_toolkit = MSSiteWorkbookToolKit(credentials=credentials)
tools_sites_workbook = ms_sites_workbook_toolkit.get_tools()

task_executor_tools = tools_todo + tools_email + tools_sites + tools_sites_workbook
task_executor_tools_node = ToolNode(
    tools=task_executor_tools,
    messages_key="task_executor_messages",
    name="task_executor_tools",
)

# Workflow Configurer Tools
workflow_configurer_tools = ToolNode(
    tools=[
        create_generate_workflow_code_tool(),
        create_save_workflow_tool(),
    ],
    messages_key="workflow_configurer_messages",
    name="workflow_configurer_tools",
)

# Build Lisa Graph
lisa_builder = StateGraph(LisaState)

# Add gating assistant nodes
lisa_builder.add_node("gating_assistant", gating_assistant)
get_workflows_node = ToolNode(
    tools=[
        create_get_workflows_tool(),
        create_execute_workflow_tool(),
        create_workflow_run_tool(),
        create_get_workflow_details_tool(),
        create_get_datetime_tool(),
        encoder_tool,
        recaller_tool,
    ],
    messages_key="messages",
    name="gating_assistant_tools",
)
lisa_builder.add_node("gating_assistant_tools", get_workflows_node)
lisa_builder.add_edge("gating_assistant_tools", "gating_assistant")
lisa_builder.add_edge(START, "gating_assistant")

# Add task executor nodes
lisa_builder.add_node("task_executor_assistant", task_executor_assistant)
lisa_builder.add_node("task_executor_tools", task_executor_tools_node)
lisa_builder.add_edge("task_executor_tools", "task_executor_assistant")

# Add workflow configurer nodes
lisa_builder.add_node("workflow_configurer_assistant", workflow_configurer_assistant)
lisa_builder.add_node("workflow_configurer_tools", workflow_configurer_tools)
lisa_builder.add_edge("workflow_configurer_tools", "workflow_configurer_assistant")

# Compile the graph
lisa_graph = lisa_builder.compile()