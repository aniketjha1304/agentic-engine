"""
Agent Service - Runtime agent building with dynamic prompts and workflows
"""

from typing import List, Optional
from agent_builder.builders.agent_builder import AgentBuilder
from app.config.default import default_llm_dict
from app.database.agent_queries import get_agent_by_name
from app.database.workflow_queries import get_workflows_by_names
from app.database.schemas import Agent, Workflow
from app.tools.get_workflow_details import create_get_workflow_details_tool
from app.tools.execute_workflow import create_execute_workflow_tool
from app.tools.list_workflows import create_list_workflows_tool
from app.utils.logger import get_logger

logger = get_logger(__name__)


def build_system_prompt_with_workflows(
    base_prompt: str, workflows: List[Workflow]
) -> str:
    """
    Build complete system prompt by adding workflow descriptions

    Args:
        base_prompt: Base system prompt from agent config
        workflows: List of workflows available to the agent

    Returns:
        Complete system prompt with workflow descriptions
    """
    if not workflows:
        return base_prompt

    workflow_descriptions = "\n\n## Available Workflows\n\n"
    workflow_descriptions += "You have access to the following workflows/skills:\n\n"

    for workflow in workflows:
        workflow_descriptions += f"### {workflow.name}\n"
        if workflow.description:
            workflow_descriptions += f"{workflow.description}\n"
        if workflow.endpoint:
            workflow_descriptions += f"Endpoint: {workflow.endpoint}\n"
        workflow_descriptions += f"Status: {workflow.status}\n\n"

    return base_prompt + workflow_descriptions


async def build_agent_runtime(agent_name: str):
    """
    Build an agent at runtime based on its configuration

    This function:
    1. Fetches the agent configuration from database
    2. Fetches associated workflows
    3. Builds the system prompt with workflow descriptions
    4. Creates and returns the agent instance

    Args:
        agent_name: Name of the agent to build

    Returns:
        Built agent instance ready for invocation

    Raises:
        ValueError: If agent not found or configuration invalid
    """
    # Fetch agent configuration
    agent = await get_agent_by_name(agent_name)
    if not agent:
        raise ValueError(f"Agent '{agent_name}' not found")

    logger.info(f"Building agent: {agent_name}")

    # Fetch associated workflows
    workflows = []
    if agent.workflow_names:
        workflows = await get_workflows_by_names(agent.workflow_names)
        logger.info(f"Loaded {len(workflows)} workflows for agent {agent_name}")

    # Build complete system prompt with workflow descriptions
    complete_prompt = build_system_prompt_with_workflows(agent.system_prompt, workflows)

    # Create agent using AgentBuilder (similar to build_lisa.py approach)
    agent_builder = AgentBuilder()
    agent_builder.set_goal(complete_prompt)

    # Set LLM (use default or from agent config)
    llm_key = agent.llm_config.get("llm_key", "azure_openai_gpt4o")
    if llm_key in default_llm_dict:
        agent_builder.set_llm(default_llm_dict[llm_key])
    else:
        agent_builder.set_llm(default_llm_dict["azure_openai_gpt4o"])

    # Add default tools for workflow interaction
    list_workflows_tool = create_list_workflows_tool()
    get_workflow_details_tool = create_get_workflow_details_tool()
    execute_workflow_tool = create_execute_workflow_tool()

    agent_builder.add_tool(list_workflows_tool)
    agent_builder.add_tool(get_workflow_details_tool)
    agent_builder.add_tool(execute_workflow_tool)

    logger.info(f"Added default workflow tools to agent: {agent_name}")

    # Build and return the agent
    built_agent = agent_builder.build()
    logger.info(f"Successfully built agent: {agent_name}")

    return built_agent


async def get_agent_info(agent_name: str) -> Optional[dict]:
    """
    Get agent information including workflows

    Args:
        agent_name: Name of the agent

    Returns:
        Dictionary with agent info and workflows
    """
    agent = await get_agent_by_name(agent_name)
    if not agent:
        return None

    workflows = []
    if agent.workflow_names:
        workflows = await get_workflows_by_names(agent.workflow_names)

    return {
        "agent": agent.model_dump(),
        "workflows": [w.model_dump() for w in workflows],
    }
