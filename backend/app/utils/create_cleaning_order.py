from app.utils.execute_http_trigger_workflow import execute_http_trigger_workflow
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def schedule_cleaning_orders():

    try:
        logger.info(f"Executing `Schedule cleaning orders` as per the schedule")
        data = await execute_http_trigger_workflow(
            workflow_title="Schedule cleaning orders"
        )
        logger.info(
            f"Result from executing `Schedule cleaning orders` workflow: {data}"
        )
    except Exception as e:
        logger.error(f"Error while processing cleaning orders: {e}")
