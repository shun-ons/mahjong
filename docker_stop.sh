#!/bin/bash

# --- スクリプトの設定 ---
# スクリプトがエラーで停止した場合、そこで終了する
set -e

# サービス名とポート
BACKEND_IMAGE="mahjong-backend"
BACKEND_NAME="backend_container"

FRONTEND_IMAGE="mahjong-frontend"
FRONTEND_NAME="frontend_container"

docker stop $BACKEND_NAME || true
docker rm $BACKEND_NAME || true
docker stop $FRONTEND_NAME || true
docker rm $FRONTEND_NAME || true