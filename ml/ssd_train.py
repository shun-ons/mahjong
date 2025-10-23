import torch
import os
import time
import uuid
import cv2
import numpy as np
from PIL import Image
from torch.utils.data import Dataset, DataLoader
import torchvision
from torchvision.models.detection.ssd import SSD300_VGG16_Weights
from torchmetrics.detection.mean_ap import MeanAveragePrecision
from torchvision.ops import box_iou ### 追加 ###

# --- データセットクラス ---
class YOLOv8Dataset(Dataset):
    def __init__(self, img_dir: str, label_dir: str, transform=None):
        self.img_dir = img_dir
        self.label_dir = label_dir
        self.transform = transform
        self.img_files = [f for f in os.listdir(img_dir) if f.endswith(('.jpg', '.png'))]
        self.classes = [
            '1m', '1p', '1s', '1z', '2m', '2p', '2s', '2z', '3m', '3p', '3s', '3z', 
            '4m', '4p', '4s', '4z', '5m', '5mr', '5p', '5pr', '5s', '5sr', '5z', '6m', '6p', '6s', '6z', 
            '7m', '7p', '7s', '7z', '8m', '8p', '8s', '9m', '9p', '9s'
        ]
    def __len__(self):
        return len(self.img_files)
    def __getitem__(self, idx: int):
        img_name = self.img_files[idx]
        img_path = os.path.join(self.img_dir, img_name)
        label_path = os.path.join(self.label_dir, os.path.splitext(img_name)[0] + '.txt')
        image = Image.open(img_path).convert("RGB")
        img_w, img_h = image.size
        boxes, labels = [], []
        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                for line in f:
                    class_id, x_center, y_center, width, height = map(float, line.strip().split())
                    x1 = (x_center - width / 2) * img_w
                    y1 = (y_center - height / 2) * img_h
                    x2 = (x_center + width / 2) * img_w
                    y2 = (y_center + height / 2) * img_h
                    boxes.append([x1, y1, x2, y2])
                    labels.append(int(class_id) + 1)
        target = {
            'boxes': torch.as_tensor(boxes, dtype=torch.float32),
            'labels': torch.as_tensor(labels, dtype=torch.int64)
        }
        if self.transform:
            image = self.transform(image)
        return image, target, img_path # ### 変更: 画像パスも返す ###

# --- 設定 ---
TRAIN_IMG_DIR = '../datasets/Mahjong.v2i.yolov8/train/images'
TRAIN_LABEL_DIR = '../datasets/Mahjong.v2i.yolov8/train/labels'
TEST_IMG_DIR = '../datasets/Mahjong.v2i.yolov8/test/images'
TEST_LABEL_DIR = '../datasets/Mahjong.v2i.yolov8/test/labels'
NUM_CLASSES = 37 + 1
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
BATCH_SIZE = 8 # 画像保存のためバッチサイズを少し小さく調整
NUM_EPOCHS = 100
LEARNING_RATE = 0.005
MODEL_SAVE_PATH = 'ssd_mahjong_model.pth'
RESULT_FILE_PATH = 'ssd_eval_result.txt'
### 追加: 結果画像保存用ディレクトリ ###
RESULT_IMAGE_DIR = 'results_ssd'

# --- 前処理とデータローダー ---
transforms = torchvision.transforms.Compose([torchvision.transforms.ToTensor()]) # リサイズは描画時に行う
test_transforms = torchvision.transforms.Compose([torchvision.transforms.ToTensor()])

# collate_fnを修正して画像パスを扱えるようにする
def collate_fn_with_path(batch):
    images, targets, paths = zip(*batch)
    return list(images), list(targets), list(paths)

train_dataset = YOLOv8Dataset(TRAIN_IMG_DIR, TRAIN_LABEL_DIR, transform=transforms)
test_dataset = YOLOv8Dataset(TEST_IMG_DIR, TEST_LABEL_DIR, transform=test_transforms)
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, collate_fn=lambda x: tuple(zip(*x)))
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False, collate_fn=collate_fn_with_path)

# --- モデル準備 ---
model = torchvision.models.detection.ssd300_vgg16(weights=SSD300_VGG16_Weights.DEFAULT)
in_channels = [512, 1024, 512, 256, 256, 256]
num_anchors = [4, 6, 6, 6, 4, 4]
model.head.classification_head = torchvision.models.detection.ssd.SSDClassificationHead(in_channels, num_anchors, NUM_CLASSES)
model.to(DEVICE)
optimizer = torch.optim.SGD(model.parameters(), lr=LEARNING_RATE, momentum=0.9, weight_decay=0.0005)

### 追加: 描画と正解判定のためのヘルパー関数 ###
def draw_boxes(image_np, gts, preds, class_names):
    """画像に正解(GT)と予測(Pred)のバウンディングボックスを描画する"""
    # 正解ボックスを緑で描画
    for box, label in zip(gts['boxes'], gts['labels']):
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(image_np, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image_np, f"GT: {class_names[label-1]}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # 予測ボックスを赤で描画 (信頼度0.5以上)
    for box, label, score in zip(preds['boxes'], preds['labels'], preds['scores']):
        if score > 0.5:
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(image_np, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(image_np, f"Pred: {class_names[label-1]} ({score:.2f})", (x1, y1 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    return image_np

def is_prediction_correct(gt_boxes, pred_boxes, iou_threshold=0.5):
    """予測が正解に近いか簡易的に判定する"""
    if len(pred_boxes) == 0 and len(gt_boxes) > 0:
        return False
    if len(pred_boxes) > 0 and len(gt_boxes) == 0:
        return False
    if len(pred_boxes) == 0 and len(gt_boxes) == 0:
        return True

    # 予測と正解のIoUを計算
    iou = box_iou(gt_boxes, pred_boxes)
    # 各正解ボックスに対して、IoUが閾値を超える予測ボックスが1つでもあればマッチしたと見なす
    matches = iou.max(dim=1).values > iou_threshold
    return matches.all()

# --- 学習ループ ---
print(f"デバイス: {DEVICE} を使用して学習を開始します。")
for epoch in range(NUM_EPOCHS):
    model.train()
    total_train_loss = 0.0
    for images, targets in train_loader:
        images = list(image.to(DEVICE) for image in images)
        targets = [{k: v.to(DEVICE) for k, v in t.items()} for t in targets]
        loss_dict = model(images, targets)
        losses = sum(loss for loss in loss_dict.values())
        optimizer.zero_grad()
        losses.backward()
        optimizer.step()
        total_train_loss += losses.item()
    avg_train_loss = total_train_loss / len(train_loader)
    print(f"Epoch [{epoch+1}/{NUM_EPOCHS}], Loss: {avg_train_loss:.4f}")

# --- 学習完了後 ---
print("\n学習完了。")
torch.save(model.state_dict(), MODEL_SAVE_PATH)
print(f"モデルを {MODEL_SAVE_PATH} に保存しました。")

# --- 最終評価と画像保存  ---
print("\n最終評価と結果画像の保存を開始します...")
model.eval()
metric = MeanAveragePrecision()
correct_dir = os.path.join(RESULT_IMAGE_DIR, 'correct')
incorrect_dir = os.path.join(RESULT_IMAGE_DIR, 'incorrect')
os.makedirs(correct_dir, exist_ok=True)
os.makedirs(incorrect_dir, exist_ok=True)

with torch.no_grad():
    for images, targets, paths in test_loader:
        images_on_device = list(image.to(DEVICE) for image in images)
        targets_on_device = [{k: v.to(DEVICE) for k, v in t.items()} for t in targets]
        predictions = model(images_on_device)
        
        # mAP計算のために更新
        metric.update(predictions, targets_on_device)

        # 各画像の描画と保存
        for i in range(len(images)):
            original_image = cv2.imread(paths[i])
            gts = targets[i]
            preds = predictions[i]
            
            # 正解判定
            is_correct = is_prediction_correct(gts['boxes'], preds['boxes'][preds['scores'] > 0.5])
            
            # 描画
            drawn_image = draw_boxes(original_image.copy(), gts, preds, test_dataset.classes)
            
            # 保存
            filename = os.path.basename(paths[i])
            if is_correct:
                save_path = os.path.join(correct_dir, filename)
            else:
                save_path = os.path.join(incorrect_dir, filename)
            cv2.imwrite(save_path, drawn_image)

final_results = metric.compute()
print("評価完了。")

# 最終評価結果をファイルに保存
print(f"評価結果を {RESULT_FILE_PATH} に保存します。")
with open(RESULT_FILE_PATH, 'w') as f:
    f.write(f"SSD Model Final Evaluation Results\n")
    f.write("-" * 50 + "\n")
    for key, val in final_results.items():
        if isinstance(val, torch.Tensor):
            f.write(f"{key}: {val.item():.4f}\n")
    f.write("-" * 50 + "\n")
    f.write(f"Result images are saved in '{RESULT_IMAGE_DIR}/' directory.\n")

print("全て完了しました。")