#!/bin/bash
# 進入後端目錄
cd backend
docker build -t gcr.io/<project-id>/backend .
docker push gcr.io/<project-id>/backend

# 進入前端目錄
cd frontend
docker build -t gcr.io/<project-id>/frontend .
docker push gcr.io/<project-id>/frontend
