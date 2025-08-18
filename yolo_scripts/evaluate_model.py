"""
指定された学習済みYOLOv8モデルの評価を行い、
PrecisionとRecallを計算してテキストファイルに保存する。
"""

import os
from ultralytics import YOLO
from ultralytics.utils.metrics import DetMetrics

# --- 定数定義 ---
MODEL_PATH: str = '/home/hamuro/Search/mahjong/runs_200/detect/mahjong_train/weights/best.pt'
DATA_YAML_PATH: str = '/home/hamuro/Search/mahjong/Mahjang.v1i.yolov8/data.yaml'
OUTPUT_FILE_PATH: str = '/home/hamuro/Search/mahjong/runs_200/detect/eval_result.txt'


def main():
    """
    学習済みYOLOv8モデルを評価し、結果をファイルに出力する。

    MODEL_PATHで指定されたモデルを、DATA_YAML_PATHで指定されたデータセットで評価。
    計算されたPrecisionとRecallの全クラス平均値をテキストファイルに保存する。
    """
    print(f"モデルを読み込んでいます: {MODEL_PATH}")
    model: YOLO = YOLO(MODEL_PATH)

    print(f"データセットでモデルを評価中: {DATA_YAML_PATH}")
    # verbose=Falseで評価中の詳細なログ出力を抑制
    metrics: DetMetrics = model.val(data=DATA_YAML_PATH, verbose=False)

    # 全クラスの平均PrecisionとRecallを計算
    precision: float = metrics.box.p.mean()
    recall: float = metrics.box.r.mean()

    print(f"評価完了。 Precision: {precision:.4f}, Recall: {recall:.4f}")

    # ディレクトリが存在しない場合に備えて作成する
    output_dir = os.path.dirname(OUTPUT_FILE_PATH)
    os.makedirs(output_dir, exist_ok=True)

    # 結果をテキストファイルに保存
    with open(OUTPUT_FILE_PATH, 'w') as f:
        f.write(f"Precision: {precision:.4f}\n")
        f.write(f"Recall:    {recall:.4f}\n") # 表示を揃えるために空白を調整

    print(f"評価結果をテキストファイルに保存しました: {OUTPUT_FILE_PATH}")


if __name__ == '__main__':
    main()