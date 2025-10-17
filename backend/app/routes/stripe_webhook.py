# ====================== stripe_webhook.py ======================
"""
stripe_webhook.py

This file now contains a simplified FastAPI router that:
1) Listens for Stripe Webhook events.
2) Verifies the webhook signature.
3) Calls our external "Confirm Reservation Workflow" via the built-in execute_http_trigger_workflow utility
   to handle reservation confirmation tasks (database updates, emails, etc.), instead of performing them here.

"""

import os
import logging
import stripe
import json
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from recall_space_agents.toolkits.ms_email.ms_email import MSEmailToolKit
from app.utils.execute_http_trigger_workflow import execute_http_trigger_workflow

logger = logging.getLogger(__name__)
router = APIRouter()

# Stripe configuration
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
if not STRIPE_SECRET_KEY:
    logger.error("STRIPE_SECRET_KEY not found")
    raise RuntimeError("STRIPE_SECRET_KEY is required")

stripe.api_key = STRIPE_SECRET_KEY


@router.post("/webhook")
async def stripe_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Stripe Webhook Listener.

    This endpoint receives Stripe events and verifies their signature.
    If the event is valid, we delegate further processing to a workflow
    (Confirm Reservation Workflow) in the background.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    # Basic logs for incoming event
    logger.info("===== Stripe Webhook Received =====")
    logger.info("Request Headers: %s", dict(request.headers))
    logger.info("Raw Payload: %s", payload)

    if not STRIPE_WEBHOOK_SECRET:
        logger.error("⚠️ STRIPE_WEBHOOK_SECRET is missing!")
        raise HTTPException(status_code=500, detail="Stripe Webhook Secret not set")

    try:
        # Verify signature and construct event
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )

        # Convert entire event to JSON string for full visibility (helpful for debugging)
        event_as_json = json.dumps(event, indent=2, default=str)
        logger.info(f"Full Event Object:\n{event_as_json}")

        event_type = event["type"]
        logger.info(f"📩 Received Stripe Event: {event_type}")

        # We'll handle two main events:
        # 1) checkout.session.completed
        # 2) payment_intent.succeeded
        if event_type == "checkout.session.completed":
            session = event["data"]["object"]
            session_id = session.get("id")
            logger.info(f"🛒 Checkout Session Completed. ID: {session_id}")

            # Retrieve session metadata
            metadata = session.get("metadata", {})
            logger.info(f"Metadata for checkout.session.completed: {metadata!r}")

            customer_id = metadata.get("customer_id")
            booking_id = metadata.get("booking_id")
            payment_id = metadata.get("payment_id")

            logger.info(
                "Extracted from metadata => customer_id: %s, booking_id: %s, payment_id: %s",
                customer_id,
                booking_id,
                payment_id,
            )

            if not all([customer_id, booking_id, payment_id]):
                logger.error(
                    "❌ Missing required metadata from checkout.session.completed"
                )
                return {"error": "Missing metadata"}

            amount_total = session.get("amount_total", 0)
            logger.info(f"Checkout Session amount_total: {amount_total}")

            # If zero-amount, confirm reservation right away
            if amount_total == 0:
                logger.info("Zero amount payment => Confirming reservation now.")
                background_tasks.add_task(
                    execute_http_trigger_workflow,
                    workflow_title="Process payment confirmation",
                    input_parameters={
                        "booking_id": booking_id,
                        "payment_id": payment_id,
                        "customer_id": customer_id,
                        "stripe_intent_id": session.get("payment_intent", ""),
                        "amount_received": 0,
                    },
                )
            else:
                logger.info(
                    "Non-zero checkout session; expecting payment_intent.succeeded later."
                )

        elif event_type == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            pi_id = payment_intent.get("id", "")
            logger.info(f"✅ Payment Intent Succeeded: {pi_id}")

            # Retrieve payment_intent metadata
            metadata = payment_intent.get("metadata", {})
            logger.info(f"Metadata for payment_intent.succeeded: {metadata!r}")

            customer_id = metadata.get("customer_id")
            booking_id = metadata.get("booking_id")
            payment_id = metadata.get("payment_id")
            stripe_intent_id = pi_id
            amount_received = payment_intent.get("amount_received", 0)

            logger.info(
                "Extracted from metadata => customer_id: %s, booking_id: %s, payment_id: %s, stripe_intent_id: %s, amount_received (in cents): %s",
                customer_id,
                booking_id,
                payment_id,
                stripe_intent_id,
                amount_received,
            )

            if not all([customer_id, booking_id, payment_id]):
                logger.error(
                    "❌ Missing required metadata from payment_intent.succeeded"
                )
                return {"error": "Missing metadata"}

            # Extract additional metadata (beyond the standard fields)
            # This includes is_prolongation, new_end_date, etc.
            standard_fields = {"customer_id", "booking_id", "payment_id"}
            additional_metadata = {
                k: v for k, v in metadata.items() if k not in standard_fields
            }

            if additional_metadata:
                logger.info(f"Additional metadata found: {additional_metadata}")

            # Trigger the background workflow
            background_tasks.add_task(
                execute_http_trigger_workflow,
                workflow_title="Process payment confirmation",
                input_parameters={
                    "booking_id": booking_id,
                    "payment_id": payment_id,
                    "customer_id": customer_id,
                    "stripe_intent_id": stripe_intent_id,
                    "amount_received": amount_received,
                    "additional_metadata": additional_metadata,  # Pass all extra metadata
                },
            )

        else:
            logger.info(f"ℹ️ Unhandled Stripe Event: {event_type}")

        logger.info("Webhook processing complete. Returning success response.")
        return {"success": True}

    except stripe.error.SignatureVerificationError:
        logger.error("❌ Invalid Stripe signature!")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logger.error(f"❌ Webhook Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Webhook Error")
