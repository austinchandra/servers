import os
from typing import Any
from lib.db import Database
from lib.stripe import (
    StripeException,
    get_api_key,
    get_endpoint_secret,
)
import stripe

from lib.types import StripeCheckout


db = Database(url=os.getenv("DATABASE_URL"))
stripe.api_key = get_api_key()


def begin_fulfillment(session_id: str, event_type: str):
    """
    Begin fulfilling a checkout session on successful payment,
    using an idempotent operation as required by Stripe.
    """

    checkout = StripeCheckout(id=session_id)
    should_process = db.record_stripe_checkout(checkout)
    if not should_process:
        return

    # TODO: Place this event on the SQS queue for processing.
    pass


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
        begin_fulfillment(event.data.object["id"], event.type)
