"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from decimal import Decimal


class OrderBase(BaseModel):
    """Base schema for order data."""
    book_id: int = Field(..., gt=0, description="ID of the book to order")
    customer_name: str = Field(..., min_length=1, max_length=255, description="Customer name")
    customer_email: EmailStr = Field(..., description="Customer email address")
    quantity: int = Field(..., gt=0, description="Number of books to order")


class OrderCreate(OrderBase):
    """Schema for creating a new order."""
    pass


class Order(OrderBase):
    """Schema for order response with all fields."""
    id: int
    book_title: str
    unit_price: Decimal
    total_price: Decimal
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderList(BaseModel):
    """Schema for list of orders response."""
    total: int
    orders: list[Order]


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status."""
    status: str = Field(..., pattern="^(pending|processing|confirmed|shipped|delivered|cancelled)$")


class Message(BaseModel):
    """Generic message response."""
    message: str


class BookAvailability(BaseModel):
    """Schema for book availability check from Catalog Service."""
    id: int
    title: str
    author: str
    price: Decimal
    quantity: int
    available: bool = True
