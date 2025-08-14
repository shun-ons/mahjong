# backend/app/services/recognition_service.py
"""
このモジュールは、アップロードされた画像から麻雀牌を検出し、
その種類を特定する機能（YOLOモデルの呼び出しなど）を提供する。
"""


# --- モジュールのインポート ---
import io
import traceback
from typing import List
import numpy as np
from PIL import Image, UnidentifiedImageError


# --- カスタム例外の定義 ---
class NoTilesDetectedError(Exception):
    """画像から信頼できる牌が一つも検出できなかった場合に送出される例外処理。"""
    pass


# --- 定数定義 ---
# モデルが認識するクラス（牌の種類）のリスト
TILE_CLASS_MAP: List[str] = [
    # 萬子 (0-8)
    '1m', '2m', '3m', '4m', '5m', '6m', '7m', '8m', '9m',
    # 筒子 (9-17)
    '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p',
    # 索子 (18-26)
    '1s', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s',
    # 字牌 (27-33)
    '1z', '2z', '3z', '4z', '5z', '6z', '7z'
    # 赤ドラを区別する場合は、ここに追加する (例: '5mr', '5pr', '5sr')
]

# 信頼度の閾値
CONFIDENCE_THRESHOLD = 0.5


def detect_tiles(image_data: bytes) -> List[str]:
    """
    アップロードされた画像ファイルから麻雀牌を認識し、含まれる牌を文字列リストとして返す。

    Args:
        image_data: 画像ファイルのバイナリデータ。

    Returns:
        検出された牌の文字列リスト。例: ['1m', '1m', '2p']

    Raises:
        ValueError: 画像データとして認識できない不正なデータが渡された場合。
        NoTilesDetectedError: 画像は正常だが、牌が一つも検出できなかった場合。
    """
    # 1. モデル読み込み
    # 実際には、ここで学習済みモデルをロードする
    # model = torch.load(...)

    # 3. 画像変換
    try:
        pil_image = Image.open(io.BytesIO(image_data)).convert('RGB')
        cv_image = np.array(pil_image)
    except UnidentifiedImageError:
        raise ValueError("提供されたデータは有効な画像形式ではありません。")

    # 4. 推論実行 - この部分はダミーです
    # 実際には、推論を実行する
    # results = model(cv_image)
    print("牌認識処理を実行します... (YOLOダミー)")
    dummy_predictions = [
        # (x1, y1, x2, y2, confidence, class_id)
        (100, 150, 150, 230, 0.95, 27),  # 1z
        (160, 150, 210, 230, 0.92, 27),  # 1z
        (220, 150, 270, 230, 0.45, 27),  # 1z (信頼度が低いため破棄される)
        (280, 150, 330, 230, 0.98, 9),   # 1p
        (340, 150, 390, 230, 0.91, 10),  # 2p
    ]

    # 5,6,7. 結果解析と形式変換、リスト生成
    recognized_tiles: List[str] = []
    # 実際には、以下のfor文を使用
    # for *box, conf, cls_id in results.xyxy[0].tolist():
    for *box, conf, cls_id in dummy_predictions:
        if conf > CONFIDENCE_THRESHOLD:
            try:
                tile_name = TILE_CLASS_MAP[int(cls_id)]
                recognized_tiles.append(tile_name)
            except IndexError:
                # モデルが予期しないクラスIDを返した場合の安全策
                print(f"警告: 不明なクラスID {int(cls_id)} が検出されました。")
                continue

    # 8. 返却
    if not recognized_tiles:
        raise NoTilesDetectedError("画像から牌を検出できませんでした。")

    return recognized_tiles

