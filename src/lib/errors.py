class HttpError(Exception):
    """
    This wraps an HTTP error, such as a 404 or 400, or similar,
    such that we can return it to the caller.
    """

    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message


class StripeException(Exception):
    """
    This error type stands for an error processing a
    Stripe webhook, for instance due to an invalid
    "signature," or similar.
    """

    pass


class OrderNotFoundException(Exception):
    """
    This error defines an order that is "not found,"
    even if we expect it to be present.
    """

    pass
