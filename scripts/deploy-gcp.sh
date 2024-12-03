#!/bin/bash

# frontend
gcloud run deploy frontend-service \
    --image gcr.io/<YOUR_PROJECT_ID>/frontend-image \
    --platform managed \
    --allow-unauthenticated \
    --region <REGION>

# backend

gcloud run deploy backend-service \
    --image gcr.io/<YOUR_PROJECT_ID>/backend-image \
    --platform managed \
    --allow-unauthenticated \
    --region <REGION>
