# backend/app/routes.py
"""
Flaskアプリケーションのエンドポイントを定義する。

このモジュールは、フロントエンドからのHTTPリクエストを受け付け、
適切なサービス（牌認識、点数計算）を呼び出し、
最終的な結果をJSON形式でクライアントに返却する。
"""


# --- モジュールのインポート ---
# 標準モジュールのインポート
import json
import traceback

from flask import Blueprint, jsonify, request
from flask.wrappers import Response

# 依存モジュールのインポート
# mahjong_logicsパッケージから各モジュールをインポート
from .mahjong_logic.helpers import Call
from .mahjong_logic.scorer import MahjongScorer

# servicesパッケージからモジュールをインポート
from .services.recognition_service import (NoTilesDetectedError,
                                            detect_tiles)


# --- Blueprintの作成 ---
api = Blueprint('api', __name__)


# --- エンドポイント（URL）の定義 ---
@api.route('/calculate', methods=['POST'])
def calculate_score_endpoint() -> tuple[Response, int]:
    """
    /api/calculateエンドポイント。

    フロントエンドからのリクエストを受け取り、点数計算結果を返す。
    画像ファイルと対局情報(JSON文字列)を元に、牌認識と点数計算を実行する。

    リクエスト形式: multipart/form-data
        - key 'image': 画像ファイル
        - key 'game_info': 対局情報を格納したJSON文字列

    Returns:
        FlaskのResponseオブジェクトとHTTPステータスコードのタプル。
    """
    # 3. 入力値検証
    if 'image' not in request.files:
        err_msg = "「画像ファイル」がリクエストに含まれていません。"
        return jsonify({"status": "error", "message": err_msg}), 400

    if 'game_info' not in request.form:
        err_msg = "「対局情報」がリクエストに含まれていません。"
        return jsonify({"status": "error", "message": err_msg}), 400

    image_file = request.files['image']
    game_info_str = request.form['game_info']

    if not image_file or image_file.filename == '':
        err_msg = "画像ファイルが選択されていません。"
        return jsonify({"status": "error", "message": err_msg}), 400

    try:
        # JSON文字列の解析
        try:
            game_info = json.loads(game_info_str)
        except json.JSONDecodeError:
            err_msg = "対局情報のJSON形式が正しくありません。"
            return jsonify({"status": "error", "message": err_msg}), 400

        # 4. 牌検出
        try:
            image_data = image_file.read()
            hand_list = detect_tiles(image_data)
        except NoTilesDetectedError as e:
            # 牌が検出できなかった場合
            return jsonify({"status": "error", "message": str(e)}), 400
        except ValueError as e:
            # 画像データが不正な場合
            return jsonify({"status": "error", "message": str(e)}), 400

        # 5. 点数計算
        called_mentsu_list_data = game_info.get('called_mentsu_list', [])
        called_mentsu_list = [Call(m['type'], m['tiles']) for m in called_mentsu_list_data]

        scorer = MahjongScorer(
            hand=hand_list,
            called_mentsu_list=called_mentsu_list,
            **game_info
        )
        score_data = scorer.calculate()

        if 'error' in score_data:
            return jsonify({"status": "error", "message": score_data['error']}), 400

        # 6. 応答生成
        final_score = score_data.get("score", {}).get("total", 0)
        full_hand = sorted(hand_list + sum([called_mentsu.tiles for called_mentsu in called_mentsu_list], []))
        yaku_list = list(score_data.get("yaku", {}).keys())

        response_data = {
            "status": "success",
            "data": {
                "hand": full_hand,
                "yaku": yaku_list,
                "han": score_data.get("han", 0),
                "fu": score_data.get("fu", 0),
                "score_name": score_data.get("score_name", ""),
                "score": final_score,
            },
        }
        return jsonify(response_data), 200

    except Exception as e:
        # 7. 例外処理
        print(f"予期せぬエラーが発生しました: {e}")
        traceback.print_exc()
        err_msg = "サーバー内部でエラーが発生しました。"
        return jsonify({"status": "error", "message": err_msg}), 500