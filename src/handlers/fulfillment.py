import os

import requests
import stripe
from lib.stripe import get_api_key
from lib.types import Order, OrderItem, OrderStatus, StripeCheckout
from lib.db import Database
from lib.printful import PrintfulClient, PrintfulItem, PrintfulRecipient

db = Database(url=os.getenv("DATABASE_URL"))
stripe.api_key = get_api_key()
printful = PrintfulClient(api_key=os.getenv("PRINTFUL_API_KEY"))


def process_fulfillment(checkout: StripeCheckout):
    """
    Fulfills a successful checkout session.
    """
    session = stripe.checkout.Session.retrieve(
        checkout.id,
        expand=["line_items", "payment_intent.latest_charge"],
    )

    if session.payment_status == "unpaid":
        return

    print(session.line_items.data)
    order = Order(
        email=session.customer_details.email,
        stripe_id=checkout.id,
        receipt_url=session.payment_intent.latest_charge.receipt_url,
        price=session.amount_total,
        items=[
            # TODO: Think about the items a little more.
        ],
    )

    created, order = db.create_order(order)
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
        result = printful.get_order_by_external_id(checkout.id)
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            result = printful.create_order(
                recipient=recipient,
                items=items,
                external_id=checkout.id,
            )
        else:
            raise e

    db.update_order(
        order.id,
        printful_id=str(result["result"]["id"]),
        status=OrderStatus.pending,
    )
