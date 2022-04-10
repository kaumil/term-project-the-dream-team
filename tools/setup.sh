#!/usr/bin/env bash
#
# Instantiate the setup of eks and deploy a stack on aws
# This script creates the iniial namespace and all the necessary setup

echo "Creating the context and namespace..."
kubectl config use-context aws756marketplace
kubectl create ns c756marketplacens
kubectl config set-context aws756marketplace --namespace=c756marketplacens

echo "Switching the context and installing istio..."
kubectl config use-context aws756marketplace
istioctl install -y --set profile=demo --set hub=gcr.io/istio-release
kubectl label namespace c756marketplacens istio-injection=enabled

echo "Building images with cri..."
make -f k8s.mak cri

echo "Deploying the services..."
make -f k8s.mak provision