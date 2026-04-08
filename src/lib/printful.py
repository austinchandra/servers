from dataclasses import asdict, dataclass
from typing import Optional
import requests

from lib.types import OrderStatus

# Store the Printful order states, using "pending" as a default when we are not
# interested in performing any custom logic.
PRINTFUL_STATUS = {
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

    def json(self):
        """
        Converts the native Python object to a dictionary for the purposes of
        performing a JSON request.
        """
        return {"sync_variant_id": self.product_id, "quantity": self.quantity}


@dataclass
class PrintfulRecipient:
    name: str
    address1: str
    address2: Optional[str] = None
    city: str
    country_code: str
    zip_code: str
    state_code: Optional[str] = None
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
                "items": [item.json() for item in items],
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
