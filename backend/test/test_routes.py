import io
import json
import pytest
from flask import Flask
from unittest.mock import MagicMock

# --- テスト対象のBlueprintをインポート ---
# 親ディレクトリ(app)にあるroutes.pyからapi (Blueprint)をインポートするためにパスを追加
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.routes import api

@pytest.fixture
def client():
    """Pytestのfixture機能を使って、テスト用のFlaskアプリとクライアントを準備する"""
    app = Flask(__name__)
    app.register_blueprint(api, url_prefix='/api') # Blueprintを登録
    with app.test_client() as client:
        yield client

def test_calculate_score_success(client, mocker):
    """正常なリクエストが来た場合のテスト（成功ケース）"""
    # --- 1. 依存機能のモックを作成 ---
    
    # detect_tiles関数をモック化し、固定の牌リストを返すように設定
    mocker.patch(
        'app.routes.detect_tiles', 
        return_value=["1m", "2m", "3m", "4p", "5p", "6p", "7s", "8s", "9s", "1z", "1z"]
    )
    
    # MahjongScorerクラスをモック化
    mock_scorer_instance = MagicMock()
    # calculateメソッドが呼ばれたら、固定の辞書を返すように設定
    mock_scorer_instance.calculate.return_value = {
        "yaku": {"リーチ": 1, "平和": 1},
        "han": 2,
        "fu": 30,
        "score_name": "子 2000点",
        "score": {"total": 2000},
    }
    mocker.patch('app.routes.MahjongScorer', return_value=mock_scorer_instance)

    # --- 2. テスト用のリクエストデータを作成 ---
    
    # ダミーの画像データ
    dummy_image = (io.BytesIO(b"dummy image data"), 'test.jpg')
    # ダミーの対局情報
    game_info = {
        "is_tsumo": True,
        "is_oya": False,
        # ... 他の必要な情報
    }
    
    data = {
        'image': dummy_image,
        'game_info': json.dumps(game_info) # JSON文字列に変換
    }

    # --- 3. テストクライアントでPOSTリクエストを送信 ---
    
    response = client.post('/api/calculate', data=data, content_type='multipart/form-data')
    
    # --- 4. 結果を検証 (assert) ---
    
    # ステータスコードが200 (OK) であることを確認
    assert response.status_code == 200
    
    # レスポンスがJSON形式であることを確認
    assert response.content_type == 'application/json'
    
    # レスポンスのJSONデータを取得
    response_data = response.get_json()
    
    # レスポンスの内容が期待通りであることを確認
    assert response_data['status'] == 'success'
    assert response_data['data']['han'] == 2
    assert response_data['data']['fu'] == 30
    assert response_data['data']['score'] == 2000
    assert "リーチ" in response_data['data']['yaku']


def test_calculate_score_missing_image(client):
    """画像ファイルがリクエストに含まれていない場合のテスト（失敗ケース）"""
    # --- 1. テスト用のリクエストデータを作成 ---
    game_info = {"is_oya": False}
    data = {
        'game_info': json.dumps(game_info)
        # 'image'キーを意図的に含めない
    }
    
    # --- 2. POSTリクエストを送信 ---
    response = client.post('/api/calculate', data=data, content_type='multipart/form-data')
    
    # --- 3. 結果を検証 ---
    
    # ステータスコードが400 (Bad Request) であることを確認
    assert response.status_code == 400
    
    response_data = response.get_json()
    assert response_data['status'] == 'error'
    assert '「画像ファイル」がリクエストに含まれていません' in response_data['message']