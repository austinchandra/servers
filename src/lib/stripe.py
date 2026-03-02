import os


class StripeException(Exception):
    """
    An unknown exception occurred within
    the Stripe webhook.
    """

    pass


def get_api_key() -> str:
    return os.environ["STRIPE_API_KEY"]


def get_endpoint_secret() -> str:
    os.environ["STRIPE_WEBHOOK_ENDPOINT_SECRET"]
