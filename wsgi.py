"""
Flaskアプリケーションのエントリーポイント
"""

import logging
import os
import sys

# Pythonの検索パスにプロジェクトルートを追加
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from app import create_app, db

# Windows環境での標準出力バッファリング無効化
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", line_buffering=True)

# ログ設定
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

app = create_app(os.getenv("FLASK_CONFIG") or "default")

@app.shell_context_processor
def make_shell_context():
    """Flaskシェルコンテキストにオブジェクトを追加します。"""
    # 循環インポートを避けるため、ここでモデルをインポートします
    from app.models import ExperienceProgram, Reservation
    return dict(db=db, ExperienceProgram=ExperienceProgram, Reservation=Reservation)


if __name__ == "__main__":
    app.run()
