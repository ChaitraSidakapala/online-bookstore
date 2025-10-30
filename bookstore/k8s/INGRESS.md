# Ingress Setup Guide

## Prerequisites

Before deploying the Ingress, you need an Ingress Controller installed in your Kubernetes cluster.

### For Docker Desktop Kubernetes

```bash
# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Wait for the ingress controller to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s
```

### For Minikube

```bash
# Enable ingress addon
minikube addons enable ingress

# Verify
kubectl get pods -n ingress-nginx
```

### For Kind

```bash
# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/kind/deploy.yaml

# Wait for it to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s
```

## Deploy Ingress

```bash
# Apply the ingress configuration
kubectl apply -f k8s/ingress.yaml

# Verify
kubectl get ingress -n bookstore
```

## Access the Application

### Option 1: Using localhost (No DNS)

```bash
# Get the ingress IP/port
kubectl get ingress -n bookstore

# Access services directly via localhost
# Catalog Service
curl http://localhost/catalog/books | jq '.'

# Order Service
curl http://localhost/orders/orders | jq '.'
```

### Option 2: Using Custom Domain (bookstore.local)

Add to `/etc/hosts`:

```bash
# For Docker Desktop / Minikube
echo "127.0.0.1 bookstore.local" | sudo tee -a /etc/hosts

# For Minikube (get IP first)
echo "$(minikube ip) bookstore.local" | sudo tee -a /etc/hosts
```

Then access:

```bash
# Catalog Service
curl http://bookstore.local/catalog/books | jq '.'

# Order Service
curl http://bookstore.local/orders/orders | jq '.'
```

### Option 3: Browser Access

Open in browser:
- Catalog API Docs: http://bookstore.local/catalog/docs
- Order API Docs: http://bookstore.local/orders/docs

Or with localhost:
- http://localhost/catalog/docs
- http://localhost/orders/docs

## API Endpoints via Ingress

### Catalog Service (via /catalog)

```bash
# List books
curl http://bookstore.local/catalog/books

# Get book
curl http://bookstore.local/catalog/books/1

# Create book
curl -X POST http://bookstore.local/catalog/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Book",
    "author": "Author Name",
    "price": 29.99,
    "quantity": 10
  }'

# Update book
curl -X PUT http://bookstore.local/catalog/books/1 \
  -H "Content-Type: application/json" \
  -d '{"price": 39.99}'

# Delete book
curl -X DELETE http://bookstore.local/catalog/books/11
```

### Order Service (via /orders)

```bash
# Place order
curl -X POST http://bookstore.local/orders/orders \
  -H "Content-Type: application/json" \
  -d '{
    "book_id": 1,
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "quantity": 2
  }'

# List orders
curl http://bookstore.local/orders/orders

# Get order
curl http://bookstore.local/orders/orders/1

# Update status
curl -X PATCH http://bookstore.local/orders/orders/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "confirmed"}'
```

## Path Routing

The Ingress routes requests based on URL paths:

- `/catalog/*` → Catalog Service
- `/orders/*` → Order Service

URL rewriting is handled automatically by the ingress controller.

## Troubleshooting

### Ingress Not Working

```bash
# Check ingress controller pods
kubectl get pods -n ingress-nginx

# Check ingress details
kubectl describe ingress bookstore-ingress -n bookstore

# Check ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller
```

### 404 Errors

Make sure paths include the service prefix:
- ❌ `http://localhost/books` (wrong)
- ✅ `http://localhost/catalog/books` (correct)

### Connection Refused

```bash
# For Minikube, create tunnel
minikube tunnel

# For Docker Desktop, ensure Kubernetes is enabled
kubectl cluster-info
```

## TLS/HTTPS (Optional)

To enable HTTPS with self-signed certificate:

```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout tls.key -out tls.crt \
  -subj "/CN=bookstore.local"

# Create TLS secret
kubectl create secret tls bookstore-tls \
  --cert=tls.crt --key=tls.key \
  -n bookstore

# Update ingress to use TLS (add to ingress.yaml):
# spec:
#   tls:
#   - hosts:
#     - bookstore.local
#     secretName: bookstore-tls
```

Then access via: https://bookstore.local/catalog/books
