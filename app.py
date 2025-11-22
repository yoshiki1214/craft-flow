"""
Flaskアプリケーションのエントリーポイント
"""

import sys
import logging

from app import create_app
import os


# ログ設定: 標準出力に確実に出力されるようにする
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", stream=sys.stdout
)
# 環境変数から設定名を取得
# FLASK_CONFIG環境変数が設定されていない場合は'default'（開発環境）を使用
config_name = os.environ.get("FLASK_CONFIG", "default")
app = create_app()

if __name__ == "__main__":
    # 開発環境でのみ使用
    # 本番環境ではWSGIサーバー（Gunicorn等）を使用すること
    import os

    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"

    # 標準出力のバッファリングを無効化（Windows環境で確実に表示されるように）
    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", line_buffering=True)

    app.run(debug=debug, host="127.0.0.1", port=5000)
