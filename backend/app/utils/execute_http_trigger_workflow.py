from typing import Optional, Dict, Any, Union
import json
import aiohttp
from app.config.env import WORKFLOW_FUNCTION_APP_MASTER_KEY
from app.config.default import (
    WORKFLOW_ACTIVE_STATUS,
    WORKFLOW_TYPE_HTTP_TRIGGER,
)
from app.database.ai_persona_hub_queries import (
    get_workflow_by_title,
    get_http_trigger_workflow_data,
    update_workflow_run,
    is_budget_sufficient,
)
from jsonschema import validate, ValidationError
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def execute_http_trigger_workflow(
    workflow_title: str,
    input_parameters: Optional[Dict[str, Any]] = None,
    wait_for_response: bool = True,
) -> Dict[str, Any]:
    """
    Execute a workflow based on the given title and input parameters.

    Args:
        workflow_title (str): The title of the workflow to be executed.
        input_parameters (Optional[Dict[str, Any]]): Input parameters matching
            the workflow's input signature.
        wait_for_response (bool): Whether to wait for the HTTP response.

    Returns:
        Dict[str, Any]: A dictionary containing 'success' (bool) and 'message' or 'data'.
    """
    try:
        is_budget_sufficient_result = await is_budget_sufficient(
            workflow_title=workflow_title, number_of_runs=1
        )
        if not is_budget_sufficient_result:
            return {
                "success": False,
                "message": """
                    This workflow requires more budget than is currently available. 
                    """,
            }
        workflow_data = await get_workflow_by_title(title=workflow_title)
        logger.info(f"Input parameters: {input_parameters}")
        logger.info(f"Workflow Data: {workflow_data}")

        if not isinstance(workflow_data, dict):
            return {"success": False, "message": "Invalid workflow data format."}

        if (
            (workflow_data is None)
            or (workflow_data["type"] != WORKFLOW_TYPE_HTTP_TRIGGER)
            or (workflow_data["status"] != WORKFLOW_ACTIVE_STATUS)
        ):
            return {
                "success": False,
                "message": f"No workflow found with title '{workflow_title}'.",
            }

        workflow_trigger_data = await get_http_trigger_workflow_data(
            workflow_id=workflow_data["id"]
        )
        logger.info(f"Workflow Trigger Data: {workflow_trigger_data}")
        if not isinstance(workflow_trigger_data, dict):
            return {
                "success": False,
                "message": "Invalid workflow trigger data format.",
            }
        workflow_endpoint = workflow_trigger_data["workflow_endpoint"]
        workflow_input_state = workflow_trigger_data["workflow_input_state"]

        # Convert the input signature to python dictionary.
        input_signature = (
            json.loads(workflow_input_state)
            if isinstance(workflow_input_state, str)
            else workflow_input_state
        )

        # Validate input parameters
        if input_signature:
            validation_result = validate_input_parameters(
                input_signature, input_parameters
            )
            logger.info(f"Vlidation Result: {validation_result}")
            if not validation_result["success"]:
                # Return the validation error
                return validation_result

        # Invoke the workflow endpoint
        data = input_parameters or {}

        # Always add the accountable user id
        data["accountable_user_id"] = workflow_data["accountable_user_id"]
        response = await invoke_workflow_endpoint(
            url=workflow_endpoint,
            data=data,
            wait_for_response=wait_for_response,
        )
        # Update the workflow run and total cost
        await update_workflow_run(workflow_title=workflow_title, number_of_runs=1)
        if wait_for_response:
            return {"success": True, "message": response}

        return {
            "success": True,
            "message": response,
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"""
                Error executing workflow: {str(e)}
                Hint: Check for details of workflow and comply with inputsignature if there is any 
                and  check for values with user if required.
                """,
        }


def validate_input_parameters(
    input_signature: Dict[str, Any],
    input_parameters: Optional[Dict[str, Any]],
) -> Optional[str]:
    """
    Validate the provided input_parameters against the input_signature (JSON Schema).

    Args:
        input_signature (Dict[str, Any]): The required input signature as a JSON Schema.
        input_parameters (Optional[Dict[str, Any]]): The input parameters provided by the user.

    Returns:
        Optional[str]: An error message if validation fails; otherwise, None.
    """

    try:
        # Validate input_parameters against the JSON Schema
        validate(instance=input_parameters, schema=input_signature)
        validation_result = {"success": True, "message": "Validation Successful"}
    except Exception as e:
        logger.error(f"Error while validation: {str(e)}")
        validation_result = {
            "success": False,
            "message": f"""Input parameter validation failed with following error: {str(e)}
                Please follow the input signature schema: {input_signature}.
                Hint: Comply with the input signature schema and check for values with user if required.
                """,
        }
    return validation_result


async def invoke_workflow_endpoint(
    url: str, data: Dict[str, Any], wait_for_response: bool
) -> Union[None, Dict[str, Any], str]:
    """
    Invoke the workflow endpoint with the provided data.
    """
    try:
        wait_for_response = True
        response_text = f"The workflow  has been invoked successfully. It might take a while until the job is finished."
        functions_key = WORKFLOW_FUNCTION_APP_MASTER_KEY
        if not functions_key:
            raise ValueError(
                "The WORKFLOW_FUNCTION_APP_MASTER_KEY environment variable is not set."
            )

        headers = {
            "x-functions-key": functions_key,
            "Accept": "text/plain",  # Expect plain text response
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                if wait_for_response:
                    response_text = await response.text()

                    # Try to parse as JSON (if applicable)
                    try:
                        return json.loads(
                            response_text
                        )  # Convert to dict if it's valid JSON
                    except json.JSONDecodeError:
                        return response_text  # Otherwise, return as plain text

    except Exception as e:
        raise Exception(f"Exception occurred while invoking workflow: {str(e)}")
