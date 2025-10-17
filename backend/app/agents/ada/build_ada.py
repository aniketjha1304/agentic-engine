"""
Definition of Ada agent
"""

from textwrap import dedent
from agent_builder.builders.agent_builder import AgentBuilder
from app.config.default import default_llm_dict
from app.agents.ada.prompt.chat_prompt import get_chat_ada_prompt

from app.agents.lisa.tools.get_workflow_details import create_get_workflow_details_tool
from app.agents.lisa.tools.get_workflows import create_get_workflows_tool
from app.agents.ada.tools.create_skill import build_create_workflow_tool
from app.agents.ada.tools.update_skill import build_update_workflow_tool
from app.agents.ada.tools.propose_workflow import build_propose_workflow_tool
from app.agents.ada.tools.explore_workflow_examples import (
    create_get_workflow_examples_tool,
)
from app.agents.ada.tools.explore_internal_packages import (
    create_explore_internal_package_tool,
)



async def build_ada_chat_agent(workflow_manager: object):
    lisa_prompt = await get_chat_ada_prompt()
    agent_builder = AgentBuilder()
    agent_builder.set_goal(dedent(lisa_prompt))
    agent_builder.set_llm(default_llm_dict["azure_openai_gpt4o"])

    # Add the retrieval tool to the agent
    lisa_tools = get_ada_tools(workflow_manager)
    for tool in lisa_tools:
        agent_builder.add_tool(tool)
    # Build and return the agent
    ada = agent_builder.build()
    return ada


def get_ada_tools(workflow_manager):

    ada_tools = [
        create_get_workflow_details_tool(),
        create_get_workflows_tool(),
        create_explore_internal_package_tool(),
        build_create_workflow_tool(workflow_manager),
        build_update_workflow_tool(workflow_manager),
        build_propose_workflow_tool(workflow_manager),
        create_get_workflow_examples_tool(),
    ]
    return ada_tools
