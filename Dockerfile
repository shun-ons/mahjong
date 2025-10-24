# Pythonベースイメージの指定.
FROM python:3.12-slim

# 作業中の不要な警告を抑制.
ENV PIP_ROOT_USER_ACTION=ignore

# pipのアップグレード.
RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

# コンテナの作業ディレクトリ.
WORKDIR /app

# 依存関係のインストール.
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー.
COPY backend/app/ ./app
COPY backend/run.py .
COPY ml/ ./ml

# 実行コマンド.
CMD ["python3", "run.py"]