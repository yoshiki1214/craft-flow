"""
Flaskアプリケーション初期化モジュール

Application Factoryパターンを使用してFlaskアプリケーションを作成します。
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from typing import Optional

# データベースとマイグレーションのインスタンスを作成
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name: Optional[str] = None) -> Flask:
    """
    Flaskアプリケーションを作成する（Application Factoryパターン）
    
    Args:
        config_name: 設定名（未使用、将来の拡張用）
    
    Returns:
        Flask: 設定済みのFlaskアプリケーションインスタンス
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # 設定
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(app.instance_path, 'app.db')
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB
    
    # instanceフォルダの作成
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # 拡張機能の初期化
    db.init_app(app)
    migrate.init_app(app, db)
    
    # モデルのインポート（循環参照を避けるため）
    from app import models
    
    # Blueprintの登録
    from app.routes import upload
    app.register_blueprint(upload.upload_bp)
    
    # ルートパスのリダイレクト
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('upload.index'))
    
    return app

