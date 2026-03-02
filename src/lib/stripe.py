import os


class MissingEnvironmentVariable(Exception):
    """
    A required environment variable was not found.
    """

    def __init__(self, name: str, *args):
        super().__init__(f"{name} not found in environment", *args)


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
    key = os.environ.get("STRIPE_API_KEY")
    if key is None:
        raise Exception("`STRIPE_API_KEY` not found in environment")

    return key


def get_endpoint_secret() -> str:
    endpoint_secret = os.environ.get("STRIPE_WEBHOOK_ENDPOINT_SECRET")
    if endpoint_secret is None:
        raise Exception("`STRIPE_WEBHOOK_ENDPOINT_SECRET` not found in environment")

    return endpoint_secret
