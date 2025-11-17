"""
<<<<<<< HEAD
Flask Application Factory

Application Factoryパターンを使用してFlaskアプリケーションを生成
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os

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
    app = Flask(__name__, instance_relative_config=True)
    
    # 設定
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(app.instance_path, 'app.db')
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
=======
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

>>>>>>> 0ba6c74c70245a273989b3356430507d4923e121
    # instanceフォルダの作成
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
<<<<<<< HEAD
    
    # 拡張機能の初期化
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # ユーザー管理実装後に有効化
    
    # モデルのインポート（循環インポートを防ぐため、ここでインポート）
    from app.models import Program, Reservation
    
    # Blueprintの登録（今後実装）
    # from app.routes import main, reservations
    # app.register_blueprint(main.main_bp)
    # app.register_blueprint(reservations.reservations_bp, url_prefix='/reservations')
    
=======

    # 拡張機能の初期化
    db.init_app(app)
    migrate.init_app(app, db)

    # データベースモデルのインポート（循環インポートを避けるため）
    from app.models import pos_sales, daily_sales  # noqa: F401

>>>>>>> 0ba6c74c70245a273989b3356430507d4923e121
    return app
