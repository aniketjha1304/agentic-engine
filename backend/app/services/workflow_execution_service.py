"""
Workflow Execution Service - Validates input and executes workflows
"""
from typing import Dict, Any
import jsonschema
from jsonschema import validate, ValidationError
import httpx
from app.database.workflow_queries import get_workflow_by_name
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def execute_workflow(workflow_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a workflow by validating input against JSON schema and making POST request
    
    Args:
        workflow_name: Name of the workflow to execute
        input_data: Input data dictionary to pass to the workflow
        
    Returns:
        Response from the workflow execution
        
    Raises:
        ValueError: If workflow not found or validation fails
        Exception: If workflow execution fails
    """
    # Fetch workflow from database
    workflow = await get_workflow_by_name(workflow_name)
    if not workflow:
        raise ValueError(f"Workflow '{workflow_name}' not found")
    
    # Check if workflow is active
    if workflow.status != "active":
        raise ValueError(f"Workflow '{workflow_name}' is not active (status: {workflow.status})")
    
    # Validate input against JSON schema if provided
    if workflow.input_parameters:
        try:
            validate(instance=input_data, schema=workflow.input_parameters)
            logger.info(f"Input validation successful for workflow: {workflow_name}")
        except ValidationError as e:
            error_msg = f"Input validation failed for workflow '{workflow_name}': {e.message}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    else:
        logger.warning(f"No input schema defined for workflow: {workflow_name}")
    
    # Check if endpoint is defined
    if not workflow.endpoint:
        raise ValueError(f"No endpoint defined for workflow '{workflow_name}'")
    
    # Execute workflow via POST request
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                workflow.endpoint,
                json=input_data
            )
            response.raise_for_status()
            
            logger.info(f"Workflow '{workflow_name}' executed successfully")
            return response.json()
            
    except httpx.HTTPError as e:
        error_msg = f"Failed to execute workflow '{workflow_name}': {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error executing workflow '{workflow_name}': {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)


async def validate_workflow_input(workflow_name: str, input_data: Dict[str, Any]) -> bool:
    """
    Validate input data against workflow's JSON schema
    
    Args:
        workflow_name: Name of the workflow
        input_data: Input data to validate
        
    Returns:
        True if validation passes
        
    Raises:
        ValueError: If validation fails
    """
    workflow = await get_workflow_by_name(workflow_name)
    if not workflow:
        raise ValueError(f"Workflow '{workflow_name}' not found")
    
    if workflow.input_parameters:
        try:
            validate(instance=input_data, schema=workflow.input_parameters)
            return True
        except ValidationError as e:
            raise ValueError(f"Validation error: {e.message}")
    
    return True
