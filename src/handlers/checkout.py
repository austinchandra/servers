import os
from typing import Any
from lib.db import Database
from lib.stripe import (
    get_api_key,
    get_endpoint_secret,
)
from lib.queue import Queue
from lib.errors import StripeException
import stripe

from lib.types import StripeCheckout

db = Database(url=os.environ["DATABASE_URL"])
queue = Queue(queue_url=os.environ["STRIPE_QUEUE_URL"])
stripe.api_key = get_api_key()


def begin_fulfillment(session_id: str):
    """
    Begin fulfilling a checkout session on successful payment,
    using an idempotent operation as required by Stripe.
    """
    checkout = StripeCheckout(id=session_id)
    should_process = db.record_stripe_checkout(checkout)
    if not should_process:
        return

    queue.send({"id": checkout.id})


def process_webhook_request(payload: Any, signature: Any):
    """
    Validates and processes the request.
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header=signature, secret=get_endpoint_secret()
        )
    except ValueError:
        raise StripeException()
    except stripe.error.SignatureVerificationError:
        raise StripeException()

    if (
        event.type == "checkout.session.completed"
        or event.type == "checkout.session.async_payment_succeeded"
    ):
        begin_fulfillment(event.data.object["id"])
