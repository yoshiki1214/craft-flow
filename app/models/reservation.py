"""
予約管理システムのデータベースモデル

体験プログラムと予約情報を管理するモデルを定義
"""
from datetime import datetime, date, time
from typing import Optional
from sqlalchemy import Index
from app import db


class Program(db.Model):
    """
    体験プログラムモデル
    
    体験プログラムの情報を管理するテーブル
    """
    __tablename__ = 'programs'
    
    # 主キー
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # プログラム基本情報
    name = db.Column(db.String(100), nullable=False, comment='プログラム名')
    description = db.Column(db.Text, nullable=True, comment='プログラム説明')
    duration = db.Column(db.Integer, nullable=False, comment='所要時間（分）')
    capacity = db.Column(db.Integer, nullable=False, default=1, comment='定員数')
    price = db.Column(db.Integer, nullable=False, default=0, comment='料金（円）')
    
    # ステータス管理
    is_active = db.Column(db.Boolean, nullable=False, default=True, comment='有効/無効フラグ')
    
    # タイムスタンプ
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='作成日時')
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新日時')
    
    # リレーション
    reservations = db.relationship('Reservation', backref='program', lazy=True, cascade='all, delete-orphan')
    
    # インデックス
    __table_args__ = (
        Index('idx_programs_is_active', 'is_active'),
    )
    
    def __repr__(self) -> str:
        return f'<Program {self.id}: {self.name}>'
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'duration': self.duration,
            'capacity': self.capacity,
            'price': self.price,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Reservation(db.Model):
    """
    予約モデル
    
    予約情報を管理するテーブル
    """
    __tablename__ = 'reservations'
    
    # 予約ステータス定数
    STATUS_PENDING = 'pending'  # 予約確定待ち
    STATUS_CONFIRMED = 'confirmed'  # 予約確定
    STATUS_CANCELLED = 'cancelled'  # キャンセル
    STATUS_COMPLETED = 'completed'  # 完了
    
    # 主キー
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # 外部キー
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False, comment='プログラムID')
    user_id = db.Column(db.Integer, nullable=True, comment='ユーザーID（ユーザーテーブル実装後に外部キー制約を追加）')
    
    # 予約情報
    reservation_date = db.Column(db.Date, nullable=False, comment='予約日')
    start_time = db.Column(db.Time, nullable=False, comment='開始時間')
    end_time = db.Column(db.Time, nullable=False, comment='終了時間')
    status = db.Column(db.String(20), nullable=False, default=STATUS_PENDING, comment='予約ステータス')
    
    # 予約者情報（ユーザーテーブル実装前の暫定対応）
    customer_name = db.Column(db.String(100), nullable=True, comment='予約者名')
    customer_email = db.Column(db.String(255), nullable=True, comment='予約者メールアドレス')
    customer_phone = db.Column(db.String(20), nullable=True, comment='予約者電話番号')
    
    # 備考
    notes = db.Column(db.Text, nullable=True, comment='備考')
    
    # タイムスタンプ
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment='作成日時')
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新日時')
    
    # インデックス（検索・ソート用）
    __table_args__ = (
        Index('idx_reservations_program_id', 'program_id'),
        Index('idx_reservations_user_id', 'user_id'),
        Index('idx_reservations_date', 'reservation_date'),
        Index('idx_reservations_status', 'status'),
        Index('idx_reservations_date_status', 'reservation_date', 'status'),
    )
    
    def __repr__(self) -> str:
        return f'<Reservation {self.id}: {self.reservation_date} {self.start_time}>'
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            'id': self.id,
            'program_id': self.program_id,
            'user_id': self.user_id,
            'reservation_date': self.reservation_date.isoformat() if self.reservation_date else None,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'status': self.status,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'customer_phone': self.customer_phone,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @property
    def is_cancelled(self) -> bool:
        """キャンセル済みかどうか"""
        return self.status == self.STATUS_CANCELLED
    
    @property
    def is_confirmed(self) -> bool:
        """確定済みかどうか"""
        return self.status == self.STATUS_CONFIRMED
    
    def cancel(self) -> None:
        """予約をキャンセル"""
        self.status = self.STATUS_CANCELLED
        self.updated_at = datetime.utcnow()
    
    def confirm(self) -> None:
        """予約を確定"""
        self.status = self.STATUS_CONFIRMED
        self.updated_at = datetime.utcnow()
