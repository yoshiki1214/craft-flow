# -*- coding: utf-8 -*-
"""
委託販売精算書生成アプリケーションのメインファイル（旧バージョン）

このファイルは後方互換性のために残されていますが、
現在は app/__init__.py と app/features/ ディレクトリで機能を分割管理しています。

精算書関連機能は app/features/settlement.py に移動しました。
"""

import sys
import logging
import os
from app import create_app

# ログ設定: 標準出力に確実に出力されるようにする
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)

# 環境変数から設定名を取得
# FLASK_CONFIG環境変数が設定されていない場合は'default'（開発環境）を使用
config_name = os.environ.get("FLASK_CONFIG", "default")
app = create_app()


# --- アプリケーションの実行 ---

# このファイルが `python app.py` のように直接実行された場合にのみ、以下のコードが実行される
if __name__ == "__main__":
    """
    開発用Webサーバーを起動します。
    """
    # Flaskに組み込まれている開発用サーバーを起動
    # debug=True: デバッグモードを有効にする。
    #   - コードを変更するとサーバーが自動で再起動する
    #   - エラーが発生した際に、ブラウザ上で詳細なエラー情報を確認できる
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"

    # 標準出力のバッファリングを無効化（Windows環境で確実に表示されるように）
    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", line_buffering=True
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, encoding="utf-8", line_buffering=True
        )

    app.run(debug=debug, host="127.0.0.1", port=5000)
