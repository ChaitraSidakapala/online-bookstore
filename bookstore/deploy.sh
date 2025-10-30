#!/bin/bash

# Simple deployment script for Bookstore Kubernetes project

echo "======================================"
echo "  Bookstore Deployment"
echo "======================================"
echo ""

# Create namespace
echo "Creating namespace..."
kubectl apply -f k8s/namespace.yaml

# Create secrets
echo "Creating secrets..."
kubectl apply -f k8s/postgres-secret.yaml

# Create storage
echo "Creating storage..."
kubectl apply -f k8s/postgres-pv.yaml
kubectl apply -f k8s/postgres-pvc.yaml

# Create ConfigMap
echo "Creating database init script..."
kubectl apply -f k8s/postgres-configmap.yaml

# Deploy PostgreSQL
echo "Deploying PostgreSQL..."
kubectl apply -f k8s/postgres-service.yaml
kubectl apply -f k8s/postgres-statefulset.yaml

# Wait for PostgreSQL
echo "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod/postgres-0 -n bookstore --timeout=90s

# Deploy Catalog Service
echo "Deploying Catalog Service..."
kubectl apply -f k8s/catalog-deployment.yaml
kubectl apply -f k8s/catalog-service.yaml

# Deploy Order Service
echo "Deploying Order Service..."
kubectl apply -f k8s/order-deployment.yaml
kubectl apply -f k8s/order-service.yaml

# Deploy Ingress (optional)
echo "Deploying Ingress..."
kubectl apply -f k8s/ingress.yaml

# Deploy HPA (Horizontal Pod Autoscaler)
echo "Deploying HPA for auto-scaling..."
kubectl apply -f k8s/catalog-hpa.yaml
kubectl apply -f k8s/order-hpa.yaml

echo ""
echo "======================================"
echo "  Deployment Complete!"
echo "======================================"
echo ""
echo "Check status with:"
echo "  kubectl get pods -n bookstore"
echo "  kubectl get hpa -n bookstore"
echo ""
echo "Access services:"
echo "  kubectl port-forward -n bookstore svc/catalog-service 8000:8000"
echo "  kubectl port-forward -n bookstore svc/order-service 8001:8000"
echo ""
