from app.utils.execute_http_trigger_workflow import execute_http_trigger_workflow
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def assign_apartment_pins():

    try:
        logger.info(f"Executing `Assign apartment pins` as per the schedule")
        data = await execute_http_trigger_workflow(
            workflow_title="Assign apartment pins", input_parameters={"days_offset": 0}
        )
        logger.info(f"Result from executing `Assign apartment pins` workflow: {data}")
    except Exception as e:
        logger.error(f"Error while assigning apartment pins: {e}")
