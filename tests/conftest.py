"""
pytest設定ファイル

テスト用のフィクスチャを定義
"""
import pytest
import os
import tempfile
from app import create_app, db
from app.models import ExperienceProgram, Reservation


@pytest.fixture
def app():
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


@pytest.fixture
def client(app):
    """テスト用クライアントフィクスチャ"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """テスト用CLIランナーフィクスチャ"""
    return app.test_cli_runner()


@pytest.fixture
def sample_program(app):
    """サンプルの体験プログラムフィクスチャ"""
    with app.app_context():
        # 既存のプログラムを削除してから作成（重複を避ける）
        ExperienceProgram.query.delete()
        db.session.commit()
        
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

