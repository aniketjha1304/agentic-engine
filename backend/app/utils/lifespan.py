from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
import logging
from zoneinfo import ZoneInfo
from app.utils.send_checkin_emails import send_checkin_emails
from app.utils.create_cleaning_order import schedule_cleaning_orders
from app.utils.delete_unpaid_bookings import delete_unpaid_bookings
from app.utils.assign_apartment_pins import assign_apartment_pins
from apscheduler.triggers.interval import IntervalTrigger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Create the APScheduler instance
scheduler = AsyncIOScheduler()


# Lifespan context manager to manage startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles the scheduling of tasks during app startup and shutdown."""
    # Start the scheduler on app startup
    scheduler.add_job(
        send_checkin_emails,
        CronTrigger(hour=18, minute=0, timezone=ZoneInfo("Europe/Berlin")),
        id="send_checkin_emails_daily",
    )
    scheduler.add_job(
        schedule_cleaning_orders,
        CronTrigger(hour=18, minute=0, timezone=ZoneInfo("Europe/Berlin")),
        id="schedule_cleaning_orders_daily",
    )
    # Run delete_unpaid_bookings every hour
    scheduler.add_job(
        delete_unpaid_bookings,
        CronTrigger(minute=0, timezone=ZoneInfo("Europe/Berlin")),
        id="delete_unpaid_bookings_hourly",
    )
    scheduler.add_job(
        assign_apartment_pins,
        CronTrigger(hour=8, minute=0, timezone=ZoneInfo("Europe/Berlin")),
        id="assign_apartment_pins_daily",
    )

    scheduler.start()
    logger.info("Scheduler started, running check-in email task every day at 6 PM CET.")
    logger.info(
        "Scheduler started, running cleaning service task every Sunday at 6 PM CET."
    )
    logger.info(
        "Scheduler started, running delete unpaid bookings task every hour at the top of the hour CET."
    )
    logger.info(
        "Scheduler started, running assign apartment pins every morning 8 AM CET."
    )

    # Yield control back to FastAPI
    yield

    # Shutdown the scheduler on app shutdown
    scheduler.shutdown()
    logger.info("Scheduler stopped.")
