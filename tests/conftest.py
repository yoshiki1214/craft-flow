"""
<<<<<<< HEAD
pytest設定ファイル

テスト用のフィクスチャを定義
"""
=======
pytestの設定ファイル

テスト用のフィクスチャを定義する。
"""

>>>>>>> main
import pytest
import os
import tempfile
from app import create_app, db
<<<<<<< HEAD
from app.models import ExperienceProgram, Reservation
=======
from app.models.pos_sales import PosSales
>>>>>>> main


@pytest.fixture
def app():
<<<<<<< HEAD
    """テスト用Flaskアプリケーションフィクスチャ"""
    # 一時ファイルを使用したテスト用データベース
    db_fd, db_path = tempfile.mkstemp()
    
    flask_app = create_app('development')
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    flask_app.config['WTF_CSRF_ENABLED'] = False  # テスト時のCSRFを無効化
    flask_app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'connect_args': {'check_same_thread': False},
        'pool_pre_ping': True
    }
    
    with flask_app.app_context():
        # テーブルを作成
        db.create_all()
        yield flask_app
        # テスト後にテーブルを削除
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)
=======
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
>>>>>>> main


@pytest.fixture
def client(app):
<<<<<<< HEAD
    """テスト用クライアントフィクスチャ"""
=======
    """
    テスト用のクライアントを作成する

    Args:
        app: テスト用のFlaskアプリケーション

    Yields:
        FlaskClient: テスト用のクライアント
    """
>>>>>>> main
    return app.test_client()


@pytest.fixture
def runner(app):
<<<<<<< HEAD
    """テスト用CLIランナーフィクスチャ"""
=======
    """
    テスト用のCLIランナーを作成する

    Args:
        app: テスト用のFlaskアプリケーション

    Yields:
        FlaskCliRunner: テスト用のCLIランナー
    """
>>>>>>> main
    return app.test_cli_runner()


@pytest.fixture
<<<<<<< HEAD
def sample_program(app):
    """サンプルの体験プログラムフィクスチャ"""
    with app.app_context():
        program = ExperienceProgram(
            name='テストプログラム',
            description='テスト用の体験プログラムです。',
            price=2000,
            capacity=15
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
                name='テストプログラム',
                description='テスト用の体験プログラムです。',
                price=2000,
                capacity=15
            )
            db.session.add(program)
            db.session.commit()
        
        reservation = Reservation(
            program_id=sample_program,
            name='山田 太郎',
            email='yamada@example.com',
            phone_number='090-1234-5678',
            reservation_date=date(2025, 12, 25),
            number_of_participants=2
        )
        db.session.add(reservation)
        db.session.commit()
        reservation_id = reservation.id
        db.session.expunge(reservation)
        return reservation_id
=======
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
>>>>>>> main
