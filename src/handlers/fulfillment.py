import os

import requests
import stripe
from lib.stripe import get_api_key
from lib.types import Order, OrderStatus, StripeCheckout
from lib.db import Database
from lib.printful import PrintfulClient, PrintfulItem, PrintfulRecipient
from lib.logs import Logs

db = Database(url=os.getenv("DATABASE_URL"))
printful = PrintfulClient(api_key=os.getenv("PRINTFUL_API_KEY"))
log = Logs(log_group=os.environ["LOG_GROUP"])
stripe.api_key = get_api_key()

# Maps Printful order statuses to our internal OrderStatus. Statuses that
# indicate the order is in progress but not yet shipped (draft, inreview,
# pending, onhold, inprocess) all map to pending. canceled maps to failed
# since we have no canceled state.
_PRINTFUL_STATUS_MAP: dict[str, OrderStatus] = {
    "failed": OrderStatus.failed,
    "canceled": OrderStatus.failed,
    "partial": OrderStatus.partial,
    "fulfilled": OrderStatus.fulfilled,
}


def process_fulfillment(checkout: StripeCheckout):
    """
    Fulfills a successful checkout session.
    """
    # Fetch the items purchased and the receipt link.
    session = stripe.checkout.Session.retrieve(
        checkout.id,
        expand=["line_items", "payment_intent.latest_charge"],
    )

    if session.payment_status == "unpaid":
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

    # Check if a Printful order already exists for this checkout. This handles
    # the case where we crashed after calling Printful but before saving the
    # printful_id — we recover the existing order rather than creating a duplicate.
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
        status=_PRINTFUL_STATUS_MAP.get(printful_order["status"], OrderStatus.pending),
    )
