"""
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
    
    # instanceフォルダの作成
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
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
    
    return app
