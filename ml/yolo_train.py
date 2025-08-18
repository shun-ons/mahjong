from ultralytics import YOLO

# 学習済みのベースモデル（例えばYOLOv8nやYOLOv8sなど）を指定
# 0から学習したい場合は'yolov8n.pt'などから始めるのが一般的
base_model = 'yolov8m.pt'

# データセットのyamlファイルパス（クラス数・画像パスなどを定義したもの）
data_yaml = '/home/hamuro/Search/mahjong/Mahjang.v1i.yolov8/data.yaml'  # あなたのyamlファイル名に置き換えてください

# 学習用YOLOモデルを読み込み
model = YOLO(base_model)

# 学習実行
model.train(
    data=data_yaml,          # データセット設定ファイル
    epochs=300,               # 学習エポック数
    batch=16,                # バッチサイズ
    imgsz=640,               # 画像サイズ（推奨640）
    name='mahjong_train',    # 保存フォルダ名（runs/train/mahjong_train）
    device=0                 # GPU番号（CPUのみなら'cpu'）
)
