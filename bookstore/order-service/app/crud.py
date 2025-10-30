"""CRUD operations for orders."""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from decimal import Decimal
from . import models, schemas


def get_order(db: Session, order_id: int) -> Optional[models.Order]:
    """Get a single order by ID."""
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def get_orders(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    customer_email: Optional[str] = None,
    status: Optional[str] = None
) -> list[models.Order]:
    """Get all orders with optional filtering."""
    query = db.query(models.Order)
    
    if customer_email:
        query = query.filter(models.Order.customer_email == customer_email)
    
    if status:
        query = query.filter(models.Order.status == status)
    
    return query.order_by(desc(models.Order.created_at)).offset(skip).limit(limit).all()


def get_orders_count(
    db: Session,
    customer_email: Optional[str] = None,
    status: Optional[str] = None
) -> int:
    """Get total count of orders."""
    query = db.query(models.Order)
    
    if customer_email:
        query = query.filter(models.Order.customer_email == customer_email)
    
    if status:
        query = query.filter(models.Order.status == status)
    
    return query.count()


def create_order(
    db: Session,
    book_id: int,
    book_title: str,
    customer_name: str,
    customer_email: str,
    quantity: int,
    unit_price: Decimal
) -> models.Order:
    """Create a new order."""
    total_price = unit_price * quantity
    
    db_order = models.Order(
        book_id=book_id,
        book_title=book_title,
        customer_name=customer_name,
        customer_email=customer_email,
        quantity=quantity,
        unit_price=unit_price,
        total_price=total_price,
        status='pending'
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def update_order_status(
    db: Session,
    order_id: int,
    status: str
) -> Optional[models.Order]:
    """Update order status."""
    db_order = get_order(db, order_id)
    if not db_order:
        return None
    
    db_order.status = status
    db.commit()
    db.refresh(db_order)
    return db_order


def delete_order(db: Session, order_id: int) -> bool:
    """Delete an order (for testing/admin purposes)."""
    db_order = get_order(db, order_id)
    if not db_order:
        return False
    
    db.delete(db_order)
    db.commit()
    return True
