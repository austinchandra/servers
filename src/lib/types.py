"""
Order, OrderStatus, and OrderItem match the types defined in schema.sql
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class OrderStatus(str, Enum):
    pending = "pending"
    placed = "placed"
    fulfilled = "fulfilled"
    shipped = "shipped"
    delivered = "delivered"

class OrderItem(Base):
    __tablename__ = "order_items"

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), primary_key=True)
    product_id: Mapped[str] = mapped_column(primary_key=True)
    quantity: Mapped[int] = mapped_column(default=1)

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    status: Mapped[OrderStatus] = mapped_column(default=OrderStatus.pending)
    stripe_id: Mapped[str] = mapped_column(unique=True)
    printful_id: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now)
    receipt_url: Mapped[str]
    tracking_url: Mapped[Optional[str]]
    price: Mapped[int]
    cost: Mapped[Optional[int]]
    items: Mapped[list[OrderItem]] = relationship()
