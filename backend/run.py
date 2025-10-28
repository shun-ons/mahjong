# backend/run.py
"""
Flaskアプリケーション全体を起動する実行ファイル。
"""

# --- モジュールのインポート ---
# 依存モジュールのインポート
from app import create_app


# アプリケーションインスタンスを作成
app = create_app()


if __name__ == '__main__':
    """
    アプリケーションの起動。
    このファイルが直接実行された場合に、サーバを起動する。
    """
    app.run(host='0.0.0.0', port=8000, debug=True)