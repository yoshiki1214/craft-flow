"""
Flaskアプリケーションの初期化モジュール

Application Factoryパターンを使用してFlaskアプリケーションを作成する。
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os
from config import config  # config.pyから設定辞書をインポート

# 拡張機能のインスタンスを作成（アプリケーションコンテキスト外で使用可能にするため）
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()


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
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    app.config["UPLOAD_FOLDER"] = os.path.join(app.instance_path, "uploads")
    app.config["OUTPUT_FOLDER"] = os.path.join(app.instance_path, "outputs")
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB制限

    # instanceフォルダの作成

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    try:
        os.makedirs(app.config["UPLOAD_FOLDER"])
    except OSError:
        pass

    try:
        os.makedirs(app.config["OUTPUT_FOLDER"])
    except OSError:
        pass

    # Blueprintの登録
    from app.routes import upload

    app.register_blueprint(upload.upload_bp)

    # 拡張機能の初期化
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "ログインが必要です。"
    login_manager.login_message_category = "info"
    csrf.init_app(app)

    # ユーザーローダーの設定
    @login_manager.user_loader
    def load_user(user_id: str):
        """ユーザーIDからユーザーオブジェクトを取得する"""
        from app.models import User

        return User.query.get(int(user_id))

    # データベースモデルのインポート（循環インポートを避けるため）
    from app.models import pos_sales, daily_sales, user, settlement_history  # noqa: F401

    # 機能Blueprintの登録
    from app.features import register_features

    register_features(app)

    return app
