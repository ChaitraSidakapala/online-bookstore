"""CRUD operations for books."""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from . import models, schemas


def get_book(db: Session, book_id: int) -> Optional[models.Book]:
    """Get a single book by ID."""
    return db.query(models.Book).filter(models.Book.id == book_id).first()


def get_book_by_isbn(db: Session, isbn: str) -> Optional[models.Book]:
    """Get a book by ISBN."""
    return db.query(models.Book).filter(models.Book.isbn == isbn).first()


def get_books(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
) -> list[models.Book]:
    """Get all books with optional search."""
    query = db.query(models.Book)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                models.Book.title.ilike(search_pattern),
                models.Book.author.ilike(search_pattern),
                models.Book.isbn.ilike(search_pattern)
            )
        )
    
    return query.offset(skip).limit(limit).all()


def get_books_count(db: Session, search: Optional[str] = None) -> int:
    """Get total count of books."""
    query = db.query(models.Book)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                models.Book.title.ilike(search_pattern),
                models.Book.author.ilike(search_pattern),
                models.Book.isbn.ilike(search_pattern)
            )
        )
    
    return query.count()


def create_book(db: Session, book: schemas.BookCreate) -> models.Book:
    """Create a new book."""
    db_book = models.Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def update_book(
    db: Session,
    book_id: int,
    book_update: schemas.BookUpdate
) -> Optional[models.Book]:
    """Update an existing book."""
    db_book = get_book(db, book_id)
    if not db_book:
        return None
    
    update_data = book_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_book, field, value)
    
    db.commit()
    db.refresh(db_book)
    return db_book


def delete_book(db: Session, book_id: int) -> bool:
    """Delete a book."""
    db_book = get_book(db, book_id)
    if not db_book:
        return False
    
    db.delete(db_book)
    db.commit()
    return True
