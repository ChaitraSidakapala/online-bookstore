# Order Service

This is the Order microservice for the Online Bookstore application. It manages customer orders and communicates with the Catalog Service to verify book availability.

## Features

- **Create Order**: POST /orders (with book availability verification)
- **List Orders**: GET /orders with filtering by email and status
- **Get Order**: GET /orders/{id}
- **Update Status**: PATCH /orders/{id}/status
- **Get Book Details**: GET /orders/{id}/book (demonstrates inter-service communication)

## Technology Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- Uvicorn
- httpx (for HTTP client)

## Inter-Service Communication

The Order Service communicates with the Catalog Service via REST API to:
- Verify book existence
- Check book availability and stock
- Get current book pricing
- Fetch book details for orders

## Running Locally

### Prerequisites

- Python 3.11+
- PostgreSQL database
- Catalog Service running (for full functionality)

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://username:password@localhost:5432/bookstore"
export CATALOG_SERVICE_URL="http://localhost:8000"

# Run the service
uvicorn app.main:app --reload --port 8001
```

### API Documentation

Once running, visit:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Docker

### Build Image

```bash
docker build -t order-service:latest .
```

### Run Container

```bash
docker run -d \
  --name order-service \
  -p 8001:8000 \
  -e DATABASE_URL="postgresql://username:password@host:5432/bookstore" \
  -e CATALOG_SERVICE_URL="http://catalog-service:8000" \
  order-service:latest
```

## API Endpoints

### POST /orders

Create a new order with automatic book availability verification.

Request Body:
```json
{
  "book_id": 1,
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "quantity": 2
}
```

Response (201 Created):
```json
{
  "id": 1,
  "book_id": 1,
  "book_title": "Clean Code",
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "quantity": 2,
  "unit_price": 44.99,
  "total_price": 89.98,
  "status": "pending",
  "created_at": "2025-10-28T10:30:00",
  "updated_at": "2025-10-28T10:30:00"
}
```

Example:
```bash
curl -X POST "http://localhost:8001/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "book_id": 1,
    "customer_name": "Jane Smith",
    "customer_email": "jane@example.com",
    "quantity": 1
  }'
```

### GET /orders

List all orders with optional filtering.

Query Parameters:
- `skip` (int, default=0): Pagination offset
- `limit` (int, default=100): Maximum records
- `customer_email` (string, optional): Filter by customer
- `status` (string, optional): Filter by status

Example:
```bash
# All orders
curl "http://localhost:8001/orders"

# Filter by customer
curl "http://localhost:8001/orders?customer_email=john@example.com"

# Filter by status
curl "http://localhost:8001/orders?status=pending"
```

### GET /orders/{id}

Get order details and current status.

Example:
```bash
curl "http://localhost:8001/orders/1"
```

### PATCH /orders/{id}/status

Update order status.

Request Body:
```json
{
  "status": "confirmed"
}
```

Valid statuses: `pending`, `processing`, `confirmed`, `shipped`, `delivered`, `cancelled`

Example:
```bash
curl -X PATCH "http://localhost:8001/orders/1/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "confirmed"}'
```

### GET /orders/{id}/book

Get current book details from Catalog Service for an order.

This endpoint demonstrates inter-service communication.

Example:
```bash
curl "http://localhost:8001/orders/1/book"
```

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string (required)
  - Format: `postgresql://user:password@host:port/database`
  - Default: `postgresql://bookstore:bookstore123@localhost:5432/bookstore`

- `CATALOG_SERVICE_URL`: URL of the Catalog Service (required)
  - Format: `http://catalog-service:8000`
  - In Kubernetes: `http://catalog-service:8000`
  - Local development: `http://localhost:8000`

## Database Schema

The service uses the following database table:

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL,
    book_title VARCHAR(255) NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    customer_email VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    total_price NUMERIC(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Order Workflow

1. Customer submits order via POST /orders
2. Order Service calls Catalog Service to:
   - Verify book exists
   - Check available quantity
   - Get current price
3. If available, order is created with status "pending"
4. Order status can be updated through lifecycle:
   - pending → processing → confirmed → shipped → delivered
   - Can be cancelled at any stage

## Error Handling

The service handles various error scenarios:

- **Book not found**: Returns 400 with message "Book with ID X not found"
- **Insufficient stock**: Returns 400 with available quantity
- **Catalog service unavailable**: Returns 400 with timeout message
- **Invalid order ID**: Returns 404
- **Invalid status**: Returns 422 validation error

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

## Service Dependencies

- **Catalog Service**: Required for order placement
  - Used to verify book availability
  - Used to fetch current pricing
  - Used to get book details
