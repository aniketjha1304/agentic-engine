"""
Workflow CRUD operations for MongoDB
"""
from typing import List, Optional
from datetime import datetime
from app.database.mongo_db import get_collection
from app.database.schemas import Workflow
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def create_workflow(workflow_data: Workflow) -> Workflow:
    """
    Create a new workflow
    
    Args:
        workflow_data: Workflow object to create
        
    Returns:
        Created workflow
    """
    collection = get_collection("workflows")
    
    # Check if workflow with same name already exists
    existing = await collection.find_one({"name": workflow_data.name})
    if existing:
        raise ValueError(f"Workflow with name '{workflow_data.name}' already exists")
    
    workflow_dict = workflow_data.model_dump()
    result = await collection.insert_one(workflow_dict)
    logger.info(f"Created workflow: {workflow_data.name}")
    return workflow_data


async def get_workflow_by_name(name: str) -> Optional[Workflow]:
    """
    Get workflow by name
    
    Args:
        name: Name of the workflow
        
    Returns:
        Workflow object or None
    """
    collection = get_collection("workflows")
    workflow_doc = await collection.find_one({"name": name})
    
    if workflow_doc:
        workflow_doc.pop("_id", None)
        return Workflow(**workflow_doc)
    return None


async def get_workflows_by_names(names: List[str]) -> List[Workflow]:
    """
    Get multiple workflows by names
    
    Args:
        names: List of workflow names
        
    Returns:
        List of workflows
    """
    collection = get_collection("workflows")
    cursor = collection.find({"name": {"$in": names}})
    workflows = []
    
    async for doc in cursor:
        doc.pop("_id", None)
        workflows.append(Workflow(**doc))
    
    return workflows


async def get_all_workflows() -> List[Workflow]:
    """
    Get all workflows
    
    Returns:
        List of workflows
    """
    collection = get_collection("workflows")
    cursor = collection.find({})
    workflows = []
    
    async for doc in cursor:
        doc.pop("_id", None)
        workflows.append(Workflow(**doc))
    
    return workflows


async def update_workflow(name: str, update_data: dict) -> Optional[Workflow]:
    """
    Update a workflow
    
    Args:
        name: Name of the workflow to update
        update_data: Dictionary with fields to update
        
    Returns:
        Updated workflow or None
    """
    collection = get_collection("workflows")
    
    # Add updated_at timestamp
    update_data["updated_at"] = datetime.utcnow()
    
    result = await collection.update_one(
        {"name": name},
        {"$set": update_data}
    )
    
    if result.modified_count > 0:
        logger.info(f"Updated workflow: {name}")
        return await get_workflow_by_name(name)
    
    return None


async def delete_workflow(name: str) -> bool:
    """
    Delete a workflow
    
    Args:
        name: Name of the workflow to delete
        
    Returns:
        True if deleted, False otherwise
    """
    collection = get_collection("workflows")
    result = await collection.delete_one({"name": name})
    
    if result.deleted_count > 0:
        logger.info(f"Deleted workflow: {name}")
        return True
    
    return False
