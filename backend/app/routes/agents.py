"""
Agent API routes for CRUD operations
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from app.database.schemas import (
    Agent,
    CreateAgentRequest,
    UpdateAgentRequest,
)
from app.database.agent_queries import (
    create_agent,
    get_agent_by_name,
    get_all_agents,
    update_agent,
    delete_agent,
)
from app.services.agent_service import get_agent_info
from app.utils.api_key_required import api_key_required
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/agents",
    dependencies=[Depends(api_key_required)],
    response_model=Agent,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new agent",
    description="Create a new AI agent with system prompt and associated workflows",
)
async def create_new_agent(request: CreateAgentRequest):
    """
    Create a new agent
    """
    try:
        agent = Agent(
            name=request.name,
            system_prompt=request.system_prompt,
            workflow_names=request.workflow_names,
            llm_config=request.llm_config or {},
        )
        created_agent = await create_agent(agent)
        return created_agent
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create agent")


@router.get(
    "/agents",
    dependencies=[Depends(api_key_required)],
    response_model=List[Agent],
    summary="Get all agents",
    description="Retrieve list of all agents",
)
async def list_agents():
    """
    Get all agents
    """
    try:
        agents = await get_all_agents()
        return agents
    except Exception as e:
        logger.error(f"Error fetching agents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch agents")


@router.get(
    "/agents/{agent_name}",
    dependencies=[Depends(api_key_required)],
    summary="Get agent by name",
    description="Retrieve a specific agent with its workflow information",
)
async def get_agent(agent_name: str):
    """
    Get agent by name with workflow details
    """
    try:
        agent_info = await get_agent_info(agent_name)
        if not agent_info:
            raise HTTPException(
                status_code=404, detail=f"Agent '{agent_name}' not found"
            )
        return agent_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching agent: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch agent")


@router.put(
    "/agents/{agent_name}",
    dependencies=[Depends(api_key_required)],
    response_model=Agent,
    summary="Update an agent",
    description="Update agent configuration (system prompt, workflows, etc.)",
)
async def update_existing_agent(agent_name: str, request: UpdateAgentRequest):
    """
    Update an agent
    """
    try:
        # Build update dictionary with only provided fields
        update_data = {}
        if request.system_prompt is not None:
            update_data["system_prompt"] = request.system_prompt
        if request.workflow_names is not None:
            update_data["workflow_names"] = request.workflow_names
        if request.llm_config is not None:
            update_data["llm_config"] = request.llm_config

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        updated_agent = await update_agent(agent_name, update_data)
        if not updated_agent:
            raise HTTPException(
                status_code=404, detail=f"Agent '{agent_name}' not found"
            )

        return updated_agent
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update agent")


@router.delete(
    "/agents/{agent_name}",
    dependencies=[Depends(api_key_required)],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an agent",
    description="Delete an agent by name",
)
async def delete_existing_agent(agent_name: str):
    """
    Delete an agent
    """
    try:
        deleted = await delete_agent(agent_name)
        if not deleted:
            raise HTTPException(
                status_code=404, detail=f"Agent '{agent_name}' not found"
            )
        return
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting agent: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete agent")
