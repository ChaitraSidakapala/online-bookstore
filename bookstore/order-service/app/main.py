"""Order Service - FastAPI Application."""
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal

from . import crud, models, schemas
from .database import engine, get_db
from .catalog_client import catalog_client

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Bookstore Order Service",
    description="Microservice for managing customer orders",
    version="1.0.0"
)


@app.get("/", response_model=schemas.Message)
def root():
    """Root endpoint - health check."""
    return {"message": "Order Service is running"}


@app.get("/health", response_model=schemas.Message)
def health_check():
    """Health check endpoint."""
    return {"message": "OK"}


@app.post("/orders", response_model=schemas.Order, status_code=201)
async def create_order(
    order_data: schemas.OrderCreate,
    db: Session = Depends(get_db)
):
    """
    Place a new order.
    
    This endpoint:
    1. Validates the book exists in the catalog
    2. Checks if sufficient quantity is available
    3. Creates the order with current pricing
    
    - **book_id**: ID of the book to order (required)
    - **customer_name**: Name of the customer (required)
    - **customer_email**: Email of the customer (required)
    - **quantity**: Number of books to order (required, must be > 0)
    """
    # Check book availability via Catalog Service
    is_available, book_data, error_msg = await catalog_client.check_availability(
        order_data.book_id,
        order_data.quantity
    )
    
    if not is_available:
        raise HTTPException(
            status_code=400,
            detail=error_msg or "Book is not available"
        )
    
    # Extract book details
    book_title = book_data['title']
    unit_price = Decimal(str(book_data['price']))
    
    # Create the order
    db_order = crud.create_order(
        db=db,
        book_id=order_data.book_id,
        book_title=book_title,
        customer_name=order_data.customer_name,
        customer_email=order_data.customer_email,
        quantity=order_data.quantity,
        unit_price=unit_price
    )
    
    # Optional: Update inventory in catalog service (future enhancement)
    # For now, we just verify availability but don't decrement stock
    # This can be implemented later with proper transaction handling
    
    return db_order


@app.get("/orders", response_model=schemas.OrderList)
def list_orders(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    customer_email: Optional[str] = Query(None, description="Filter by customer email"),
    status: Optional[str] = Query(None, description="Filter by order status"),
    db: Session = Depends(get_db)
):
    """
    List all orders with optional filtering and pagination.
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    - **customer_email**: Filter orders by customer email
    - **status**: Filter orders by status (pending, processing, confirmed, shipped, delivered, cancelled)
    """
    orders = crud.get_orders(
        db,
        skip=skip,
        limit=limit,
        customer_email=customer_email,
        status=status
    )
    total = crud.get_orders_count(
        db,
        customer_email=customer_email,
        status=status
    )
    return {"total": total, "orders": orders}


@app.get("/orders/{order_id}", response_model=schemas.Order)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """
    Get order details and status.
    
    - **order_id**: The ID of the order to retrieve
    """
    db_order = crud.get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order


@app.patch("/orders/{order_id}/status", response_model=schemas.Order)
def update_order_status(
    order_id: int,
    status_update: schemas.OrderStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    Update order status.
    
    - **order_id**: The ID of the order to update
    - **status**: New status (pending, processing, confirmed, shipped, delivered, cancelled)
    """
    db_order = crud.update_order_status(
        db,
        order_id=order_id,
        status=status_update.status
    )
    
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return db_order


@app.get("/orders/{order_id}/book", response_model=schemas.BookAvailability)
async def get_order_book_details(order_id: int, db: Session = Depends(get_db)):
    """
    Get current book details for an order (from Catalog Service).
    
    This demonstrates inter-service communication.
    
    - **order_id**: The ID of the order
    """
    db_order = crud.get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Fetch current book details from Catalog Service
    book_data = await catalog_client.get_book(db_order.book_id)
    
    if book_data is None:
        raise HTTPException(
            status_code=404,
            detail=f"Book {db_order.book_id} no longer exists in catalog"
        )
    
    return {
        "id": book_data['id'],
        "title": book_data['title'],
        "author": book_data['author'],
        "price": book_data['price'],
        "quantity": book_data['quantity'],
        "available": book_data['quantity'] > 0
    }
