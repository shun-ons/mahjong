#!/bin/bash

# --- スクリプトの設定 ---
# スクリプトがエラーで停止した場合、そこで終了する
set -e

# サービス名とポート
BACKEND_IMAGE="mahjong-backend"
BACKEND_NAME="backend_container"
BACKEND_PORT=8000 # run.py で実行するポートに合わせてください

FRONTEND_IMAGE="mahjong-frontend"
FRONTEND_NAME="frontend_container"
FRONTEND_PORT=8080

# --- Dockerコンテナの実行 ---
echo "Starting backend container ($BACKEND_NAME)..."
docker run -d \
    -p ${BACKEND_PORT}:${BACKEND_PORT} \
    --name $BACKEND_NAME \
    $BACKEND_IMAGE

echo "Starting frontend container ($FRONTEND_NAME)..."
docker run -d \
    -p ${FRONTEND_PORT}:80 \
    --name $FRONTEND_NAME \
    $FRONTEND_IMAGE

echo "------------------------------------------"
echo "✅ Docker containers are up and running!"
echo "Backend:  http://localhost:$BACKEND_PORT"
echo "Frontend: http://localhost:$FRONTEND_PORT"
echo "------------------------------------------"