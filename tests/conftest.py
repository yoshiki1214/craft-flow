"""
pytestの設定ファイル

テスト用のフィクスチャを定義する。
"""

import pytest
import os
import tempfile
from app import create_app, db
from app.models.pos_sales import PosSales


@pytest.fixture
def app():
    """
    テスト用のFlaskアプリケーションを作成する

    Yields:
        Flask: テスト用のFlaskアプリケーションインスタンス
    """
    # 一時的なデータベースファイルを作成
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

    app = create_app("testing")
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        # データベース接続を明示的に閉じる
        db.engine.dispose()

    os.close(db_fd)
    # Windows環境でのファイル削除エラーを回避
    try:
        os.unlink(db_path)
    except (PermissionError, FileNotFoundError):
        # ファイルが既に削除されているか、アクセスできない場合は無視
        pass


@pytest.fixture
def client(app):
    """
    テスト用のクライアントを作成する

    Args:
        app: テスト用のFlaskアプリケーション

    Yields:
        FlaskClient: テスト用のクライアント
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    テスト用のCLIランナーを作成する

    Args:
        app: テスト用のFlaskアプリケーション

    Yields:
        FlaskCliRunner: テスト用のCLIランナー
    """
    return app.test_cli_runner()


@pytest.fixture
def sample_pos_data():
    """
    サンプルのPOSデータを返す

    Returns:
        dict: サンプルのPOSデータ
    """
    return {
        "pos_number": "POS1",
        "sale_date": "2025-11-05",
        "reported_at": "2025-11-06 17:30:00",
        "product_code": "PROD001",
        "product_name": "テスト商品",
        "quantity": 2,
        "unit_price": 1000,
        "subtotal": 2000,
        "total_amount": 2000,
        "pdf_source_file": "test.pdf",
    }
