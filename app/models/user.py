"""
ユーザーデータモデル

アプリケーション利用者の情報を管理するテーブル。
ユーザー認証・認可の基盤として機能する。
"""

from datetime import datetime
from flask_login import UserMixin
from app import db


class User(UserMixin, db.Model):
    """
    ユーザーデータテーブル

    アプリケーション利用者の基本情報を保存する。
    Flask-Loginによる認証機能の基盤として使用される。

    Attributes:
        id: 主キー（自動採番）
        username: ユーザー名
        email: メールアドレス（一意制約）
        department: 所属
        hashed_password: ハッシュ化されたパスワード
        created_at: 登録日時（自動設定）
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False, comment="ユーザー名")
    email = db.Column(db.String(255), nullable=False, unique=True, comment="メールアドレス")
    department = db.Column(db.String(50), nullable=False, comment="所属")
    hashed_password = db.Column(db.String(255), nullable=False, comment="ハッシュ化されたパスワード")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, comment="登録日時")

    def __repr__(self) -> str:
        """オブジェクトの文字列表現を返す"""
        return f"<User {self.id}: {self.username} ({self.email})>"
