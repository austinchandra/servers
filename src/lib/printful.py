from dataclasses import asdict, dataclass
from typing import Optional
import requests

@dataclass
class PrintfulItem:
    sync_variant_id: int
    quantity: int

    def to_dict(self):
        return {
            "sync_variant_id": self.sync_variant_id,
            "quantity": self.quantity
        }

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
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })

    def _request(self, method, endpoint, **kwargs):
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    def create_order(self, recipient: PrintfulRecipient, items: list[PrintfulItem], external_id: str):
        return self._request("POST", "/orders?confirm=true", json={
            "external_id": external_id,
            "recipient": asdict(recipient),
            "items": [item.to_dict() for item in items]
        })

    def get_order(self, order_id: int):
        return self._request("GET", f"/orders/{order_id}")