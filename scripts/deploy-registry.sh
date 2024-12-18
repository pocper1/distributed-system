#!/bin/bash

# 設置變數
PROJECT_ID="vivid-reality-443509-d4"
REGION="asia-east1"

# 映像名稱與儲存庫標籤
BACKEND_IMAGE="backend:latest"
FRONTEND_IMAGE="frontend:latest"

BACKEND_TAG="${REGION}-docker.pkg.dev/${PROJECT_ID}/backend-repo/backend:latest"
FRONTEND_TAG="${REGION}-docker.pkg.dev/${PROJECT_ID}/frontend-repo/frontend:latest"

# 構建 Backend 映像
echo "開始建置 Backend 映像..."
docker buildx build --platform linux/amd64 -t ${BACKEND_IMAGE} -f Dockerfiles/backend.Dockerfile ./Backend
if [ $? -ne 0 ]; then
    echo "❌ Backend 映像建置失敗！"
    exit 1
else
    echo "✅ Backend 映像建置完成！"
fi

# 構建 Frontend 映像
echo "開始建置 Frontend 映像..."
docker buildx build --platform linux/amd64 -t ${FRONTEND_IMAGE} -f Dockerfiles/frontend.Dockerfile ./Frontend
if [ $? -ne 0 ]; then
    echo "❌ Frontend 映像建置失敗！"
    exit 1
else
    echo "✅ Frontend 映像建置完成！"
fi

# 推送 Backend 映像
echo "推送 Backend 映像到 Artifact Registry..."
docker tag ${BACKEND_IMAGE} ${BACKEND_TAG}
docker push ${BACKEND_TAG}
if [ $? -ne 0 ]; then
    echo "❌ Backend 映像推送失敗！"
    exit 1
else
    echo "✅ Backend 映像推送完成！"
fi

# 推送 Frontend 映像
echo "推送 Frontend 映像到 Artifact Registry..."
docker tag ${FRONTEND_IMAGE} ${FRONTEND_TAG}
docker push ${FRONTEND_TAG}
if [ $? -ne 0 ]; then
    echo "❌ Frontend 映像推送失敗！"
    exit 1
else
    echo "✅ Frontend 映像推送完成！"
fi

# 部署 Backend 到 Cloud Run
echo "部署 Backend 到 Cloud Run..."
gcloud run deploy backend-service \
--image ${BACKEND_TAG} \
--platform managed \
--region ${REGION} \
--allow-unauthenticated
if [ $? -ne 0 ]; then
    echo "❌ Backend 部署失敗！"
    exit 1
else
    echo "✅ Backend 部署完成！"
fi

# 部署 Frontend 到 Cloud Run
echo "部署 Frontend 到 Cloud Run..."
gcloud run deploy frontend-service \
--image ${FRONTEND_TAG} \
--platform managed \
--region ${REGION} \
--allow-unauthenticated
if [ $? -ne 0 ]; then
    echo "❌ Frontend 部署失敗！"
    exit 1
else
    echo "✅ Frontend 部署完成！"
fi

echo "🎉 所有服務已成功部署到 Cloud Run！"