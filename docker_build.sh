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

# --- 古いコンテナの停止と削除 ---
# 以前のコンテナが残っているとポートが競合するため、先に停止・削除します
echo "Stopping and removing old containers..."
docker stop $BACKEND_NAME || true
docker rm $BACKEND_NAME || true
docker stop $FRONTEND_NAME || true
docker rm $FRONTEND_NAME || true

# --- Dockerイメージのビルド ---
echo "Building backend image ($BACKEND_IMAGE)..."
docker build -t $BACKEND_IMAGE -f Dockerfile .

echo "Building frontend image ($FRONTEND_IMAGE)..."
docker build -t $FRONTEND_IMAGE -f frontend/Dockerfile.frontend .