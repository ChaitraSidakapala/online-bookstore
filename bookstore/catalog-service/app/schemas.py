"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal


class BookBase(BaseModel):
    """Base schema for book data."""
    title: str = Field(..., min_length=1, max_length=255, description="Book title")
    author: str = Field(..., min_length=1, max_length=255, description="Book author")
    isbn: Optional[str] = Field(None, min_length=10, max_length=13, description="ISBN number")
    price: Decimal = Field(..., gt=0, description="Book price")
    quantity: int = Field(default=0, ge=0, description="Available quantity")
    description: Optional[str] = Field(None, description="Book description")


class BookCreate(BookBase):
    """Schema for creating a new book."""
    pass


class BookUpdate(BaseModel):
    """Schema for updating an existing book."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    isbn: Optional[str] = Field(None, min_length=10, max_length=13)
    price: Optional[Decimal] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None


class Book(BookBase):
    """Schema for book response with all fields."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BookList(BaseModel):
    """Schema for list of books response."""
    total: int
    books: list[Book]


class Message(BaseModel):
    """Generic message response."""
    message: str
