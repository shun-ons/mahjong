# mahjong

## 使用技術一覧

<img src="https://img.shields.io/badge/-Vue.js-4FC08D.svg?logo=vue.js&style=plastic">
<img src="https://img.shields.io/badge/-Python-3776AB.svg?logo=python&style=plastic">
<img src="https://img.shields.io/badge/-Ubuntu-E95420.svg?logo=ubuntu&style=plastic">



## 目次

1. [プロジェクトについて](#プロジェクトについて)
2. [開発環境](#開発環境)
3. [実行方法](#実行方法)
4. [トラブルシューティング](#トラブルシューティング)

## プロジェクトについて
黒い麻雀牌の和了牌の画像から得点を計算するプログラムです。
画像認識にはYOLOを用いています。

## 開発環境
- **CPU:** 12th Gen Intel(R) Core(TM) i5-12400
- **GPU:** NVIDIA GeForce RTX 3060
- **Memory:** 16GB RAM
- **OS:** Ubuntu 24.04.3 LTS
- **CUDA version:** 13.0

PythonとVueで使用するライブラリ等は[requrements.txt](backend/requirements.txt)を参照してください。

## 実行方法
- Dockerのビルド方法
```sh
chmod +x docker_build.sh # 初回のみ.
sh docker_build.sh
```

- アプリケーションの起動方法
```sh
chmod +x run.sh  # 初回のみ.
sh run.sh
```

- アプリケーションの終了方法
```sh
docker stop backend_container frontend_container
```

## トラブルシューティング
現在作成中.
運用中に不具合が生じた場合,ここに対策法を記述します.
