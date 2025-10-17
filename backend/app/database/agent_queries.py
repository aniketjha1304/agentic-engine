"""
Agent CRUD operations for MongoDB
"""
from typing import List, Optional
from datetime import datetime
from app.database.mongo_db import get_collection
from app.database.schemas import Agent
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def create_agent(agent_data: Agent) -> Agent:
    """
    Create a new agent
    
    Args:
        agent_data: Agent object to create
        
    Returns:
        Created agent
    """
    collection = get_collection("agents")
    
    # Check if agent with same name already exists
    existing = await collection.find_one({"name": agent_data.name})
    if existing:
        raise ValueError(f"Agent with name '{agent_data.name}' already exists")
    
    agent_dict = agent_data.model_dump()
    result = await collection.insert_one(agent_dict)
    logger.info(f"Created agent: {agent_data.name}")
    return agent_data


async def get_agent_by_name(name: str) -> Optional[Agent]:
    """
    Get agent by name
    
    Args:
        name: Name of the agent
        
    Returns:
        Agent object or None
    """
    collection = get_collection("agents")
    agent_doc = await collection.find_one({"name": name})
    
    if agent_doc:
        # Remove MongoDB _id field
        agent_doc.pop("_id", None)
        return Agent(**agent_doc)
    return None


async def get_all_agents() -> List[Agent]:
    """
    Get all agents
    
    Returns:
        List of agents
    """
    collection = get_collection("agents")
    cursor = collection.find({})
    agents = []
    
    async for doc in cursor:
        doc.pop("_id", None)
        agents.append(Agent(**doc))
    
    return agents


async def update_agent(name: str, update_data: dict) -> Optional[Agent]:
    """
    Update an agent
    
    Args:
        name: Name of the agent to update
        update_data: Dictionary with fields to update
        
    Returns:
        Updated agent or None
    """
    collection = get_collection("agents")
    
    # Add updated_at timestamp
    update_data["updated_at"] = datetime.utcnow()
    
    result = await collection.update_one(
        {"name": name},
        {"$set": update_data}
    )
    
    if result.modified_count > 0:
        logger.info(f"Updated agent: {name}")
        return await get_agent_by_name(name)
    
    return None


async def delete_agent(name: str) -> bool:
    """
    Delete an agent
    
    Args:
        name: Name of the agent to delete
        
    Returns:
        True if deleted, False otherwise
    """
    collection = get_collection("agents")
    result = await collection.delete_one({"name": name})
    
    if result.deleted_count > 0:
        logger.info(f"Deleted agent: {name}")
        return True
    
    return False
