import stripe
from lib.stripe import get_api_key
from lib.types import CheckoutSession


stripe.api_key = get_api_key()


def process_fulfillment(session: CheckoutSession):
    """
    Fulfills a successful checkout session.
    """

    # TODO: Make sure fulfillment hasn't already been
    # performed for this Checkout Session

    session = stripe.checkout.Session.retrieve(
        session.id,
        expand=["line_items"],
    )

    if session.payment_status == "unpaid":
        return

    # TODO: Perform fulfillment of the line items
    # TODO: Record/save fulfillment status for this
    pass
