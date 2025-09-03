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
from glob import glob

# --- 定数定義 ---
MODEL_PATH: str = "/home/hamuro/Search/mahjong/runs/detect/mahjong_train/weights/best.pt"
CONFIDENCE_THRESHOLD: float = 0.5
MODE=1#1なら単一画像、2ならフォルダ内の画像に対して検出
# ↓↓↓ 処理したい単一の画像ファイルのパスを指定してください ↓↓↓
TARGET_IMAGE_PATH: str = "/home/hamuro/Search/mahjong/Mahjang.v2i.yolov8/test/images/test_250825_3_jpg.rf.0e86e7efdd4d8c3c3a27301939a00b84.jpg"
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


def process_single_image(
    model: YOLO,
    image_path: str,
    return_with_conf: bool = False
) -> list:
    """指定された単一の画像に対し、牌検出とセグメンテーションを実行します。

    Args:
        model (YOLO): 読み込み済みのYOLOモデル。
        image_path (str): 処理対象の画像ファイルパス。
        return_with_conf (bool): Trueなら (牌, 信頼度) のリストを返す。
                                 Falseなら 牌だけのリストを返す。

    Returns:
        list: 検出された牌のリスト（文字列 or (文字列, 信頼度) のタプル）。
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

        # hand（牌だけのリスト）
        hand = [tile for tile, conf in detected_tiles]

        # 解析は残す（必要なら利用可能）
        agari_hai = hand[-1] if hand else ""
        melds = []
        _ = HandAnalysis(hand=hand, melds=melds, agari_hai=agari_hai)

        # 結果画像保存
        base_name = os.path.splitext(image_filename)[0]
        save_path = os.path.join(OUTPUT_FOLDER, f"{base_name}_segmented.jpg")
        cv2.imwrite(save_path, annotated_img)
        print(f"\n-> セグメンテーション結果画像を保存しました: {save_path}")

        # 戻り値（リストのみ）
        return detected_tiles if return_with_conf else hand

    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません: {image_path}")
        return []
    except NoTilesDetectedError:
        print("-> 牌を検出できませんでした。")
        return []
    except Exception as e:
        print(f"-> 予期せぬエラーが発生しました: {e}")
        return []

def process_folder(
    model: YOLO,
    folder_path: str,
    return_with_conf: bool = False
) -> dict:
    """指定フォルダ内の全画像を処理し、結果をまとめて返す。

    Args:
        model (YOLO): 読み込み済みのYOLOモデル。
        folder_path (str): 処理対象のフォルダパス。
        return_with_conf (bool): Trueなら (牌, 信頼度) のリストを返す。
                                 Falseなら 牌だけのリストを返す。

    Returns:
        dict: {画像ファイル名: 検出された牌リスト}
    """
    image_extensions = ("*.jpg", "*.jpeg", "*.png", "*.bmp")
    image_files = []
    for ext in image_extensions:
        image_files.extend(glob(os.path.join(folder_path, ext)))

    if not image_files:
        print(f"指定フォルダに画像が見つかりません: {folder_path}")
        return {}

    results = {}
    for img_path in sorted(image_files):
        print("\n" + "=" * 60)
        print(f"処理中: {os.path.basename(img_path)}")
        print("=" * 60)

        tiles = process_single_image(model, img_path, return_with_conf=return_with_conf)
        results[os.path.basename(img_path)] = tiles

    return results


if __name__ == "__main__":
    mode=MODE
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    print("YOLOモデルを読み込んでいます...")
    yolo_model = YOLO(MODEL_PATH)
    print("モデルの読み込み完了。")

    # 単一画像の場合
    if mode==1:
        hand_only = process_single_image(yolo_model, TARGET_IMAGE_PATH, return_with_conf=False)
        print("\n=== 単一画像の検出結果 ===")
        pprint(hand_only, indent=2)

    # フォルダ内すべての画像を処理
    if mode==2:
        target_folder = "/home/hamuro/Search/mahjong/Mahjang.v2i.yolov8/test/images"
        all_results = process_folder(yolo_model, target_folder, return_with_conf=False)

    print("\n" + "=" * 60)
    print(f"<<< フォルダ内の全検出結果: {target_folder} >>>")
    print("=" * 60)
    pprint(all_results, indent=2)
