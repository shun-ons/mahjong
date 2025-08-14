# backend/app/__init__.py
"""
Flaskアプリケーション本体を作成する。
またapiオブジェクトをアプリケーションに登録する。
"""


# --- モジュールのインポート ---
# 標準モジュールのインポート
from flask import Flask

# 依存モジュールのインポート
from .routes import api


def create_app():
    """
    Flaskアプリケーションのインスタンスを作成し、設定を行う。

    Returns:
        Flaskアプリケーションのインスタンス
    """
    
    # Flaskアプリケーションのインスタンスを作成
    app = Flask(__name__)

    # --- Blueprintの登録 ---
    app.register_blueprint(api, url_prefix='/api')

    return app