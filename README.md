# Deploying the Queue App on K3s

This guide explains how to set up a single-node K3s cluster and deploy the Queue app.

## Prerequisites

- A Linux machine with at least 2GB of RAM.
- Docker installed on the machine.

## Step 1: Install K3s

1. Run the following command to install K3s:
   ```bash
   curl -sfL https://get.k3s.io | sh -
   ```

2. Verify that K3s is running:
   ```bash
   sudo kubectl get nodes
   ```

## Step 2: Build and Push Docker Images

1. Build the Docker image for the FastAPI app:
   ```bash
   docker build -t queue-api:latest .
   ```

2. Save the image to a tar file:
   ```bash
   docker save queue-api:latest -o queue-api.tar
   ```

3. Load the image into the K3s cluster:
   ```bash
   sudo k3s ctr images import queue-api.tar
   ```

## Step 3: Deploy the App

1. Apply the Kubernetes manifests:
   ```bash
   kubectl apply -f .k8s/deployment.yaml
   kubectl apply -f .k8s/service.yaml
   ```

2. Verify the deployments:
   ```bash
   kubectl get pods
   ```

3. Verify the services:
   ```bash
   kubectl get services
   ```

## Step 4: Access the App

1. Find the NodePort for the `queue-api` service:
   ```bash
   kubectl get service queue-api
   ```

2. Access the app in your browser using `http://<node-ip>:<node-port>`.

## Cleanup

To remove the app and K3s, run:
```bash
kubectl delete -f .k8s/
sudo /usr/local/bin/k3s-uninstall.sh
```
