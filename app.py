"""
Flaskアプリケーションのエントリーポイント
"""

import sys
import logging

from app import create_app

# ログ設定: 標準出力に確実に出力されるようにする
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", stream=sys.stdout
)

app = create_app()

if __name__ == "__main__":
    # 標準出力のバッファリングを無効化（Windows環境で確実に表示されるように）
    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", line_buffering=True)

    app.run(debug=True)
