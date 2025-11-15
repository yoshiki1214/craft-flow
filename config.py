"""
アプリケーション設定モジュール
"""

import os
from pathlib import Path

# ベースディレクトリ
basedir = Path(__file__).parent.absolute()


class Config:
    """基本設定クラス"""

    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or f'sqlite:///{basedir / "instance" / "app.db"}'


class DevelopmentConfig(Config):
    """開発環境設定"""

    DEBUG = True


class ProductionConfig(Config):
    """本番環境設定"""

    DEBUG = False


config = {"development": DevelopmentConfig, "production": ProductionConfig, "default": DevelopmentConfig}
