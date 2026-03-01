from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from .types import Order

class Database:
    def __init__(self, url: str):
        self.engine = create_engine(url)

    """
    Perform a lookup for a single order using our internal ID.
    """
    def get_order(self, order_id: int) -> Optional[Order]:
        with Session(self.engine) as session:
            return session.get(Order, order_id)

    """
    Write an order to the database, including its items.
    """
    def create_order(self, order: Order) -> Order:
        with Session(self.engine) as session:
            session.add(order)
            session.commit()
            session.refresh(order)
            return order
