#!/bin/bash

# Simple cleanup script

echo "This will delete all bookstore resources from Kubernetes."
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo "Deleting bookstore namespace..."
kubectl delete namespace bookstore

echo "Deleting persistent volume..."
kubectl delete pv postgres-pv

echo "Done!"
