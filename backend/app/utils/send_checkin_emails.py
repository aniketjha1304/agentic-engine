from app.utils.execute_http_trigger_workflow import execute_http_trigger_workflow
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def send_checkin_emails():
    try:
        logger.info("Executing the workflow `Send Checkin Emails` as per the schedule")
        data = await execute_http_trigger_workflow(workflow_title="Send Checkin Emails")
        logger.info(f"Result from executing `Send Checkin Emails` workflow: {data}")
    except Exception as e:
        logger.error(f"Error while processing check-in emails: {e}")
