# Catalog Service

This is the Catalog microservice for the Online Bookstore application. It manages the book catalog with full CRUD operations.

## Features

- **List Books**: GET /books with search and pagination
- **Get Book**: GET /books/{id}
- **Create Book**: POST /books
- **Update Book**: PUT /books/{id}
- **Delete Book**: DELETE /books/{id}

## Technology Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- Uvicorn

## Running Locally

### Prerequisites

- Python 3.11+
- PostgreSQL database

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variable for database
export DATABASE_URL="postgresql://username:password@localhost:5432/bookstore"

# Run the service
uvicorn app.main:app --reload --port 8000
```

### API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Docker

### Build Image

```bash
docker build -t catalog-service:latest .
```

### Run Container

```bash
docker run -d \
  --name catalog-service \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://username:password@host:5432/bookstore" \
  catalog-service:latest
```

## API Endpoints

### GET /books

List all books with optional filtering and pagination.

Query Parameters:
- `skip` (int, default=0): Number of records to skip
- `limit` (int, default=100): Maximum records to return
- `search` (string, optional): Search by title, author, or ISBN

Example:
```bash
curl "http://localhost:8000/books?search=python&limit=10"
```

### GET /books/{id}

Get a specific book by ID.

Example:
```bash
curl "http://localhost:8000/books/1"
```

### POST /books

Create a new book.

Request Body:
```json
{
  "title": "The Pragmatic Programmer",
  "author": "Andrew Hunt and David Thomas",
  "isbn": "9780135957059",
  "price": 49.99,
  "quantity": 10,
  "description": "A guide to pragmatic programming"
}
```

Example:
```bash
curl -X POST "http://localhost:8000/books" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "isbn": "9780132350884",
    "price": 44.99,
    "quantity": 5,
    "description": "A Handbook of Agile Software Craftsmanship"
  }'
```

### PUT /books/{id}

Update an existing book. All fields are optional.

Example:
```bash
curl -X PUT "http://localhost:8000/books/1" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 39.99,
    "quantity": 15
  }'
```

### DELETE /books/{id}

Delete a book from the catalog.

Example:
```bash
curl -X DELETE "http://localhost:8000/books/1"
```

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string (required)
  - Format: `postgresql://user:password@host:port/database`
  - Default: `postgresql://bookstore:bookstore123@localhost:5432/bookstore`

## Database Schema

The service uses the following database table:

```sql
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    isbn VARCHAR(13) UNIQUE,
    price NUMERIC(10, 2) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Development

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black app/
```

### Linting

```bash
flake8 app/
```
