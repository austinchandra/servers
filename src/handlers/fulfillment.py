import stripe
from lib.stripe import get_api_key
from lib.types import StripeCheckout


stripe.api_key = get_api_key()


def process_fulfillment(checkout: StripeCheckout):
    """
    Fulfills a successful checkout session.
    """

    # TODO: Make sure fulfillment hasn't already been
    # performed for this checkout.

    session = stripe.checkout.Session.retrieve(
        checkout.id,
        expand=["line_items"],
    )

    if session.payment_status == "unpaid":
        return

    # TODO: Perform fulfillment of the line items
    # TODO: Record/save fulfillment status for this
    pass
