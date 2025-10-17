"""
Workflow API routes for CRUD operations
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from app.database.schemas import (
    Workflow,
    CreateWorkflowRequest,
    UpdateWorkflowRequest,
    ExecuteWorkflowRequest,
)
from app.database.workflow_queries import (
    create_workflow,
    get_workflow_by_name,
    get_all_workflows,
    update_workflow,
    delete_workflow,
)
from app.utils.api_key_required import api_key_required
from app.services.workflow_execution_service import execute_workflow
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/workflows",
    dependencies=[Depends(api_key_required)],
    response_model=Workflow,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new workflow",
    description="Create a new workflow with code, status, and attributes",
)
async def create_new_workflow(request: CreateWorkflowRequest):
    """
    Create a new workflow
    """
    try:
        workflow = Workflow(
            name=request.name,
            code=request.code,
            status=request.status,
            endpoint=request.endpoint,
            attributes=request.attributes or {},
            description=request.description,
            input_parameters=request.input_parameters,
        )
        created_workflow = await create_workflow(workflow)
        return created_workflow
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating workflow: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create workflow")


@router.get(
    "/workflows",
    dependencies=[Depends(api_key_required)],
    response_model=List[Workflow],
    summary="Get all workflows",
    description="Retrieve list of all workflows",
)
async def list_workflows():
    """
    Get all workflows
    """
    try:
        workflows = await get_all_workflows()
        return workflows
    except Exception as e:
        logger.error(f"Error fetching workflows: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch workflows")


@router.get(
    "/workflows/{workflow_name}",
    dependencies=[Depends(api_key_required)],
    response_model=Workflow,
    summary="Get workflow by name",
    description="Retrieve a specific workflow by its name",
)
async def get_workflow(workflow_name: str):
    """
    Get workflow by name
    """
    try:
        workflow = await get_workflow_by_name(workflow_name)
        if not workflow:
            raise HTTPException(
                status_code=404, detail=f"Workflow '{workflow_name}' not found"
            )
        return workflow
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching workflow: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch workflow")


@router.put(
    "/workflows/{workflow_name}",
    dependencies=[Depends(api_key_required)],
    response_model=Workflow,
    summary="Update a workflow",
    description="Update workflow configuration (code, status, attributes, etc.)",
)
async def update_existing_workflow(workflow_name: str, request: UpdateWorkflowRequest):
    """
    Update a workflow
    """
    try:
        # Build update dictionary with only provided fields
        update_data = {}
        if request.code is not None:
            update_data["code"] = request.code
        if request.status is not None:
            update_data["status"] = request.status
        if request.endpoint is not None:
            update_data["endpoint"] = request.endpoint
        if request.attributes is not None:
            update_data["attributes"] = request.attributes
        if request.description is not None:
            update_data["description"] = request.description
        if request.input_parameters is not None:
            update_data["input_parameters"] = request.input_parameters

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        updated_workflow = await update_workflow(workflow_name, update_data)
        if not updated_workflow:
            raise HTTPException(
                status_code=404, detail=f"Workflow '{workflow_name}' not found"
            )

        return updated_workflow
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating workflow: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update workflow")


@router.delete(
    "/workflows/{workflow_name}",
    dependencies=[Depends(api_key_required)],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a workflow",
    description="Delete a workflow by name",
)
async def delete_existing_workflow(workflow_name: str):
    """
    Delete a workflow
    """
    try:
        deleted = await delete_workflow(workflow_name)
        if not deleted:
            raise HTTPException(
                status_code=404, detail=f"Workflow '{workflow_name}' not found"
            )
        return
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting workflow: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete workflow")


@router.post(
    "/workflows/{workflow_name}/execute",
    dependencies=[Depends(api_key_required)],
    summary="Execute a workflow",
    description="Execute a workflow with input data validation",
)
async def execute_workflow_endpoint(
    workflow_name: str, request: ExecuteWorkflowRequest
):
    """
    Execute a workflow by validating input and making POST request to endpoint
    """
    try:
        result = await execute_workflow(request.workflow_name, request.input_data)
        return {
            "status": "success",
            "workflow_name": request.workflow_name,
            "result": result,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing workflow: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to execute workflow: {str(e)}"
        )
