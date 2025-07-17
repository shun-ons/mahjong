# **設計書: `routes.py`**

## **1. 概要 (Overview)**

このファイルは、Flaskアプリケーションにおける**エンドポイント（URL）を定義**する役割を担う。フロントエンドからのHTTPリクエストを受け取り、リクエスト内容に応じて適切な処理（AIモデルの呼び出し、点数計算の実行など）を呼び出し、最終的な結果をJSON形式でフロントエンドに返す。

-----

## **2. 依存関係 (Dependencies)**

| 種類 | モジュール / ライブラリ | 目的 |
| :--- | :--- | :--- |
| **外部** | `flask` | `request` (リクエスト情報), `jsonify` (JSON応答の作成) |
| **内部** | `app` | Flaskアプリケーションのインスタンス |
| **内部** | `models` | 牌検出を行うYOLOモデルのラッパー関数 |
| **内部** | `app.mahjong_logic` | 点数計算を行う `score_calculator` モジュール |

-----

## **3. エンドポイント定義 (API Specification)**

### **3.1. 点数計算API**

- **機能説明:** アップロードされた麻雀のあがり画像と対局情報から、点数を計算して返す。
- **URL:** `/api/calculate`
- **HTTPメソッド:** `POST`
- **リクエスト形式:** `multipart/form-data`
  - リクエストは、**画像ファイル**と**対局情報のJSON文字列**の2つのパートで構成される。

| キー | 型 | 必須 | 説明 |
| :--- | :--- | :--- | :--- |
| `image` | File | ✔️ | あがり形の画像ファイル (jpeg, pngなど) |
| `game_info` | String | ✔️ | 対局情報を格納したJSON文字列（下記「データ構造」参照） |

-----

### **3.2. 処理フロー (Processing Flow)**

1. `/api/calculate` への `POST` リクエストを受信する。
2. リクエストデータから `image` ファイルと `game_info` 文字列を抽出する。
3. **入力値検証:**
      - `image` と `game_info` が存在するか検証する。なければエラー (HTTP 400)。
      - `game_info` をJSONとして解析する。解析に失敗すればエラー (HTTP 400)。
4. **牌検出:**
      - `image` ファイルをメモリ上で開き、`models` の牌検出関数に渡す。
      - 検出された牌のリストを取得する。
5. **点数計算:**
      - 検出された牌リストと、`game_info` の内容を `app.mahjong_logic.score_calculator` に渡す。
      - 計算結果（役、符、飜、点数など）を受け取る。
6. **応答生成:**
      - 計算結果を「成功応答 (JSON)」の形式に整形する。
      - `jsonify` を用いてクライアントに応答を返す (HTTP 200)。
7. **例外処理:**
      - 処理中に予期せぬエラーが発生した場合、「エラー応答 (JSON)」を返す (HTTP 500)。

-----

## **4. データ構造 (Data Structures)**

### **4.1. リクエスト (`game_info` JSON)**

```json
{
  "is_tsumo": True,
  "is_oya": False,
  "is_reach": True,
  "dora_indicators": ["5m", "5p"],
  "ura_dora_indicators": ["6m", "6p"],
  "bakaze": "1z",
  "jikaze": "2z",
  "renchan": 0,
  "is_chankan": True,
  "is_haitei": False,
  "is_kaitei": True,
  "is_ippatsu": False,
  "is_riichi": True,
  "is_tenhou": False,
  "is_chiihou": False,
  "is_rinshan": False,
  }
```

### **4.2. 成功応答 (JSON)**

```json
{
  "status": "success",
  "data": {
    "hand": ["1m", "2m", "3m", "4p", "5p", "6p", "7s", "8s", "9s", "1z", "1z"],
    "yaku": ["立直", "平和", "ドラ1"],
    "han": 3,
    "fu": 30,
    "score_name": "子 3900点",
    "score": 3900
  }
}
```

### **4.3. エラー応答 (JSON)**

```json
{
  "status": "error",
  "message": "計算に必要な情報が不足しています。" // エラー内容に応じたメッセージ
}
```