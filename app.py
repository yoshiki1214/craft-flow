"""
Flaskアプリケーションのエントリーポイント
"""

from app import create_app
import os

# 環境変数から設定名を取得
# FLASK_CONFIG環境変数が設定されていない場合は'default'（開発環境）を使用
config_name = os.environ.get("FLASK_CONFIG", "default")
app = create_app()

if __name__ == "__main__":
    # 開発環境でのみ使用
    # 本番環境ではWSGIサーバー（Gunicorn等）を使用すること
    import os
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug, host="127.0.0.1", port=5000)
