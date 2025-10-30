# 📚 Bookstore Microservices - Kubernetes Learning Project

A simple microservices-based bookstore application to learn Kubernetes basics.

## Project Overview

This is a cloud-native microservices-based Online Bookstore application built with Python and PostgreSQL. The application demonstrates modern software architecture principles including service independence, horizontal scalability, and containerized deployment using Kubernetes.

This is a learning project that demonstrates:
- **Microservices architecture** - Two separate services communicating with each other
- **Kubernetes deployment** - Running containers in a local Kubernetes cluster
- **Database integration** - PostgreSQL with persistent storage
- **Service communication** - How microservices talk to each other

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                      │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  Ingress Controller                  │   │
│  │            (External Access Entry Point)             │   │
│  └────────────┬─────────────────────┬───────────────────┘   │
│               │                     │                       
│  ┌────────────▼───────────┐  ┌─────▼──────────────────┐    │
│  │   Catalog Service      │  │   Order Service        │    │
│  │   (FastAPI)            │  │   (FastAPI)            │    │
│  │                        │  │                        │    │
│  │   - GET /books         │  │   - POST /orders       │    │
│  │   - POST /books        │  │   - GET /orders        │    │
│  │   - PUT /books/{id}    │  │   - GET /orders/{id}   │    │
│  │   - DELETE /books/{id} │  │                        │    │
│  │                        │  │   (Calls Catalog API)  │    │
│  │   Horizontally         │  │   Horizontally         │    │
│  │   Scalable             │  │   Scalable             │    │
│  └────────────┬───────────┘  └─────┬──────────────────┘    │
│               │                    │                        │
│               └────────┬───────────┘                        │
│                        │                                    │
│               ┌────────▼───────────┐                        │
│               │   PostgreSQL       │                        │
│               │   (StatefulSet)    │                        │
│               │                    │                        │
│               │   - Books Table    │                        │
│               │   - Orders Table   │                        │
│               │                    │                        │
│               │   Persistent       │                        │
│               │   Volume Storage   │                        │
│               └────────────────────┘                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Services:
1. **Catalog Service** - Manages books (list, add, update, delete)
2. **Order Service** - Handles customer orders
3. **PostgreSQL** - Stores all data

## 🚀 Quick Start

### Prerequisites

You need these installed:
- **Docker Desktop** (with Kubernetes enabled)
- **kubectl** command-line tool

### Step 1: Build Docker Images

```bash
# Build catalog service image
docker build -t catalog-service:latest catalog-service/

# Build order service image
docker build -t order-service:latest order-service/
```

### Step 2: Deploy to Kubernetes

```bash
# Deploy everything
./deploy.sh

# Wait for pods to start (1-2 minutes)
kubectl get pods -n bookstore -w
```

### Step 3: Access the Services

```bash
# Port-forward to access catalog service
kubectl port-forward -n bookstore svc/catalog-service 8000:8000

# In another terminal, test it
curl http://localhost:8000/books
```

Open in browser: http://localhost:8000/docs

## 📖 API Examples

### Catalog Service (Books)

```bash
# List all books
curl http://localhost:8000/books

# Get one book
curl http://localhost:8000/books/1

# Create a book
curl -X POST http://localhost:8000/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Kubernetes in Action",
    "author": "Marko Luksa",
    "isbn": "978-1617293726",
    "price": 44.99,
    "quantity": 10
  }'

# Update a book
curl -X PUT http://localhost:8000/books/1 \
  -H "Content-Type: application/json" \
  -d '{"price": 39.99}'

# Delete a book
curl -X DELETE http://localhost:8000/books/1
```

### Order Service

```bash
# Port-forward order service (in new terminal)
kubectl port-forward -n bookstore svc/order-service 8001:8000

# Create an order
curl -X POST http://localhost:8001/orders \
  -H "Content-Type: application/json" \
  -d '{
    "book_id": 1,
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "quantity": 2
  }'

# List orders
curl http://localhost:8001/orders
```

## 🗂️ Project Structure

```
playground/
├── catalog-service/          # Book management service
│   ├── app/
│   │   ├── main.py          # API endpoints
│   │   ├── models.py        # Database models
│   │   ├── crud.py          # Database operations
│   │   └── schemas.py       # Data validation
│   ├── Dockerfile
│   └── requirements.txt
│
├── order-service/            # Order management service
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── crud.py
│   │   └── schemas.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── k8s/                      # Kubernetes configuration files
│   ├── namespace.yaml       # Creates bookstore namespace
│   ├── postgres-*.yaml      # Database setup (7 files)
│   ├── catalog-*.yaml       # Catalog service deployment & HPA
│   ├── order-*.yaml         # Order service deployment & HPA
│   └── ingress.yaml         # Optional external access
│
├── deploy.sh                # Deployment script
├── cleanup.sh               # Cleanup script
├── ARCHITECTURE.md          # System architecture documentation
└── DEMO-GUIDE.md            # Presentation and demo guide
```

## 🔍 Useful Commands

```bash
# Check status
kubectl get all -n bookstore

# Check auto-scaling status
kubectl get hpa -n bookstore

# View logs
kubectl logs -n bookstore -l app=catalog-service
kubectl logs -n bookstore -l app=order-service

# Check database
kubectl exec -it postgres-0 -n bookstore -- psql -U bookstore -d bookstore

# Test auto-scaling with load
./load-test.sh

# Delete everything
./cleanup.sh
```

## 📈 Auto-Scaling Feature

This project includes **Horizontal Pod Autoscaler (HPA)** to demonstrate Kubernetes auto-scaling:

### How Auto-Scaling Works

```yaml
# Catalog Service: Scales 1-5 pods based on load
Min Replicas: 2
Max Replicas: 5
Target CPU: 70%
Target Memory: 80%

# Order Service: Scales 1-10 pods based on load
Min Replicas: 2
Max Replicas: 10
Target CPU: 70%
Target Memory: 80%
```

### View Auto-Scaling Status

```bash
# Check current HPA status
kubectl get hpa -n bookstore

# Watch HPA in real-time
kubectl get hpa -n bookstore -w

# See pod count
kubectl get pods -n bookstore
```

**Note**: Auto-scaling metrics require metrics-server to be installed in your Kubernetes cluster. Without it, HPA will show `<unknown>` for targets but the configuration is still active and will work once metrics-server is available.

## 🧪 What's Inside the Database?

The database comes pre-loaded with 10 sample books:
- Clean Code
- The Pragmatic Programmer
- Design Patterns
- And more...

You can see them with: `curl http://localhost:8000/books`

## 🎓 Learning Points

### Kubernetes Concepts:
- **Namespace**: Isolated environment for your app
- **Deployment**: Manages your application pods
- **Service**: Network endpoint for your app
- **StatefulSet**: For stateful apps like databases
- **PersistentVolume**: Storage that survives pod restarts
- **ConfigMap**: Configuration data
- **Secret**: Sensitive data (passwords)
- **Ingress**: External HTTP access
- **HPA (HorizontalPodAutoscaler)**: Auto-scales pods based on CPU/memory usage

### Microservices Concepts:
- **Service-to-service communication**: Order service calls Catalog service
- **Shared database** vs **Database per service**
- **REST APIs**: HTTP endpoints for CRUD operations
- **API documentation**: Auto-generated Swagger UI
- **Load balancing**: Traffic distributed across multiple pods
- **Auto-scaling**: Dynamic pod scaling based on demand

## 🛠️ Troubleshooting

### Pods not starting?

```bash
# Check pod status
kubectl get pods -n bookstore

# See what's wrong
kubectl describe pod <pod-name> -n bookstore

# Check logs
kubectl logs <pod-name> -n bookstore
```

### Can't access services?

Make sure you have port-forward running:
```bash
kubectl port-forward -n bookstore svc/catalog-service 8000:8000
```

### Need to rebuild?

```bash
# Cleanup first
./cleanup.sh

# Rebuild images
docker build -t catalog-service:latest catalog-service/
docker build -t order-service:latest order-service/

# Deploy again
./deploy.sh
```

## 📚 Next Steps

After getting this running, try:

1. **Check auto-scaling** - Run `kubectl get hpa -n bookstore` to see scaling configuration
2. **Modify the code** - Add new endpoints or features
3. **Scale manually** - `kubectl scale deployment catalog-service -n bookstore --replicas=3`
4. **Add monitoring** - Install metrics-server and watch HPA in action
5. **Read the docs** - Check:
   - `ARCHITECTURE.md` for system design details
   - `ADR.md` for architecture decisions and trade-offs
   - `DEMO-GUIDE.md` for presentation tips


## 📖 Technologies Used

- **Python 3.11** - Programming language
- **FastAPI** - Web framework
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Database
- **Docker** - Containerization
- **Kubernetes** - Orchestration
- **Uvicorn** - ASGI server

