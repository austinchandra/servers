from dataclasses import asdict, dataclass
from typing import Optional
import requests

from lib.types import OrderStatus

# Capture the states of an order from Printful, and for some of these, such as "onhold,"
# we prefer to deal with them in the application-level, rather than persist such states
# to the database.
PRINTFUL_STATUS_MAP = {
    "pending": OrderStatus.pending,
    "inprocess": OrderStatus.pending,
    "onhold": OrderStatus.pending,
    "inreview": OrderStatus.pending,
    "fulfilled": OrderStatus.fulfilled,
    "failed": OrderStatus.failed,
}


@dataclass
class PrintfulItem:
    product_id: int
    quantity: int

    def to_dict(self):
        return {"sync_variant_id": self.product_id, "quantity": self.quantity}


@dataclass
class PrintfulRecipient:
    name: str
    address1: str
    city: str
    country_code: str
    zip: str
    state_code: Optional[str] = None
    address2: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class PrintfulClient:
    BASE_URL = "https://api.printful.com"

    def __init__(self, api_key: str):
        """
        Create a new client prepared to include the bearer token in each request.
        """
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        )

    def _request(self, method, endpoint, **kwargs):
        """
        Send the desired request with a method, such as "POST", the
        endpoint, and a set of parameters, typically json={}.
        """
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    def create_order(
        self, recipient: PrintfulRecipient, items: list[PrintfulItem], external_id: str
    ):
        """
        Send a request to create an order, given a list of items and an order ID.
        """
        # Set confirm to true to place the order in one step,
        # rather than to stage it in a draft.
        return self._request(
            "POST",
            "/orders?confirm=true",
            json={
                "external_id": external_id,
                "recipient": asdict(recipient),
                "items": [item.to_dict() for item in items],
            },
        )

    def get_order(self, order_id: int):
        """
        Send a request to get the order with `order_id`.
        """
        return self._request("GET", f"/orders/{order_id}")

    def get_order_by_external_id(self, external_id: str):
        """
        Send a request to get the order with `external_id`.
        """
        return self._request("GET", f"/orders/@{external_id}")
