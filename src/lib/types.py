"""
Order, OrderStatus, and OrderItem match the types defined in schema.sql. This is
manually defined, and in a "production" environment with heavier types, using an
autogeneration tool would be better.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class OrderStatus(str, Enum):
    failed = "failed"
    pending = "pending"
    partial = "partial"
    fulfilled = "fulfilled"


class OrderItem(Base):
    __tablename__ = "order_items"

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), primary_key=True)
    product_id: Mapped[str] = mapped_column(primary_key=True)
    quantity: Mapped[int] = mapped_column(default=1)


class Shipment(Base):
    __tablename__ = "shipments"

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), primary_key=True)
    shipment_id: Mapped[int] = mapped_column(primary_key=True)
    tracking_url: Mapped[Optional[str]]


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    status: Mapped[Optional[OrderStatus]] = mapped_column(default=None)
    stripe_id: Mapped[str] = mapped_column(unique=True)
    printful_id: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now)
    receipt_url: Mapped[str]
    tracking_url: Mapped[Optional[str]]
    price: Mapped[int]
    cost: Mapped[Optional[int]]
    items: Mapped[list[OrderItem]] = relationship()
    shipments: Mapped[list[Shipment]] = relationship()


class StripeCheckout(Base):
    __tablename__ = "stripe_checkouts"

    id: Mapped[str] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
