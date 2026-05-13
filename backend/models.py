from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    trailer_line = Column(String, nullable=True)  # Silverstar, Pacesetter, etc.
    unit_cost = Column(Float, nullable=False, default=0.0)
    stock = Column(Integer, nullable=False, default=0)
    min_stock = Column(Integer, nullable=False, default=5)
    location = Column(String, nullable=True)
    supplier = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String, unique=True, index=True, nullable=False)
    vendor = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="received")  # ordered, received, partial
    total = Column(Float, nullable=False, default=0.0)
    notes = Column(Text, nullable=True)

    items = relationship("PurchaseItem", back_populates="purchase", cascade="all, delete-orphan")


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Float, nullable=False)
    line_total = Column(Float, nullable=False)

    purchase = relationship("Purchase", back_populates="items")
    product = relationship("Product")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    category = Column(String, nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    paid_to = Column(String, nullable=True)
    notes = Column(Text, nullable=True)


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    product_id = Column(Integer, ForeignKey("products.id"))
    movement_type = Column(String, nullable=False)  # IN, OUT, ADJUST
    quantity = Column(Integer, nullable=False)
    reason = Column(String, nullable=True)
    reference = Column(String, nullable=True)  # PO #, work order #, etc.

    product = relationship("Product")
