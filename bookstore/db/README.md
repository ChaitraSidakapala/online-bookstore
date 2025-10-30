# PostgreSQL Database Documentation

## Overview

This directory contains the PostgreSQL database configuration and initialization scripts for the Online Bookstore application.

## Database Schema

### Books Table

Stores the catalog of available books.

```sql
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    isbn VARCHAR(13) UNIQUE,
    price NUMERIC(10, 2) NOT NULL CHECK (price > 0),
    quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:**
- Primary key on `id`
- Index on `title`
- Index on `author`
- Unique index on `isbn`

### Orders Table

Stores customer orders.

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL,
    book_title VARCHAR(255) NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    customer_email VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price > 0),
    total_price NUMERIC(10, 2) NOT NULL CHECK (total_price > 0),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_book FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE RESTRICT
);
```

**Indexes:**
- Primary key on `id`
- Index on `book_id`
- Index on `customer_email`
- Index on `status`
- Index on `created_at` (descending)

**Foreign Key:**
- `book_id` references `books(id)` with RESTRICT on delete

## Sample Data

The initialization script includes 10 sample books covering various programming and technology topics:

1. Clean Code - Robert C. Martin
2. The Pragmatic Programmer - Andrew Hunt and David Thomas
3. Design Patterns - Gang of Four
4. Refactoring - Martin Fowler
5. Introduction to Algorithms - Thomas H. Cormen
6. Python Crash Course - Eric Matthes
7. JavaScript: The Good Parts - Douglas Crockford
8. Head First Design Patterns - Eric Freeman
9. The DevOps Handbook - Gene Kim
10. Kubernetes in Action - Marko Luksa

## Automatic Triggers

**Update Timestamp Trigger:**

Both tables have triggers that automatically update the `updated_at` timestamp whenever a record is modified:

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';
```

## Database Credentials

**Note:** In production, these should be managed more securely!

- **Database Name:** bookstore
- **Username:** bookstore
- **Password:** bookstore123
- **Port:** 5432

## Connection String

```
postgresql://bookstore:bookstore123@postgres-service:5432/bookstore
```

## Manual Database Operations

### Connect to Database (from within Kubernetes)

```bash
# Get the pod name
kubectl get pods -n bookstore -l app=postgres

# Connect to PostgreSQL
kubectl exec -it postgres-0 -n bookstore -- psql -U bookstore -d bookstore
```

### Common SQL Queries

```sql
-- List all books
SELECT * FROM books;

-- List all orders
SELECT * FROM orders;

-- Get orders with book details
SELECT o.id, o.book_title, o.customer_name, o.quantity, o.total_price, o.status
FROM orders o
JOIN books b ON o.book_id = b.id;

-- Check inventory
SELECT title, author, quantity FROM books ORDER BY quantity DESC;

-- Get pending orders
SELECT * FROM orders WHERE status = 'pending';
```

## Data Persistence

Data is stored in a PersistentVolume mounted at `/var/lib/postgresql/data/pgdata` inside the container.

This ensures data survives:
- Pod restarts
- Container crashes
- Kubernetes cluster restarts (if volume is properly configured)

## Backup and Restore

### Backup

```bash
# Create backup
kubectl exec postgres-0 -n bookstore -- pg_dump -U bookstore bookstore > backup.sql
```

### Restore

```bash
# Restore from backup
kubectl exec -i postgres-0 -n bookstore -- psql -U bookstore -d bookstore < backup.sql
```

## Performance Considerations

- Indexes are created on frequently queried columns
- Foreign key constraints ensure referential integrity
- Connection pooling should be implemented in application services
- For production: consider read replicas for scaling

## Security Notes

⚠️ **Important for Production:**

1. Change default passwords
2. Use Kubernetes Secrets (already implemented)
3. Enable SSL/TLS connections
4. Implement network policies
5. Regular backups
6. Monitor access logs
7. Apply principle of least privilege

## Monitoring

Check database health:

```bash
# Check if database is ready
kubectl exec postgres-0 -n bookstore -- pg_isready -U bookstore

# Check database size
kubectl exec postgres-0 -n bookstore -- psql -U bookstore -d bookstore -c "\l+"

# Check table sizes
kubectl exec postgres-0 -n bookstore -- psql -U bookstore -d bookstore -c "\dt+"

# Check active connections
kubectl exec postgres-0 -n bookstore -- psql -U bookstore -d bookstore -c "SELECT * FROM pg_stat_activity;"
```
