"""
Flask Application Factory

Application Factoryパターンを使用してFlaskアプリケーションを生成
"""
import locale
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import config

# 拡張機能のインスタンス（アプリ外で初期化）
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config_name: str = 'default') -> Flask:
    """
    Flaskアプリケーションを作成するファクトリ関数
    
    Args:
        config_name: 設定名（デフォルト: 'default'）
    
    Returns:
        Flask: 設定済みのFlaskアプリケーションインスタンス
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 拡張機能の初期化
    db.init_app(app)
    migrate.init_app(app, db)
    # login_manager.init_app(app) # ユーザー管理実装時に有効化
    # login_manager.login_view = 'auth.login'  # ユーザー管理実装時に有効化
    
    # 循環インポートを避けるため、関数内でインポートします
    from . import models
    from .reservation import reservation_bp
    from . import commands

    # カスタムフィルターの登録
    @app.template_filter('comma')
    def format_comma(value):
        """数値を3桁区切りの文字列にフォーマットするフィルター"""
        locale.setlocale(locale.LC_ALL, '')
        return locale.format_string("%d", value, grouping=True)

    app.register_blueprint(reservation_bp)
    commands.init_app(app)

    return app
