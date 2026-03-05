import os


def get_api_key() -> str:
    return os.environ["STRIPE_API_KEY"]


def get_endpoint_secret() -> str:
    os.environ["STRIPE_WEBHOOK_ENDPOINT_SECRET"]
