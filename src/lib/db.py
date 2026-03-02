from datetime import datetime
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .types import Order, Shipment, StripeCheckout


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
    Update an order with the given fields, e.g. cost=100.
    """

    def update_order(self, order_id: int, **kwargs) -> Optional[Order]:
        with Session(self.engine) as session:
            order = session.get(Order, order_id)
            if order is None:
                return None
            # Automatically update updated_at so callers do not need to.
            kwargs["updated_at"] = datetime.now()
            for key, value in kwargs.items():
                setattr(order, key, value)
            session.commit()
            session.refresh(order)
            return order

    """
    Insert or update a new shipment for an order.
    """

    def upsert_shipment(self, shipment: Shipment) -> Shipment:
        with Session(self.engine) as session:
            shipment = session.merge(shipment)
            session.commit()
            session.refresh(shipment)
            return shipment

    """
    Write an order to the database, including its items.
    """

    def create_order(self, order: Order) -> Order:
        with Session(self.engine) as session:
            session.add(order)
            session.commit()
            session.refresh(order)
            return order

    def record_stripe_checkout(self, checkout: StripeCheckout) -> bool:
        """
        Attempts to record the checkout in the database, and returns
        whether we should process this checkout, as an "idempotency
        protection" requested by Stripe.
        """

        with Session(self.engine) as session:
            try:
                session.add(checkout)
                session.commit()
                return True
            except IntegrityError:
                # The checkout has already been processed.
                session.rollback()
                return False
