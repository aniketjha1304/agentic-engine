from app.utils.execute_http_trigger_workflow import execute_http_trigger_workflow
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def delete_unpaid_bookings():
    """Fetches unpaid bookings and deletes them if still unpaid."""
    try:
        logger.info(f"Executing `Remove unpaid bookings`")
        data = await execute_http_trigger_workflow(
            workflow_title="Remove unpaid bookings"
        )
        logger.info(f"Result from executing `Remove unpaid bookings` workflow: {data}")
    except Exception as e:
        logger.error(f"Error while processing unpaid bookings: {e}")
