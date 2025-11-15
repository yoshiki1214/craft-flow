"""Flaskアプリケーションの初期化"""
from flask import Flask
import os


def create_app(config_name='default'):
    """
    Application FactoryパターンでFlaskアプリケーションを作成
    
    Args:
        config_name: 設定名
        
    Returns:
        Flaskアプリケーションインスタンス
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # 基本設定
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['UPLOAD_FOLDER'] = os.path.join(app.instance_path, 'uploads')
    app.config['OUTPUT_FOLDER'] = os.path.join(app.instance_path, 'outputs')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB制限
    
    # instanceフォルダとサブフォルダの作成
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'])
    except OSError:
        pass
    
    try:
        os.makedirs(app.config['OUTPUT_FOLDER'])
    except OSError:
        pass
    
    # Blueprintの登録
    from app.routes import upload
    app.register_blueprint(upload.upload_bp)
    
    return app
