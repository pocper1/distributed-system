#!/bin/bash
gcloud container clusters create marketing-cluster --num-nodes=3

kubectl create deployment backend --image=gcr.io/<project-id>/backend
kubectl create deployment frontend --image=gcr.io/<project-id>/frontend

kubectl expose deployment backend --type=LoadBalancer --port=8000
kubectl expose deployment frontend --type=LoadBalancer --port=3000
