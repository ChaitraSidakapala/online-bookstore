# Software Architecture Design

## Overview

This document describes the software architecture of the Online Bookstore application, detailing the role of each component, their responsibilities, and the architectural principles used to create a cohesive, cloud-native system.

## System Components

### 1. Catalog Service (Microservice)

**Type**: Stateless REST API Service

**Responsibilities**:
- Manage the complete lifecycle of book data (Create, Read, Update, Delete)
- Provide RESTful endpoints for book operations
- Validate incoming book data
- Interact with PostgreSQL database for book persistence
- Handle concurrent requests independently

**Technology Stack**:
- FastAPI (Web Framework)
- SQLAlchemy (ORM)
- Pydantic (Data Validation)
- Uvicorn (ASGI Server)

**API Endpoints**:
- `GET /books` - List/search books with optional filters
- `GET /books/{id}` - Get a specific book by ID
- `POST /books` - Add a new book to the catalog
- `PUT /books/{id}` - Update an existing book
- `DELETE /books/{id}` - Remove a book from the catalog

**Scalability**: Horizontally scalable - multiple replicas can run simultaneously

---

### 2. Order Service (Microservice)

**Type**: Stateless REST API Service

**Responsibilities**:
- Manage customer orders
- Validate order requests
- Verify book availability by communicating with Catalog Service
- Persist order data to PostgreSQL database
- Provide order status information

**Technology Stack**:
- FastAPI (Web Framework)
- SQLAlchemy (ORM)
- Pydantic (Data Validation)
- httpx (HTTP Client for inter-service communication)
- Uvicorn (ASGI Server)

**API Endpoints**:
- `POST /orders` - Place a new order
- `GET /orders` - List all orders
- `GET /orders/{id}` - Get order details and status

**Inter-Service Communication**:
- Uses HTTP REST calls to Catalog Service to verify book availability
- Uses Kubernetes DNS for service discovery (catalog-service.bookstore.svc.cluster.local)

**Scalability**: Horizontally scalable - multiple replicas can run simultaneously

---

### 3. PostgreSQL Database (Microservice)

**Type**: Stateful Database Service

**Responsibilities**:
- Persist book catalog data
- Persist order data
- Provide ACID transactions
- Maintain data integrity through constraints and relationships

**Database Schema**:

**Books Table**:
```sql
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    isbn VARCHAR(13) UNIQUE,
    price DECIMAL(10, 2) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Orders Table**:
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    customer_email VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id)
);
```

**Deployment Strategy**:
- Kubernetes StatefulSet for stable network identity
- PersistentVolume and PersistentVolumeClaim for data durability
- Single replica (not horizontally scalable per requirements)

---

## Architecture Principles & Patterns

### 1. Microservices Architecture

**Principle**: Decompose the application into small, independent services that can be developed, deployed, and scaled separately.

**Implementation**:
- Catalog Service handles only book-related operations
- Order Service handles only order-related operations
- Each service has its own codebase and can be updated independently

**Benefits**:
- Independent development and deployment
- Technology flexibility
- Fault isolation
- Easier to understand and maintain

---

### 2. API-First Design

**Principle**: All services expose well-defined REST APIs for communication.

**Implementation**:
- FastAPI provides automatic OpenAPI documentation
- Standardized HTTP methods (GET, POST, PUT, DELETE)
- JSON for data exchange
- Pydantic schemas for request/response validation

**Benefits**:
- Clear contracts between services
- Easy to test and document
- Language-agnostic integration

---

### 3. Service Discovery

**Principle**: Services should be able to find and communicate with each other dynamically.

**Implementation**:
- Kubernetes DNS provides automatic service discovery
- Services reference each other by name (e.g., `http://catalog-service:8000`)
- No hardcoded IP addresses

**Benefits**:
- Dynamic service location
- Automatic load balancing
- Resilience to pod restarts

---

### 4. Stateless Services

**Principle**: Application services should not store session state locally.

**Implementation**:
- Catalog and Order services are completely stateless
- All state is stored in the PostgreSQL database
- Any replica can handle any request

**Benefits**:
- Horizontal scalability
- Simple load balancing
- Easy recovery from failures

---

### 5. Persistent Storage Pattern

**Principle**: Separate stateful and stateless components.

**Implementation**:
- PostgreSQL deployed as StatefulSet with persistent volumes
- Application services are stateless and ephemeral
- Data survives pod restarts and cluster changes

**Benefits**:
- Data durability
- Independent scaling of compute and storage
- Simplified application logic

---

### 6. Configuration Externalization

**Principle**: Configuration should be external to the application code.

**Implementation**:
- Environment variables for database connections
- Kubernetes ConfigMaps for application settings
- Kubernetes Secrets for sensitive data (passwords, API keys)

**Benefits**:
- Same container image across environments
- Secure credential management
- Easy configuration updates without redeployment

---

### 7. API Gateway Pattern (Ingress)

**Principle**: Single entry point for external clients.

**Implementation**:
- Kubernetes Ingress controller routes traffic to services
- Path-based routing (/catalog/*, /orders/*)
- Optional TLS termination

**Benefits**:
- Centralized access control
- SSL/TLS offloading
- Simplified client configuration

---

## Component-to-Microservice Mapping

| Software Component | Microservice Implementation | Kubernetes Resource |
|-------------------|---------------------------|---------------------|
| Book Catalog Management | Catalog Service | Deployment + Service |
| Order Management | Order Service | Deployment + Service |
| Data Persistence | PostgreSQL Database | StatefulSet + Service + PV/PVC |
| External Access | Ingress Controller | Ingress |
| Service Discovery | Kubernetes DNS | Built-in |
| Configuration | ConfigMaps & Secrets | ConfigMap + Secret |

---

## Data Flow Examples

### Example 1: Adding a Book to Catalog

```
Client → Ingress → Catalog Service → PostgreSQL
                      ↓
                   Validate
                      ↓
                 Insert Book
                      ↓
                Return Success
```

### Example 2: Placing an Order

```
Client → Ingress → Order Service → Catalog Service (Check Availability)
                      ↓                     ↓
                   Validate           Query Book
                      ↓                     ↓
              Check Availability      Return Book Data
                      ↓
              Create Order → PostgreSQL
                      ↓
             Return Order Confirmation
```

---

## Scalability Strategy

### Horizontal Scaling

**Catalog Service**:
- Can scale from 1 to N replicas
- Kubernetes Service provides round-robin load balancing
- Each replica can handle requests independently

**Order Service**:
- Can scale from 1 to N replicas
- Independent scaling from Catalog Service
- Handles traffic spikes during high-demand periods

**Database**:
- Single replica (as per requirements)
- Future: Could implement read replicas for read scaling

### Scaling Commands

```bash
# Scale Catalog Service
kubectl scale deployment catalog-service --replicas=3

# Scale Order Service
kubectl scale deployment order-service --replicas=5
```

---

## Network Communication

### Internal (Service-to-Service)
- Catalog Service ← Order Service: HTTP REST API
- Services ← → PostgreSQL: PostgreSQL protocol (port 5432)
- Uses Kubernetes internal DNS

### External (Client-to-Service)
- Client → Ingress Controller → Services
- HTTP/HTTPS protocol
- Public IP or LoadBalancer

---

## Security Architecture

### Current Security Measures:
1. Database credentials stored in Kubernetes Secrets
2. Internal network isolation via Kubernetes networking
3. No direct external access to database

### Planned Security Enhancements:
1. API authentication (JWT or API keys)
2. TLS/HTTPS for Ingress
3. Network policies to restrict traffic
4. Role-Based Access Control (RBAC)
5. Input validation and sanitization

---

## Benefits of This Architecture

1. **Independent Scalability**: Each service can scale based on its own load
2. **Fault Isolation**: Failure in one service doesn't crash the entire system
3. **Development Velocity**: Teams can work on services independently
4. **Technology Flexibility**: Can use different tech stacks for different services
5. **Easier Testing**: Services can be tested in isolation
6. **Cloud-Native**: Designed to leverage Kubernetes features
7. **Maintainability**: Smaller codebases are easier to understand

---

## Challenges and Mitigations

### Challenge 1: Distributed System Complexity

**Issue**: Multiple services increase operational complexity

**Mitigation**:
- Use Kubernetes for automated deployment and management
- Implement comprehensive logging and monitoring
- Use service mesh (future enhancement) for observability

### Challenge 2: Network Latency

**Issue**: Inter-service communication adds network overhead

**Mitigation**:
- Services deployed in same cluster minimize latency
- Use connection pooling for database
- Cache frequently accessed data (future enhancement)

### Challenge 3: Data Consistency

**Issue**: Distributed data requires careful transaction management

**Mitigation**:
- Use database transactions for critical operations
- Implement eventual consistency patterns where appropriate
- Order Service validates with Catalog Service before creating orders

### Challenge 4: Security

**Issue**: Multiple entry points increase attack surface

**Mitigation**:
- Centralize external access through Ingress
- Use Kubernetes Secrets for sensitive data
- Implement API authentication for production use
- Apply network policies to restrict traffic

### Challenge 5: Debugging and Troubleshooting

**Issue**: Harder to trace requests across multiple services

**Mitigation**:
- Implement structured logging with correlation IDs
- Use distributed tracing (future enhancement)
- Centralized log aggregation (future enhancement)

---

## Future Enhancements

1. **Service Mesh** (Istio/Linkerd): Advanced traffic management and security
2. **Message Queue**: Asynchronous communication for order processing
3. **Caching Layer** (Redis): Improve read performance
4. **API Rate Limiting**: Protect services from abuse
5. **Health Checks**: Liveness and readiness probes
6. **Monitoring**: Prometheus + Grafana for metrics
7. **CI/CD Pipeline**: Automated testing and deployment
8. **Database Replication**: Read replicas for better performance

---

This architecture provides a solid foundation for a scalable, maintainable, cloud-native application while keeping the implementation scope manageable for this project.
