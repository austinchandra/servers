import os
from typing import Any
from lib.db import Database
from lib.stripe import (
    get_api_key,
    get_endpoint_secret,
    InvalidPayload,
    SignatureVerificationFailed,
)
import stripe

from lib.types import StripeCheckouts


db = Database(url=os.getenv("DATABASE_URL"))
stripe.api_key = get_api_key()


def begin_fulfillment(session_id: str, event_type: str):
    """
    Begins fulfillment process of checkout sessions
    with a successful payment.

    This operation is idempotent, i.e. fulfillment only
    occurs at most once regardless of the number of attempts.
    """

    checkout = StripeCheckouts(id=session_id)
    should_process = db.record_stripe_checkout(checkout)
    if not should_process:
        return

    # TODO: Place this event on the SQS queue for processing.
    pass


def process_webhook_request(payload: Any, signature: Any):
    """
    Validates the webhook request and places
    the processed event on the event pipeline.
    """

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header=signature, secret=get_endpoint_secret()
        )
    except ValueError:
        raise InvalidPayload()
    except stripe.error.SignatureVerificationError:
        raise SignatureVerificationFailed()

    if (
        event.type == "checkout.session.completed"
        or event.type == "checkout.session.async_payment_succeeded"
    ):
        begin_fulfillment(event.data.object["id"], event.type)
