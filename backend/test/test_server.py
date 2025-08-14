from flask import Flask, request, jsonify
from flask_cors import CORS

# Flaskアプリケーションのインスタンスを作成
app = Flask(__name__)

# CORS (Cross-Origin Resource Sharing) を有効にする
# これにより、Vueの開発サーバー(例: localhost:5173)から
# Flaskサーバー(例: localhost:5001)へのAPIリクエストが許可される
CORS(app) 

# '/api/calculate' というURLにPOSTリクエストが来たときに、この関数を実行する
@app.route('/api/calculate', methods=['POST'])
def handle_calculate():
    """
    フロントエンドから送信されたフォームデータとファイルを受け取り、
    その情報をJSON形式で返すテスト用の関数。
    """
    print("✅ Request received at /api/calculate")

    # 返信するデータを格納するための辞書を準備
    received_data = {}

    # 1. テキスト形式のフォームデータを取得
    # request.formには、'is_oya'や'bakaze'などのテキストデータが格納されている
    form_data = request.form.to_dict()
    received_data['form_data'] = form_data
    print("📄 Form data:", form_data)

    # 2. ファイルデータを取得
    # request.filesには、'image'キーで画像ファイルが格納されている
    if 'image' in request.files:
        image_file = request.files['image']
        
        # ファイルに関する情報を辞書に格納
        file_info = {
            'filename': image_file.filename,
            'content_type': image_file.content_type,
        }
        received_data['file_info'] = file_info
        print("🖼️ File info:", file_info)
    else:
        received_data['file_info'] = 'No file received'
        print("⚠️ No file part in the request")

    # 3. 受け取ったデータをJSON形式でフロントエンドに返す
    return jsonify(received_data)

# このファイルが直接実行された場合にサーバーを起動する
if __name__ == '__main__':
    # デバッグモードを有効にし、ポート5001でサーバーを実行
    # Vueの開発サーバーとポートが衝突しないように5001を指定
    app.run(debug=True, port=5001)