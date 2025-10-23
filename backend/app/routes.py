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
from .mahjong_logic.helpers import Call, Tile
from .mahjong_logic.scorer import MahjongScorer
# servicesパッケージからモジュールをインポート
from .services.recognition_service import (NoTilesDetectedError, detect_tiles)


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
    try:
        if request.is_json:
            json_data = request.get_json()
            if not json_data or 'game_info' not in json_data:
                err_msg = "「対局情報」がリクエストに含まれていません。"
                return jsonify({"status": "error", "message": err_msg}), 400
            game_info = json_data['game_info']
            if 'hand' not in game_info:
                err_msg = "「手牌」が対局情報に含まれていません。"
                return jsonify({"status": "error", "message": err_msg}), 400
            hand_list = game_info['hand']
        else:
            print("step1 ok")
            # 3. 入力値検証
            if 'image' not in request.files:
                err_msg = "「画像ファイル」がリクエストに含まれていません。"
                return jsonify({"status": "error", "message": err_msg}), 400

            if 'game_info' not in request.form:
                err_msg = "「対局情報」がリクエストに含まれていません。"
                return jsonify({"status": "error", "message": err_msg}), 400
            
            print('step2 ok')

            image_file = request.files['image']
            game_info_str = request.form['game_info']

            if not image_file or image_file.filename == '':
                err_msg = "画像ファイルが選択されていません。"
                return jsonify({"status": "error", "message": err_msg}), 400
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
                print(hand_list)
                
                # テスト用の仮リスト.
                # hand_list = ["1m","2m","3m","2p","3p","4p","5s","6s","7s","1z","1z","1z", "5z", "5z"]
            except NoTilesDetectedError as e:
                # 牌が検出できなかった場合
                return jsonify({"status": "error", "message": str(e)}), 400
            except ValueError as e:
                # 画像データが不正な場合
                return jsonify({"status": "error", "message": str(e)}), 400

        # 5. 点数計算
        called_mentsu_list_data = game_info.get('called_mentsu_list', [])
        called_mentsu_list = [Call(m['type'], m['tiles'].split(',')) for m in called_mentsu_list_data]

        game_info.pop('hand', None)
        scorer = MahjongScorer(
            hand=hand_list,
            called_mentsu=called_mentsu_list,
            **game_info
        )
        score_data = scorer.calculate()

        if 'error' in score_data:
            return jsonify({"status": "error", "message": score_data['error'], "hand": sorted(hand_list, key=Tile.sort_key)}), 400

        # 6. 応答生成
        # final_score = score_data.get("score", {}).get("total", 0)
        # full_hand = sorted(hand_list + sum([called_mentsu.tiles for called_mentsu in called_mentsu_list], []))
        yaku_list = list(score_data.get("yaku", {}).keys())

        print([m.tiles for m in called_mentsu_list])
        response_data = {
            "status": "success",
            "data": {
                "hand": sorted(hand_list, key=Tile.sort_key),
                "yaku": yaku_list,
                "han": score_data.get("han", 0),
                "fu": score_data.get("fu", 0),
                "score_name": score_data.get("score_name", ""),
                "called_mentsu": [m.tiles for m in called_mentsu_list]
            },
        }
        for key, value in score_data.get("score", {}).items():
            response_data["data"][key] = value
            
        print(response_data)  # デバッグ用
        return jsonify(response_data), 200

    except Exception as e:
        # 7. 例外処理
        print(f"予期せぬエラーが発生しました: {e}")
        traceback.print_exc()
        err_msg = "サーバー内部でエラーが発生しました。"
        return jsonify({"status": "error", "message": err_msg}), 500