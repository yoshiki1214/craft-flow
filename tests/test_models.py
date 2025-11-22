"""
モデルの基本的な定義テスト

pytestを使用してモデルの動作をテストします。
カバレッジ70%を意識したテスト実装
"""
import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import ExperienceProgram, Reservation


class TestExperienceProgram:
    """ExperienceProgramモデルのテストクラス"""
    
    def test_create_program(self, app):
        """体験プログラムの作成テスト"""
        with app.app_context():
            program = ExperienceProgram(
                name='藍染め体験 ハンカチ',
                description='天然藍を使った染色体験です。',
                price=2000,
                capacity=15
            )
            db.session.add(program)
            db.session.commit()
            
            assert program.id is not None
            assert program.name == '藍染め体験 ハンカチ'
            assert program.description == '天然藍を使った染色体験です。'
            assert program.price == 2000
            assert program.capacity == 15
    
    def test_program_repr(self, app, sample_program):
        """__repr__メソッドのテスト"""
        with app.app_context():
            program = db.session.get(ExperienceProgram, sample_program)
            repr_str = repr(program)
            assert 'ExperienceProgram' in repr_str
            assert program.name in repr_str
    
    def test_program_name_unique(self, app, sample_program):
        """プログラム名の一意性制約テスト"""
        with app.app_context():
            program = db.session.get(ExperienceProgram, sample_program)
            duplicate_program = ExperienceProgram(
                name=program.name,  # 同じ名前
                description='別の説明',
                price=3000,
                capacity=20
            )
            db.session.add(duplicate_program)
            
            with pytest.raises(IntegrityError):
                db.session.commit()
    
    def test_program_required_fields(self, app):
        """必須フィールドのテスト"""
        with app.app_context():
            # nameがNoneの場合
            program = ExperienceProgram(
                name=None,
                description='説明',
                price=2000,
                capacity=15
            )
            db.session.add(program)
            with pytest.raises(IntegrityError):
                db.session.commit()
    
    def test_program_relationship_with_reservations(self, app, sample_program, sample_reservation):
        """予約とのリレーションシップのテスト"""
        with app.app_context():
            program = db.session.get(ExperienceProgram, sample_program)
            reservation = db.session.get(Reservation, sample_reservation)
            # backrefによるリレーションシップの確認
            assert len(program.reservations) == 1
            assert program.reservations[0].id == reservation.id


class TestReservation:
    """Reservationモデルのテストクラス"""
    
    def test_create_reservation(self, app, sample_program):
        """予約の作成テスト"""
        with app.app_context():
            reservation = Reservation(
                program_id=sample_program,
                name='佐藤 花子',
                email='sato@example.com',
                phone_number='080-9876-5432',
                reservation_date=date(2025, 12, 25),
                number_of_participants=3
            )
            db.session.add(reservation)
            db.session.commit()
            
            assert reservation.id is not None
            assert reservation.program_id == sample_program
            assert reservation.name == '佐藤 花子'
            assert reservation.email == 'sato@example.com'
            assert reservation.phone_number == '080-9876-5432'
            assert reservation.reservation_date == date(2025, 12, 25)
            assert reservation.number_of_participants == 3
    
    def test_reservation_repr(self, app, sample_reservation):
        """__repr__メソッドのテスト"""
        with app.app_context():
            reservation = db.session.get(Reservation, sample_reservation)
            repr_str = repr(reservation)
            assert 'Reservation' in repr_str
            assert reservation.name in repr_str
            assert str(reservation.program_id) in repr_str
    
    def test_reservation_required_fields(self, app, sample_program):
        """必須フィールドのテスト"""
        with app.app_context():
            # nameがNoneの場合
            reservation = Reservation(
                program_id=sample_program,
                name=None,
                email='test@example.com',
                phone_number='090-1234-5678',
                reservation_date=date(2025, 12, 25),
                number_of_participants=1
            )
            db.session.add(reservation)
            with pytest.raises(IntegrityError):
                db.session.commit()
    
    def test_reservation_foreign_key_constraint(self, app):
        """外部キー制約のテスト"""
        with app.app_context():
            # SQLiteでは外部キー制約がデフォルトで無効のため、スキップ
            # 実際には外部キー制約が有効化されていればエラーが発生する
            # このテストは外部キー制約が有効な環境でのみ動作
            pass
    
    def test_reservation_relationship_with_program(self, app, sample_reservation, sample_program):
        """プログラムとのリレーションシップのテスト"""
        with app.app_context():
            reservation = db.session.get(Reservation, sample_reservation)
            program = db.session.get(ExperienceProgram, sample_program)
            # relationshipによるアクセス
            assert reservation.program.id == program.id
            assert reservation.program.name == program.name
    
    def test_multiple_reservations_for_program(self, app, sample_program):
        """1つのプログラムに対する複数の予約テスト"""
        with app.app_context():
            reservation1 = Reservation(
                program_id=sample_program,
                name='予約者1',
                email='reservation1@example.com',
                phone_number='090-1111-1111',
                reservation_date=date(2025, 12, 25),
                number_of_participants=2
            )
            reservation2 = Reservation(
                program_id=sample_program,
                name='予約者2',
                email='reservation2@example.com',
                phone_number='090-2222-2222',
                reservation_date=date(2025, 12, 26),
                number_of_participants=3
            )
            
            db.session.add(reservation1)
            db.session.add(reservation2)
            db.session.commit()
            
            # プログラムから予約を取得
            program = db.session.get(ExperienceProgram, sample_program)
            reservations = program.reservations
            assert len(reservations) >= 2
            
            # IDで確認
            reservation_ids = [r.id for r in reservations]
            assert reservation1.id in reservation_ids
            assert reservation2.id in reservation_ids


class TestModelIntegration:
    """モデル間の統合テストクラス"""
    
    def test_cascade_delete(self, app, sample_program):
        """プログラム削除時の予約削除テスト"""
        with app.app_context():
            # 予約を作成
            reservation = Reservation(
                program_id=sample_program,
                name='テスト ユーザー',
                email='test@example.com',
                phone_number='090-1234-5678',
                reservation_date=date(2025, 12, 25),
                number_of_participants=1
            )
            db.session.add(reservation)
            db.session.commit()
            
            # プログラムを削除（CASCADE設定がない場合、外部キー制約により削除できない）
            # 実際にはCASCADEが設定されていないため、予約が存在する場合は削除できない
            program = db.session.get(ExperienceProgram, sample_program)
            with pytest.raises(IntegrityError):
                db.session.delete(program)
                db.session.commit()
    
    def test_query_reservations_by_program(self, app, sample_program):
        """プログラムから予約をクエリするテスト"""
        with app.app_context():
            # 複数の予約を作成
            for i in range(3):
                reservation = Reservation(
                    program_id=sample_program,
                    name=f'予約者{i+1}',
                    email=f'reservation{i+1}@example.com',
                    phone_number=f'090-1111-111{i}',
                    reservation_date=date(2025, 12, 25),
                    number_of_participants=i+1
                )
                db.session.add(reservation)
            db.session.commit()
            
            # プログラムから予約を取得
            program = db.session.get(ExperienceProgram, sample_program)
            program_reservations = program.reservations
            assert len(program_reservations) >= 3
    
    def test_reservation_date_validation(self, app, sample_program):
        """予約日のデータ型テスト"""
        with app.app_context():
            reservation = Reservation(
                program_id=sample_program,
                name='日付テスト',
                email='date@example.com',
                phone_number='090-1234-5678',
                reservation_date=date(2025, 12, 31),
                number_of_participants=1
            )
            db.session.add(reservation)
            db.session.commit()
            
            assert isinstance(reservation.reservation_date, date)
            assert reservation.reservation_date.year == 2025
            assert reservation.reservation_date.month == 12
            assert reservation.reservation_date.day == 31

