"""
牌認識サービスモジュール。

このモジュールは、Webルートと機械学習の中核的な認識ロジックとの間の
中間的な役割を果たします。YOLOモデルの呼び出し、その出力の処理、
および特定のエラーのハンドリングを担当します。
"""
import sys
import os
from typing import List

# プロジェクトのルートディレクトリをPythonのパスに追加します。
# これにより、'ml'のような他のトップレベルディレクトリからモジュールをインポートできます。
# パスは、このファイルのディレクトリから3レベル上がることで構築されます
# (services -> app -> backend -> プロジェクトルート).
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    # パスが設定されたので、'ml'モジュールからインポートできます。
    # 'recognition.py'には'analyze_hand_from_image'のような関数があると仮定します。
    from ml.recognition import analyze_hand_from_image
except ImportError as e:
    raise ImportError(
        "'ml.recognition'からのインポートに失敗しました。"
        "ファイルが存在し、プロジェクト構造が正しいことを確認してください。"
    ) from e

# --- カスタム例外クラス ---

class NoTilesDetectedError(Exception):
    """画像内で牌が検出されなかった場合に発生するカスタム例外。"""
    pass


# --- サービス関数 ---

def detect_tiles(image_data: bytes) -> List[str]:
    """
    画像データを受け取り、認識モデルを呼び出し、検出された牌を返します。

    この関数は、牌認識サービスのメインエントリーポイントとして機能します。

    Args:
        image_data: 生の画像ファイルの内容（バイト列）。

    Returns:
        検出された牌の表記を表す文字列のリスト
        (例: ['1m', '2p', '7s', ...])。

    Raises:
        NoTilesDetectedError: 認識モデルが牌を検出しなかった場合。
        FileNotFoundError: 指定されたYOLOモデルファイルが見つからない場合。
        ValueError: 画像データが破損しているか、サポートされていない形式の場合に
                    認識モジュールから発生する可能性があります。
    """
    # プロジェクトルートからの相対パスとして、学習済みモデルファイルへのパスを定義します。
    model_path = os.path.join(
        PROJECT_ROOT, 'runs', 'detect', 'mahjong_train_v3', 'weights', 'best.pt'
    )

    if not os.path.exists(model_path):
        # もし指定された学習済みモデルが見つからない場合、代替を用意することが望ましいです。
        # ここでは、代替としてベースモデルを試します。
        fallback_path = os.path.join(PROJECT_ROOT, 'yolov8m.pt')
        if os.path.exists(fallback_path):
            print(f"警告: 学習済みモデルが {model_path} に見つかりません。{fallback_path} を使用します。")
            model_path = fallback_path
        else:
            raise FileNotFoundError(
                f"学習済みYOLOモデルが {model_path} に、代替モデルも {fallback_path} に見つかりませんでした。"
            )

    try:
        # mlモジュールから中核となる認識関数を呼び出します。
        print(f"認識モデルを使用中: {model_path}")
        detected_tiles = analyze_hand_from_image(image_data, model_path)

        # モデルからの結果を検証します。
        if not detected_tiles:
            # リストが空の場合、信頼できる牌が一つも識別されなかったことを意味します。
            raise NoTilesDetectedError(
                "画像から牌を検出できませんでした。画像の角度や明るさを変えて再度お試しください。"
            )

        return detected_tiles

    except Exception as e:
        # 分析中に他の予期せぬエラーが発生した場合は、それを再送出します。
        # これにより、ルート(routes.py)がエラーを捕捉し、一般的なサーバーエラーを返すことができます。
        print(f"認識サービスで予期せぬエラーが発生しました: {e}")
        raise

