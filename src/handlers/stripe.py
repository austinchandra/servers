import json
import os

from lib.db import Database
from lib.errors import StripeException
from lib.printful import (
    PRINTFUL_STATUS_MAP,
    PrintfulClient,
    PrintfulItem,
    PrintfulRecipient,
)
from lib.logs import Logs
from lib.queue import Queue
from lib.types import Order, OrderStatus, Checkout
import requests
import stripe

db = Database(url=os.environ("DATABASE_URL"))
log = Logs(log_group=os.environ["LOG_GROUP"])
printful = PrintfulClient(api_key=os.environ("PRINTFUL_API_KEY"))
queue = Queue(queue_url=os.environ["STRIPE_QUEUE_URL"])
secret = os.environ["STRIPE_WEBHOOK_ENDPOINT_SECRET"]
stripe.api_key = os.environ["STRIPE_API_KEY"]


def handler(event: dict, context):
    """
    Entry point invoked by SQS. Processes each record in the event,
    which should contain a checkout session ID in its body.
    """
    for record in event["Records"]:
        body = json.loads(record["body"])
        checkout = Checkout(id=body["id"])
        _fulfill_checkout(checkout)


def consumer(event, context):
    """
    Entry point from a purchase receives a request from Stripe and
    checks for idempotency before adding it to the queue.
    """
    try:
        payload = event["body"]
        signature = event["headers"]["Stripe-Signature"]

        event = stripe.Webhook.construct_event(
            payload, sig_header=signature, secret=secret
        )
    except ValueError:
        raise StripeException()
    except stripe.error.SignatureVerificationError:
        raise StripeException()

    if (
        event.type == "checkout.session.completed"
        or event.type == "checkout.session.async_payment_succeeded"
    ):
        _queue_purchase(event.data.object["id"])


def _queue_purchase(session_id: str):
    """
    Begin fulfilling a checkout session on successful payment,
    using an idempotent operation as required by Stripe.
    """
    checkout = Checkout(id=session_id)
    should_process = db.record_stripe_checkout(checkout)
    if not should_process:
        return

    queue.send({"id": checkout.id})


def _fulfill_checkout(checkout: Checkout):
    """
    Process a checkout order, updating the database with the new request,
    and sending it to Printful.
    """
    # Fetch the items purchased and the receipt link.
    session = stripe.checkout.Session.retrieve(
        checkout.id,
        expand=["line_items", "payment_intent.latest_charge"],
    )

    # Payment status can either be "paid" or "unpaid" or "not required",
    # see reference:
    # https://docs.stripe.com/api/checkout/sessions/object#checkout_session_object-payment_status
    if session.payment_status != "paid":
        return

    log.info(session.line_items.data)
    order = Order(
        email=session.customer_details.email,
        stripe_id=checkout.id,
        receipt_url=session.payment_intent.latest_charge.receipt_url,
        price=session.amount_total,
        items=[
            # TODO: Think about the items a little more.
        ],
    )

    order, created = db.create_order(order)
    if not created and order.printful_id is not None:
        # Order was already fully fulfilled on a previous attempt.
        return

    shipping = session.shipping_details
    recipient = PrintfulRecipient(
        name=shipping.name,
        address1=shipping.address.line1,
        address2=shipping.address.line2,
        city=shipping.address.city,
        state_code=shipping.address.state,
        country_code=shipping.address.country,
        zip=shipping.address.postal_code,
        email=session.customer_details.email,
    )
    items = [
        PrintfulItem(product_id=int(item.product_id), quantity=item.quantity)
        for item in order.items
    ]

    # Perform a lookup so we avoid creating duplicate errors if we already processed
    # this in a previous call.
    try:
        result = printful.get_order_by_external_id(order.id)
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            result = printful.create_order(
                recipient=recipient,
                items=items,
                external_id=checkout.id,
            )
        else:
            raise e

    printful_order = result["result"]
    db.update_order(
        order.id,
        printful_id=str(printful_order["id"]),
        status=PRINTFUL_STATUS_MAP.get(printful_order["status"], OrderStatus.pending),
    )
