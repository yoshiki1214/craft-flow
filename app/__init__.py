"""
Flaskアプリケーションの初期化モジュール

Application Factoryパターンを使用してFlaskアプリケーションを作成する。
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from config import config  # config.pyから設定辞書をインポート

# 拡張機能のインスタンスを作成（アプリケーションコンテキスト外で使用可能にするため）
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name: str = "default") -> Flask:
    """
    Flaskアプリケーションを作成する（Application Factoryパターン）

    Args:
        config_name: 設定名（'development', 'production', 'default'）
                    'default'は開発環境設定（DevelopmentConfig）を指す

    Returns:
        Flask: 初期化されたFlaskアプリケーションインスタンス
    """
    app = Flask(__name__, instance_relative_config=True)

    # config.pyから設定を読み込む
    app.config.from_object(config[config_name])

    # instanceフォルダの作成
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 拡張機能の初期化
    db.init_app(app)
    migrate.init_app(app, db)

    # データベースモデルのインポート（循環インポートを避けるため）
    from app.models import pos_sales, daily_sales  # noqa: F401

    # 機能Blueprintの登録
    from app.features import register_features

    register_features(app)

    return app
