"""
pytestの設定ファイル

テスト用のフィクスチャを定義する。
"""

import pytest
import os
import tempfile
from app import create_app, db
from app.models import ExperienceProgram, Reservation
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
def sample_program(app):
    """サンプルの体験プログラムフィクスチャ"""
    with app.app_context():
        program = ExperienceProgram(
            name="テストプログラム",
            description="テスト用の体験プログラムです。",
            price=2000,
            capacity=15,
        )
        db.session.add(program)
        db.session.commit()
        # IDを保存してから返す
        program_id = program.id
        # セッションをコミットしてexpireしないようにする
        db.session.expunge(program)
        return program_id


@pytest.fixture
def sample_reservation(app, sample_program):
    """サンプルの予約フィクスチャ"""
    with app.app_context():
        from datetime import date

        # program_idから新しいセッションで取得
        program = db.session.get(ExperienceProgram, sample_program)
        if not program:
            # プログラムが存在しない場合は作成
            program = ExperienceProgram(
                id=sample_program,
                name="テストプログラム",
                description="テスト用の体験プログラムです。",
                price=2000,
                capacity=15,
            )
            db.session.add(program)
            db.session.commit()

        reservation = Reservation(
            program_id=sample_program,
            name="山田 太郎",
            email="yamada@example.com",
            phone_number="090-1234-5678",
            reservation_date=date(2025, 12, 25),
            number_of_participants=2,
        )
        db.session.add(reservation)
        db.session.commit()
        reservation_id = reservation.id
        db.session.expunge(reservation)
        return reservation_id


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
