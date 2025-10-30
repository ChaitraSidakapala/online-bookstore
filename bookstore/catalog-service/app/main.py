"""Catalog Service - FastAPI Application."""
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from . import crud, models, schemas
from .database import engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Bookstore Catalog Service",
    description="Microservice for managing book catalog",
    version="1.0.0"
)


@app.get("/", response_model=schemas.Message)
def root():
    """Root endpoint - health check."""
    return {"message": "Catalog Service is running"}


@app.get("/health", response_model=schemas.Message)
def health_check():
    """Health check endpoint."""
    return {"message": "OK"}


@app.get("/books", response_model=schemas.BookList)
def list_books(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search by title, author, or ISBN"),
    db: Session = Depends(get_db)
):
    """
    List all books with optional search and pagination.
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    - **search**: Search term to filter books by title, author, or ISBN
    """
    books = crud.get_books(db, skip=skip, limit=limit, search=search)
    total = crud.get_books_count(db, search=search)
    return {"total": total, "books": books}


@app.get("/books/{book_id}", response_model=schemas.Book)
def get_book(book_id: int, db: Session = Depends(get_db)):
    """
    Get a specific book by ID.
    
    - **book_id**: The ID of the book to retrieve
    """
    db_book = crud.get_book(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@app.post("/books", response_model=schemas.Book, status_code=201)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    """
    Add a new book to the catalog.
    
    - **title**: Book title (required)
    - **author**: Book author (required)
    - **isbn**: ISBN number (optional, must be unique)
    - **price**: Book price (required, must be positive)
    - **quantity**: Available quantity (default: 0)
    - **description**: Book description (optional)
    """
    # Check if ISBN already exists
    if book.isbn:
        existing_book = crud.get_book_by_isbn(db, isbn=book.isbn)
        if existing_book:
            raise HTTPException(
                status_code=400,
                detail=f"Book with ISBN {book.isbn} already exists"
            )
    
    return crud.create_book(db=db, book=book)


@app.put("/books/{book_id}", response_model=schemas.Book)
def update_book(
    book_id: int,
    book_update: schemas.BookUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing book.
    
    - **book_id**: The ID of the book to update
    - All fields are optional - only provided fields will be updated
    """
    # Check if ISBN is being updated and already exists
    if book_update.isbn:
        existing_book = crud.get_book_by_isbn(db, isbn=book_update.isbn)
        if existing_book and existing_book.id != book_id:
            raise HTTPException(
                status_code=400,
                detail=f"Book with ISBN {book_update.isbn} already exists"
            )
    
    db_book = crud.update_book(db, book_id=book_id, book_update=book_update)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@app.delete("/books/{book_id}", response_model=schemas.Message)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """
    Delete a book from the catalog.
    
    - **book_id**: The ID of the book to delete
    """
    success = crud.delete_book(db, book_id=book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": f"Book {book_id} deleted successfully"}
