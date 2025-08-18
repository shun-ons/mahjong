"""
YOLOモデルを用いて指定された単一の画像から麻雀牌を検出し、
検出結果とセグメンテーションマスクを描画した画像を保存する。

検出結果は牌の文字列と信頼度のタプルのリストとして取得できます。
"""

import os
from pprint import pprint
from typing import Dict, List, Tuple

import cv2
import numpy as np
from ultralytics import YOLO

# --- 定数定義 ---
MODEL_PATH: str = "runs/detect/mahjong_train/weights/best.pt"
CONFIDENCE_THRESHOLD: float = 0.5
# ↓↓↓ 処理したい単一の画像ファイルのパスを指定してください ↓↓↓
TARGET_IMAGE_PATH: str = "Mahjang.v1i.yolov8/test/LINE_ALBUM_麻雀2_250816_1.jpg"
OUTPUT_FOLDER: str = "output"

# モデルのクラス名を指定形式の文字列に変換するための対応表
TILE_NAME_MAP = {
    "1m": "1m", "2m": "2m", "3m": "3m", "4m": "4m", "5m": "5m",
    "5mr": "5mr", "6m": "6m", "7m": "7m", "8m": "8m", "9m": "9m",
    "1p": "1p", "2p": "2p", "3p": "3p", "4p": "4p", "5p": "5p",
    "5pr": "5pr", "6p": "6p", "7p": "7p", "8p": "8p", "9p": "9p",
    "1s": "1s", "2s": "2s", "3s": "3s", "4s": "4s", "5s": "5s",
    "5sr": "5sr", "6s": "6s", "7s": "7s", "8s": "8s", "9s": "9s",
    "1z": "1z", "2z": "2z", "3z": "3z", "4z": "4z", "5z": "5z",
    "6z": "6z", "7z": "7z",
}


class Meld:
    """鳴き面子（チー、ポン、カン）を表すクラス。（プレースホルダー）"""
    pass


class HandAnalysis:
    """手牌の構造を解析し、考えられる全ての面子・雀頭の組み合わせを導出する。

    Attributes:
        agari_combinations (list[dict]): 手牌の解釈パターンのリスト。
    """

    def __init__(self, hand: list[str], melds: list[Meld], agari_hai: str):
        """HandAnalysisオブジェクトを初期化する。"""
        self.agari_combinations: list[dict] = []
        self._analyze_hand(hand, melds, agari_hai)

    def _analyze_hand(self, hand: list[str], melds: list[Meld], agari_hai: str):
        """手牌解析のメインロジック。（現在はサンプルデータを返すモック実装）"""
        if len(hand) + (len(melds) * 3) == 14:
            normal_combination = {
                "type": "normal", "janto": ["1m", "1m"],
                "mentsu": [["2m", "3m", "4m"], ["6p", "7p", "8p"], ["3s", "4s", "5s"]],
                "machi": "ryanmen",
            }
            chitoi_combination = {
                "type": "chitoi", "janto": None,
                "mentsu": [
                    ["1m", "1m"], ["2p", "2p"], ["3s", "3s"], ["4m", "4m"],
                    ["5p", "5p"], ["6s", "6s"], ["7z", "7z"]
                ],
                "machi": "tanki",
            }
            self.agari_combinations = [normal_combination, chitoi_combination]


class NoTilesDetectedError(Exception):
    """画像は正常だが、信頼できる牌が一つも検出できなかった場合に送出される例外。"""
    pass


def detect_tiles_with_segmentation(
    model: YOLO, image_path: str, confidence_threshold: float
) -> tuple[list[tuple[str, float]], np.ndarray]:
    """画像から麻雀牌を検出し、セグメンテーションマスクを描画します。"""
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    np_array = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("画像データとして認識できません。")
    results = model(image, verbose=False)
    detected_tiles: list[tuple[str, float]] = []
    annotated_frame = results[0].plot()
    for box in results[0].boxes:
        conf = float(box.conf[0])
        if conf > confidence_threshold:
            class_id = int(box.cls[0])
            model_class_name = model.names[class_id]
            hand_tile_str = TILE_NAME_MAP.get(model_class_name, "unknown")
            detected_tiles.append((hand_tile_str, conf))
    if not detected_tiles:
        raise NoTilesDetectedError("牌を検出できませんでした。")
    return detected_tiles, annotated_frame


def process_single_image(model: YOLO, image_path: str) -> list[dict]:
    """指定された単一の画像に対し、牌検出とセグメンテーションを実行します。

    Args:
        model (YOLO): 読み込み済みのYOLOモデル。
        image_path (str): 処理対象の画像ファイルパス。

    Returns:
        list[dict]: 画像の解析結果 (agari_combinations) のリスト。
    """
    image_filename = os.path.basename(image_path)
    try:
        detected_tiles, annotated_img = detect_tiles_with_segmentation(
            model, image_path, CONFIDENCE_THRESHOLD
        )

        print(f"--- {image_filename} ---")
        print(f"検出した牌の数: {len(detected_tiles)}")
        print("検出結果（牌: 信頼度）:")
        for tile, conf in detected_tiles:
            print(f"  {tile}: {conf:.3f}")

        hand = [tile for tile, conf in detected_tiles]
        agari_hai = hand[-1] if hand else ""
        melds = []
        
        hand_analyzer = HandAnalysis(hand=hand, melds=melds, agari_hai=agari_hai)

        # 結果画像保存
        base_name = os.path.splitext(image_filename)[0]
        save_path = os.path.join(OUTPUT_FOLDER, f"{base_name}_segmented.jpg")
        cv2.imwrite(save_path, annotated_img)
        print(f"\n-> セグメンテーション結果画像を保存しました: {save_path}")

        return hand_analyzer.agari_combinations

    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません: {image_path}")
        return []
    except NoTilesDetectedError:
        print("-> 牌を検出できませんでした。")
        return []
    except Exception as e:
        print(f"-> 予期せぬエラーが発生しました: {e}")
        return []


if __name__ == "__main__":
    # 出力フォルダが存在しない場合は作成
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # YOLOモデルを読み込み
    print("YOLOモデルを読み込んでいます...")
    yolo_model = YOLO(MODEL_PATH)
    print("モデルの読み込み完了。")

    # 単一の画像を処理
    final_combinations = process_single_image(yolo_model, TARGET_IMAGE_PATH)

    # 最終的な解析結果をまとめて出力
    print("\n" + "="*50)
    print(f"<<< 最終解析結果: {os.path.basename(TARGET_IMAGE_PATH)} >>>")
    print("="*50)

    if final_combinations:
        pprint(final_combinations, indent=2)
    else:
        print("有効な和了形は検出されませんでした。")