#!/bin/bash
kubectl autoscale deployment backend-deployment --cpu-percent=50 --min=3 --max=10
