"""SQLAlchemy models for the order service."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from .database import Base


class Order(Base):
    """Order model representing a customer order."""
    
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, nullable=False, index=True)
    book_title = Column(String(255), nullable=False)  # Denormalized for easier access
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), nullable=False, default='pending', index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Order(id={self.id}, book_id={self.book_id}, customer='{self.customer_name}', status='{self.status}')>"
