#!/bin/bash

gcloud functions deploy calculate_score \
    --runtime python310 \
    --trigger-topic score-updates \
    --set-env-vars DATABASE_URL=<DB_URL>,REDIS_IP=<REDIS_IP>
