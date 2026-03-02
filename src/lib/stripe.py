import os


class InvalidPayload(Exception):
    """
    The payload contained in a Webhook request was invalid.
    """

    pass


class SignatureVerificationFailed(Exception):
    """
    The Webhook's signature was invalid.
    """

    pass


def get_api_key() -> str:
    return os.environ["STRIPE_API_KEY"]


def get_endpoint_secret() -> str:
    os.environ["STRIPE_WEBHOOK_ENDPOINT_SECRET"]
